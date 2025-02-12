import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from captcha_ocr import get_ocr_res
import os
import json
from dotenv import load_dotenv
from course_selector import get_jx0502zbid
from search_and_select_course import search_and_select_course
from session_manager import init_session, get_session
import colorlog
import logging
import datetime
import time


def setup_logger():
    """
    配置日志系统
    """
    # 确保logs目录存在
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # 创建logger
    logger = colorlog.getLogger()
    logger.setLevel(logging.DEBUG)

    # 清除可能存在的处理器
    if logger.handlers:
        logger.handlers.clear()

    # 配置文件处理器 - 使用普通的Formatter
    file_handler = logging.FileHandler(
        os.path.join(
            "logs", f'app_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        encoding="utf-8",
    )
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    # 配置控制台处理器 - 使用ColoredFormatter
    console_handler = colorlog.StreamHandler()
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s: %(message)s%(reset)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    console_handler.setFormatter(console_formatter)

    # 添加处理器到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 在文件开头调用setup_logger
logger = setup_logger()

load_dotenv()


# 设置基本的URL和数据

# 验证码请求URL
RandCodeUrl = "http://zhjw.qfnu.edu.cn/verifycode.servlet"
# 登录请求URL
loginUrl = "http://zhjw.qfnu.edu.cn/Logon.do?method=logonLdap"
# 初始数据请求URL
dataStrUrl = "http://zhjw.qfnu.edu.cn/Logon.do?method=logon&flag=sess"


def get_initial_session():
    """
    创建会话并获取初始数据
    返回: 初始数据字符串
    """
    session = init_session()  # 初始化全局session
    response = session.get(dataStrUrl)
    return response.text


def handle_captcha():
    """
    获取并识别验证码
    返回: 识别出的验证码字符串
    """
    session = get_session()
    response = session.get(RandCodeUrl)

    if response.status_code != 200:
        logger.error(f"请求验证码失败，状态码: {response.status_code}")
        return None

    try:
        image = Image.open(BytesIO(response.content))
    except Exception as e:
        logger.error(f"无法识别图像文件: {e}")
        return None

    return get_ocr_res(image)


def generate_encoded_string(data_str, user_account, user_password):
    """
    生成登录所需的encoded字符串
    参数:
        data_str: 初始数据字符串
        user_account: 用户账号
        user_password: 用户密码
    返回: encoded字符串
    """
    res = data_str.split("#")
    code, sxh = res[0], res[1]
    data = f"{user_account}%%%{user_password}"
    encoded = ""
    b = 0

    for a in range(len(code)):
        if a < 20:
            encoded += data[a]
            for _ in range(int(sxh[a])):
                encoded += code[b]
                b += 1
        else:
            encoded += data[a:]
            break
    return encoded


def login(user_account, user_password, random_code, encoded):
    """
    执行登录操作
    返回: 登录响应结果
    """
    session = get_session()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Origin": "http://zhjw.qfnu.edu.cn",
        "Referer": "http://zhjw.qfnu.edu.cn/",
        "Upgrade-Insecure-Requests": "1",
    }

    data = {
        "userAccount": user_account,
        "userPassword": user_password,
        "RANDOMCODE": random_code,
        "encoded": encoded,
    }

    return session.post(loginUrl, headers=headers, data=data, timeout=1000)


