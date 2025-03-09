from PIL import Image
from io import BytesIO
from src.utils.captcha_ocr import get_ocr_res
import os
import json
from dotenv import load_dotenv
from src.core.course_selector import get_jx0502zbid
from src.core.search_and_select_course import search_and_select_course
from src.utils.session_manager import init_session, get_session
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
    console_handler.setLevel(logging.INFO)  # 设置控制台处理器的日志级别为INFO
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


def generate_encoded_string(user_account, user_password):
    """
    生成登录所需的encoded字符串
    参数:
        data_str: 初始数据字符串 (实际未使用)
        user_account: 用户账号
        user_password: 用户密码
    返回: encoded字符串 (账号base64 + %%% + 密码base64)
    """
    import base64

    # 对账号和密码分别进行base64编码
    account_b64 = base64.b64encode(user_account.encode()).decode()
    password_b64 = base64.b64encode(user_password.encode()).decode()

    # 拼接编码后的字符串
    encoded = f"{account_b64}%%%{password_b64}"

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
        mode: 选课模式
        courses: 课程列表
    """
    # 检查配置文件是否存在
    if not os.path.exists("config.json"):
        # 创建默认配置文件
        default_config = {
            "user_account": "",
            "user_password": "",
            "select_semester": "",
            "dingtalk_webhook": "",
            "dingtalk_secret": "",
            "feishu_webhook": "",
            "feishu_secret": "",
            "mode": "snipe",
            "courses": [
                {
                    "course_id_or_name": "",
                    "teacher_name": "",
                    "class_period": "",
                    "week_day": "",
                    "weeks": "",
                    "jx02id": "",
                    "jx0404id": "",
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

    # 验证必填字段
    required_fields = ["user_account", "user_password"]
    for field in required_fields:
        if not config.get(field):
            raise ValueError(f"配置文件中缺少必填字段: {field}")

    # 验证课程配置
    for course in config.get("courses", []):
        # 检查必填字段
        if not course.get("course_id_or_name") or not course.get("teacher_name"):
            raise ValueError("每个课程配置必须包含 course_id_or_name 和 teacher_name")

        # 验证 week_day 格式（如果提供）
        if course.get("week_day") and not course["week_day"] in [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
        ]:
            raise ValueError(
                f"课程【{course['course_id_or_name']}-{course['teacher_name']}】的 week_day 格式错误: "
                "必须是 1-7 之间的数字"
            )

    # 验证选课模式
    valid_modes = ["fast", "normal", "snipe"]
    if config.get("mode") and config["mode"] not in valid_modes:
        logger.warning(f"无效的选课模式: {config['mode']}，将使用默认的 snipe 模式")
        config["mode"] = "snipe"

    return (
        config["user_account"],
        config["user_password"],
        config["select_semester"],
        config.get("mode", "snipe"),
        config.get("courses", []),
    )


def simulate_login(user_account, user_password):
    """
    模拟登录过程
    返回: 是否登录成功
    """

    for attempt in range(3):
        random_code = handle_captcha()
        logger.info(f"验证码: {random_code}")
        encoded = generate_encoded_string(user_account, user_password)
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


def select_courses(courses, mode, select_semester):
    # 创建一个字典来跟踪每个课程的选课状态
    course_status = {
        f"{c['course_id_or_name']}-{c['teacher_name']}": False for c in courses
    }

    if mode == "fast":
        # 高速模式：以最快速度持续尝试选课
        for course in courses:
            result = search_and_select_course(course)
            if result:
                course_status[
                    f"{course['course_id_or_name']}-{course['teacher_name']}"
                ] = True

            # 检查是否所有课程都已选上
            if all(course_status.values()):
                logger.info("所有课程已选择成功，程序即将退出...")
                exit(0)

    elif mode == "normal":
        # 普通模式：正常速度选课，每次请求间隔较长
        for course in courses:
            result = search_and_select_course(course)
            if result:
                course_status[
                    f"{course['course_id_or_name']}-{course['teacher_name']}"
                ] = True

            # 检查是否所有课程都已选上
            if all(course_status.values()):
                logger.info("所有课程已选择成功，程序即将退出...")
                exit(0)

            logger.info(
                f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课操作结束，等待5秒后继续选下一节课"
            )
            time.sleep(5)

    elif mode == "snipe":
        # 蹲课模式：每次选课前刷新轮次，持续执行选课操作
        session = get_session()
        while True:
            # 检查是否所有课程都已选上
            if all(course_status.values()):
                logger.info("所有课程已选择成功，程序即将退出...")
                exit(0)

            # 每次选课前刷新选课轮次ID
            current_jx0502zbid = get_jx0502zbid(session, select_semester)
            if not current_jx0502zbid:
                logger.warning(
                    "获取选课轮次失败，1秒后重试...若持续失败，可能是账号被踢，请重新运行脚本"
                )
                time.sleep(1)
                continue

            response = session.get(
                f"http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid={current_jx0502zbid}"
            )
            logger.debug(f"选课页面响应状态码: {response.status_code}")

            # 执行选课操作
            for course in courses:
                # 如果该课程已经选上，则跳过
                if course_status[
                    f"{course['course_id_or_name']}-{course['teacher_name']}"
                ]:
                    continue

                result = search_and_select_course(course)
                if result:
                    course_status[
                        f"{course['course_id_or_name']}-{course['teacher_name']}"
                    ] = True
                logger.info(
                    f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课操作结束"
                )

            logger.info("本轮选课操作完成，2秒后开始新一轮选课...")
            time.sleep(2)
    else:
        logger.warning(
            "模式错误，请检查配置文件的mode字段是否为fast、normal或snipe，即将默认使用snipe模式"
        )
        mode = "snipe"
        select_courses(courses, mode, select_semester)


def main():
    """
    主函数，协调整个程序的执行流程
    """
    print_welcome()

    # 获取环境变量
    user_account, user_password, select_semester, mode, courses = get_user_config()

    if user_account:
        logger.info("成功获取配置文件")
        logger.info(f"用户名: {user_account}")

    while True:  # 添加外层循环
        try:
            # 模拟登录
            if not simulate_login(user_account, user_password):
                logger.error("无法建立会话，请检查网络连接或教务系统的可用性。")
                time.sleep(1)  # 添加重试间隔
                continue  # 重试登录

            session = get_session()
            if not session:
                logger.error("无法建立会话，请检查网络连接或教务系统的可用性。")
                time.sleep(1)
                continue

            # 访问主页和选课页面
            for page_url in [
                "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp",
                "http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xklc_list",
            ]:
                for attempt in range(3):
                    try:
                        response = session.get(page_url)
                        logger.debug(f"页面响应状态码: {response.status_code}")
                        if response.status_code == 200:
                            break
                    except Exception as e:
                        if attempt == 2:
                            logger.error(f"访问页面失败: {str(e)}")
                            raise
                        logger.warning(f"访问页面失败，正在进行第{attempt + 2}次尝试")
                        continue

            # 获取选课轮次编号
            jx0502zbid = get_jx0502zbid(session, select_semester)
            if jx0502zbid:
                logger.critical(f"成功获取到选课轮次ID: {jx0502zbid}")
                response = session.get(
                    f"http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid={jx0502zbid}"
                )
                logger.debug(f"选课页面响应状态码: {response.status_code}")
                select_courses(courses, mode, select_semester)
                break  # 成功后退出循环
            else:
                logger.warning("获取选课轮次编号失败，正在重新登录...")
                time.sleep(1)
                continue  # 重新登录

        except Exception as e:
            logger.error(f"发生错误: {str(e)}，正在重新登录...")
            time.sleep(1)
            continue  # 重新登录


if __name__ == "__main__":
    main()
