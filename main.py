from PIL import Image
from io import BytesIO
import os
import json
import time
import logging
import datetime
import colorlog
from typing import Tuple, List, Dict
from dataclasses import dataclass
from functools import wraps
from dotenv import load_dotenv
from src.utils.captcha_ocr import get_ocr_res
from src.core.course_selector import get_jx0502zbid
from src.core.search_and_select_course import search_and_select_course
from src.utils.session_manager import init_session, get_session

# 常量配置
BASE_URL = "http://zhjw.qfnu.edu.cn"
URLS = {
    "rand_code": f"{BASE_URL}/verifycode.servlet",
    "login": f"{BASE_URL}/Logon.do?method=logonLdap",
    "init_data": f"{BASE_URL}/Logon.do?method=logon&flag=sess",
    "main_page": f"{BASE_URL}/jsxsd/framework/xsMain.jsp",
    "course_selection": f"{BASE_URL}/jsxsd/xsxk/xklc_list",
}

RETRY_ATTEMPTS = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 10


@dataclass
class CourseConfig:
    course_id_or_name: str
    teacher_name: str
    week_day: str = ""
    class_period: str = ""
    week_type: str = ""
    jx02id: str = ""
    jx0404id: str = ""


@dataclass
class UserConfig:
    user_account: str
    user_password: str
    select_semester: str
    mode: str = "fast"
    courses: List[CourseConfig] = None


def setup_logger() -> logging.Logger:
    """配置日志系统"""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger = colorlog.getLogger()
    logger.setLevel(logging.DEBUG)

    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 配置文件处理器
    filename = f"logs/app_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(filename, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    # 控制台处理器
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s: %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logger()
load_dotenv()


def retry(exceptions=Exception, attempts=3, delay=1):
    """通用重试装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"操作失败: {str(e)}, 剩余重试次数: {attempts - _ - 1}")
                    time.sleep(delay)
            raise Exception(f"操作超过最大重试次数 ({attempts})")

        return wrapper

    return decorator


def load_config() -> UserConfig:
    """加载并验证配置文件"""
    config_path = "config.json"
    if not os.path.exists(config_path):
        create_default_config(config_path)
        logger.error("配置文件不存在，已创建默认配置")
        exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = json.load(f)

    validate_required_fields(raw_config)
    courses = [
        CourseConfig(**course) for course in raw_config.get("courses", [])
    ]
    validate_courses(courses)

    return UserConfig(
        user_account=raw_config["user_account"],
        user_password=raw_config["user_password"],
        select_semester=raw_config.get("select_semester", ""),
        mode=raw_config.get("mode", "fast"),
        courses=courses
    )


def create_default_config(path: str):
    """创建默认配置文件"""
    default_config = {
        "user_account": "",
        "user_password": "",
        "select_semester": "",
        "mode": "fast",
        "courses": [{"course_id_or_name": "", "teacher_name": ""} for _ in range(3)]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4)


def validate_required_fields(config: dict):
    """验证必填字段"""
    required = ["schedule_time","user_account", "user_password"]
    missing = [field for field in required if not config.get(field)]
    if missing:
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")


def validate_courses(courses: List[CourseConfig]):
    """验证课程配置"""
    for course in courses:
        if not course.course_id_or_name or not course.teacher_name:
            raise ValueError("课程必须包含 course_id_or_name 和 teacher_name")
        if course.week_day and course.week_day not in list("1234567"):
            raise ValueError(f"课程 {course.course_id_or_name} 的 week_day 无效")


@retry(Exception, attempts=RETRY_ATTEMPTS, delay=RETRY_DELAY)
def get_initial_session() -> str:
    """初始化会话并获取初始数据"""
    session = init_session()
    response = session.get(URLS["init_data"], timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.text


@retry(Exception, attempts=3, delay=1)
def handle_captcha() -> str:
    """处理验证码识别"""
    session = get_session()
    response = session.get(URLS["rand_code"], timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    try:
        image = Image.open(BytesIO(response.content))
        return get_ocr_res(image)
    except Exception as e:
        logger.error(f"验证码处理失败: {str(e)}")
        raise


def generate_encoded_string(data_str: str, account: str, password: str) -> str:
    """生成加密字符串"""
    code, sxh = data_str.split("#")[:2]
    data = f"{account}%%%{password}"
    encoded = []
    code_idx = 0

    for i in range(min(20, len(data))):
        encoded.append(data[i])
        encoded.extend([code[code_idx + j] for j in range(int(sxh[i]))])
        code_idx += int(sxh[i])

    if len(data) > 20:
        encoded.append(data[20:])

    return "".join(encoded)


@retry(Exception, attempts=3, delay=1)
def login(account: str, password: str, code: str, encoded: str) -> bool:
    """执行登录操作"""
    session = get_session()
    headers = {
        "Referer": BASE_URL,
        "Origin": BASE_URL,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }
    data = {
        "userAccount": account,
        "userPassword": password,
        "RANDOMCODE": code,
        "encoded": encoded
    }

    response = session.post(URLS["login"], headers=headers, data=data, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    if "验证码错误" in response.text:
        raise ValueError("验证码错误")
    if "密码错误" in response.text:
        raise PermissionError("用户名或密码错误")
    return True


def print_welcome():
    """打印欢迎信息"""
    logger.info(f"\n{'*' * 10} 曲阜师范大学教务系统抢课脚本 {'*' * 10}\n")
    logger.info("By W1ndys | https://github.com/W1ndys")
    logger.info(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("免责声明: 本脚本仅供学习研究用途，使用者需自行承担风险")


def select_courses_strategy(courses: List[CourseConfig], mode: str):
    """选课策略分发"""
    strategies = {
        "fast": lambda: [search_and_select_course(course) for course in courses],
        "normal": lambda: [search_and_select_course(course) or time.sleep(5) for course in courses],
        "snipe": lambda: (search_and_select_course(course) for course in courses) or time.sleep(2)
    }

    strategy = strategies.get(mode, strategies["snipe"])
    while True:
        strategy()
        logger.info(f"{mode}模式执行完成，等待下次循环")


def main_flow(config: UserConfig):
    """主业务流程"""
    print_welcome()

    # 初始化会话
    data_str = get_initial_session()
    encoded = generate_encoded_string(data_str, config.user_account, config.user_password)

    # 登录流程
    for _ in range(RETRY_ATTEMPTS):
        try:
            captcha = handle_captcha()
            logger.info(f"验证码识别结果: {captcha}")
            if login(config.user_account, config.user_password, captcha, encoded):
                logger.info("登录成功")
                break
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            time.sleep(RETRY_DELAY)
    else:
        raise Exception("登录超过最大重试次数")

    # 访问必要页面
    session = get_session()
    for url in [URLS["main_page"], URLS["course_selection"]]:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

    # 获取选课编号并执行选课
    jx0502zbid = get_jx0502zbid(session, config.select_semester)
    if not jx0502zbid:
        raise ValueError("获取选课编号失败")

    logger.info(f"选课编号: {jx0502zbid}")
    session.get(f"{BASE_URL}/jsxsd/xsxk/xsxk_index?jx0502zbid={jx0502zbid}")
    select_courses_strategy(config.courses, config.mode)


if __name__ == "__main__":
    try:
        config = load_config()
        main_flow(config)
    except Exception as e:
        logger.critical(f"程序异常终止: {str(e)}")
        exit(1)