def get_user_config():
    """
    获取用户配置
    返回:
        user_account: 用户账号
        user_password: 用户密码
        select_semester: 选课学期
        courses: 课程列表
    """
    # 检查配置文件是否存在
    if not os.path.exists("config.json"):
        # 创建默认配置文件
        default_config = {
            "user_account": "",
            "user_password": "",
            "select_semester": "",
            "courses": [
                {
                    "course_id_or_name": "",
                    "teacher_name": "",
                    "course_time": "",
                    "class_period": "",
                    "week_day": "",
                }
            ],
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        logger.error(
            "配置文件不存在，已创建默认配置文件 config.json\n请填写相关信息后重新运行程序"
        )
        exit(0)

    # 读取配置文件
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return (
        config["user_account"],
        config["user_password"],
        config["select_semester"],
        config["courses"],
    )


def simulate_login(user_account, user_password):
    """
    模拟登录过程
    返回: 是否登录成功
    """
    data_str = get_initial_session()

    for attempt in range(3):
        random_code = handle_captcha()
        logger.info(f"验证码: {random_code}")
        encoded = generate_encoded_string(data_str, user_account, user_password)
        response = login(user_account, user_password, random_code, encoded)

        if response.status_code == 200:
            if "验证码错误!!" in response.text:
                logger.warning(f"验证码识别错误，重试第 {attempt + 1} 次")
                continue
            if "密码错误" in response.text:
                raise Exception("用户名或密码错误")
            logger.info("登录成功")
            return True
        else:
            raise Exception("登录失败")

    raise Exception("验证码识别错误，请重试")


def print_welcome():
    logger.info(f"\n{'*' * 10} 曲阜师范大学教务系统抢课脚本 {'*' * 10}\n")
    logger.info("By W1ndys")
    logger.info("https://github.com/W1ndys")
    logger.info("\n\n")
    logger.info(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("免责声明: ")
    logger.info("1. 本脚本仅供学习和研究目的，用于了解网络编程和自动化技术的实现原理。")
    logger.info(
        "2. 使用本脚本可能违反学校相关规定。使用者应自行承担因使用本脚本而产生的一切后果，包括但不限于："
    )
    logger.info("   - 账号被封禁")
    logger.info("   - 选课资格被取消")
    logger.info("   - 受到学校纪律处分")
    logger.info("   - 其他可能产生的不良影响")
    logger.info("3. 严禁将本脚本用于：")
    logger.info("   - 商业用途")
    logger.info("   - 干扰教务系统正常运行")
    logger.info("   - 影响其他同学正常选课")
    logger.info("   - 其他任何非法或不当用途")
    logger.info(
        "4. 下载本脚本即视为您已完全理解并同意本免责声明。请在下载后 24 小时内删除。"
    )
    logger.info("5. 开发者对使用本脚本造成的任何直接或间接损失不承担任何责任。")


def main():
    """
    主函数，协调整个程序的执行流程
    """
    print_welcome()

    # 获取环境变量
    user_account, user_password, select_semester, courses = get_user_config()

    # 模拟登录
    try:
        if not simulate_login(user_account, user_password):
            logger.error("无法建立会话，请检查网络连接或教务系统的可用性。")
            return
    except Exception as e:
        logger.error(f"登录过程出错: {str(e)}")
        return

    session = get_session()

    if not session:
        logger.error("无法建立会话，请检查网络连接或教务系统的可用性。")
        return
    try:
        # 添加重试逻辑
        for attempt in range(3):
            try:
                response = session.get(
                    "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp"
                )
                logger.debug(f"主页响应状态码: {response.status_code}")
                if response.status_code == 200:
                    break
            except Exception as e:
                if attempt == 2:  # 最后一次尝试
                    logger.error(f"访问主页失败: {str(e)}")
                    raise
                logger.warning(f"访问主页失败，正在进行第{attempt + 2}次尝试")
                continue

        for attempt in range(3):
            try:
                response = session.get("http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xklc_list")
                logger.debug(f"选课页面响应状态码: {response.status_code}")
                if response.status_code == 200:
                    break
            except Exception as e:
                if attempt == 2:  # 最后一次尝试
                    logger.error(f"访问选课页面失败: {str(e)}")
                    raise
                logger.warning(f"访问选课页面失败，正在进行第{attempt + 2}次尝试")
                continue

        jx0502zbid = None
        while True:
            try:
                jx0502zbid = get_jx0502zbid(session, select_semester)
                if jx0502zbid:
                    logger.info(f"成功获取到选课轮次编号: {jx0502zbid}")
                    break
                else:
                    logger.warning(
                        "获取选课轮次编号失败，正在重试。如果多次尝试失败，请检查配置文件或确认选课是否已开启"
                    )
                    time.sleep(1)  # 每次尝试间隔1秒
                    continue
            except Exception as e:
                logger.warning(
                    f"获取选课轮次编号失败: {str(e)}，正在重试。如果多次尝试失败，请检查配置文件或确认选课是否已开启"
                )
                time.sleep(1)

        if jx0502zbid:
            response = session.get(
                f"http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid={jx0502zbid}"
            )
            logger.debug(f"选课页面响应状态码: {response.status_code}")

            # 依次搜索并选课
            for course in courses:
                search_and_select_course(course)

        else:
            logger.error(
                "获取选课轮次编号失败，请检查配置文件或选课暂未开启，请重新运行脚本"
            )
            return

    except Exception as e:
        logger.error(f"主函数选课过程出错: {str(e)}")
        return


if __name__ == "__main__":
    main()
