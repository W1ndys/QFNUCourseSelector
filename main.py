import os
import sys
import json
import time
import datetime
import traceback
import asyncio
from io import BytesIO

from PIL import Image
from dotenv import load_dotenv
from loguru import logger

# 添加项目根目录到sys.path以支持相对导入
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.captcha_ocr import get_ocr_res
from src.core.course_selector import get_jx0502zbid
from src.core.search_and_select_course import search_and_select_course
from src.utils.session_manager import get_session
from src.utils.feishu import feishu


# 配置日志
# 确保logs目录存在
if not os.path.exists("logs"):
    os.makedirs("logs")
logger.remove()
# 设置控制台输出
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
)

load_dotenv()


async def handle_captcha():
    """
    获取并识别验证码
    返回: 识别出的验证码字符串
    """
    session = await get_session()

    # 验证码请求URL
    RandCodeUrl = "http://zhjw.qfnu.edu.cn/jsxsd/verifycode.servlet"

    response = await session.get(RandCodeUrl)

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


async def login(random_code, encoded):
    """
    执行登录操作
    返回: 登录响应结果
    """

    # 登录请求URL
    loginUrl = "http://zhjw.qfnu.edu.cn/jsxsd/xk/LoginToXkLdap"
    session = await get_session()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Origin": "http://zhjw.qfnu.edu.cn",
        "Referer": "http://zhjw.qfnu.edu.cn/",
    }

    data = {
        "userAccount": "",
        "userPassword": "",
        "RANDOMCODE": random_code,
        "encoded": encoded,
    }

    return await session.post(loginUrl, headers=headers, data=data, timeout=1000)


def get_user_config():
    """
    获取用户配置
    返回:
        user_account: 用户账号
        user_password: 用户密码
        courses: 课程列表
    """
    # 检查配置文件是否存在
    if not os.path.exists("config.json"):
        # 创建默认配置文件
        default_config = {
            "user_account": "你的学号",
            "user_password": "你的教务系统密码",
            "feishu_webhook": "",
            "courses": [
                {
                    "course_name": "你的课程名称",
                    "course_id": "你的课程编号",
                    "teacher_name": "你的老师名称",
                    "jx02id": "",
                    "jx0404id": "",
                    "week_day": "",
                    "class_period": "",
                    "class_times": [
                        {
                            "week": "",
                            "week_day": "",
                            "class_period": ""
                        }
                    ]
                }
            ],
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        logger.error(
            "配置文件不存在，已创建默认配置文件 config.json\n请填写相关信息后重新运行程序"
        )
        # 暂停让用户查看错误信息
        input("按回车键退出程序...")
        exit(0)

    # 读取配置文件
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        # 验证必填字段
        required_fields = ["user_account", "user_password"]
        for field in required_fields:
            if not config.get(field):
                logger.error(f"配置文件中缺少必填字段: {field}")
                input("按回车键退出程序...")
                exit(1)

        # 验证课程配置
        for course in config.get("courses", []):
            # 检查基础必填字段
            base_required_fields = ["course_name", "course_id", "teacher_name"]
            missing_fields = [field for field in base_required_fields if not course.get(field)]
            if missing_fields:
                logger.error(
                    f"每个课程配置必须包含以下字段: {', '.join(base_required_fields)}\n"
                    f"缺失的字段: {', '.join(missing_fields)}"
                )
                input("按回车键退出程序...")
                exit(1)

            # 检查选课模式：要么填写jx02id和jx0404id，要么填写搜索参数
            jx02id = course.get("jx02id", "").strip()
            jx0404id = course.get("jx0404id", "").strip()
            week_day = course.get("week_day", "").strip()
            class_period = course.get("class_period", "").strip()
            class_times = course.get("class_times", [])

            has_direct_ids = jx02id and jx0404id
            has_search_params = week_day and class_period and class_times

            if not has_direct_ids and not has_search_params:
                logger.error(
                    f"课程【{course['course_name']}-{course['teacher_name']}】配置无效：\n"
                    f"请填写以下两种方式之一：\n"
                    f"1. 直接填写 jx02id 和 jx0404id\n"
                    f"2. 填写搜索参数：week_day(星期几)、class_period(节次范围) 和 class_times(上课时间列表)"
                )
                input("按回车键退出程序...")
                exit(1)

            # 如果使用搜索模式，验证参数格式
            if has_search_params:
                # 验证week_day为1-7的数字
                if not week_day.isdigit() or not (1 <= int(week_day) <= 7):
                    logger.error(
                        f"课程【{course['course_name']}-{course['teacher_name']}】的 week_day(星期几) 必须为1-7之间的数字"
                    )
                    input("按回车键退出程序...")
                    exit(1)

                # 验证class_period为有效的节次范围
                valid_periods = ["1-2", "3-4", "5-6", "7-8", "9-11", "12-13"]
                if class_period not in valid_periods:
                    logger.error(
                        f"课程【{course['course_name']}-{course['teacher_name']}】的 class_period(节次范围) 必须为以下之一：{', '.join(valid_periods)}"
                    )
                    input("按回车键退出程序...")
                    exit(1)

                # 验证class_times
                if not isinstance(class_times, list) or not class_times:
                    logger.error(
                        f"课程【{course['course_name']}-{course['teacher_name']}】的 class_times 必须为非空列表"
                    )
                    input("按回车键退出程序...")
                    exit(1)

                for idx, time_node in enumerate(class_times):
                    t_week = str(time_node.get("week", "")).strip()
                    t_week_day = str(time_node.get("week_day", "")).strip()
                    t_class_period = str(time_node.get("class_period", "")).strip()

                    if not t_week.isdigit():
                        logger.error(f"课程【{course['course_name']}】第{idx+1}个时间节点的 week 必须为数字")
                        input("按回车键退出程序...")
                        exit(1)
                    if not t_week_day.isdigit() or not (1 <= int(t_week_day) <= 7):
                        logger.error(f"课程【{course['course_name']}】第{idx+1}个时间节点的 week_day 必须为1-7之间的数字")
                        input("按回车键退出程序...")
                        exit(1)
                    if not t_class_period.isdigit() or not (1 <= int(t_class_period) <= 13):
                        logger.error(f"课程【{course['course_name']}】第{idx+1}个时间节点的 class_period 必须为数字(1-13)")
                        input("按回车键退出程序...")
                        exit(1)

        return (
            config["user_account"],
            config["user_password"],
            config.get("courses", []),
        )
    except json.JSONDecodeError:
        logger.error("配置文件格式错误，请检查 config.json 文件格式是否正确")
        input("按回车键退出程序...")
        exit(1)
    except Exception as e:
        logger.error(f"读取配置文件时发生错误: {str(e)}")
        input("按回车键退出程序...")
        exit(1)


async def simulate_login(user_account, user_password):
    """
    模拟登录过程
    返回: 是否登录成功
    """
    session = await get_session()
    # 访问教务系统首页，获取必要的cookie
    response = await session.get("http://zhjw.qfnu.edu.cn/jsxsd/")
    if response.status_code != 200:
        logger.error("无法访问教务系统首页，请检查网络连接或教务系统的可用性。")
        return False

    # 获取必要的cookie
    cookies = session.cookies
    logger.info(f"获取到的cookie: {cookies}")

    for attempt in range(3):
        random_code = await handle_captcha()
        logger.info(f"验证码: {random_code}")
        encoded = generate_encoded_string(user_account, user_password)
        logger.info(f"encoded: {encoded}")
        response = await login(random_code, encoded)
        logger.info(f"登录响应: {response.status_code}")

        if response.status_code == 200:
            if "验证码错误" in response.text:
                logger.warning(f"验证码识别错误，重试第 {attempt + 1} 次")
                continue
            if "密码错误" in response.text:
                raise Exception("用户名或密码错误")
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


def get_course_key(course):
    """
    生成课程唯一标识
    优先使用 jx02id 和 jx0404id，如果为空则使用 course_id + teacher_name + 搜索参数
    """
    jx02id = course.get("jx02id", "").strip()
    jx0404id = course.get("jx0404id", "").strip()

    if jx02id and jx0404id:
        return f"{jx02id}-{jx0404id}"
    else:
        # 使用课程ID、教师名和搜索参数作为唯一标识
        # 由于class_times是列表，将其转换为字符串作为key的一部分
        class_times_str = "-".join([f"{t.get('week')}_{t.get('week_day')}_{t.get('class_period')}" for t in course.get('class_times', [])])
        return f"{course['course_id']}-{course['teacher_name']}-{course.get('week_day', '')}-{course.get('class_period', '')}-{class_times_str}"


async def select_courses(courses):
    """
    蹲课模式：持续尝试选课，每个课程之间间隔0.5秒
    依次遍历每个选课轮次，如果某课程在某轮次选课成功，则锁定该轮次
    """
    # 创建一个字典来跟踪每个课程的选课状态
    # 状态值：False=未选上, True=已选上, "permanent_failure"=永久失败
    course_status = {
        get_course_key(c): False for c in courses
    }

    # 记录每个课程锁定的轮次 ID，None 表示尚未锁定
    locked_rounds = {
        get_course_key(c): None for c in courses
    }

    # 对课程进行分组：相同课程名字和相同老师的视为同一组
    course_groups = {}
    for course in courses:
        group_key = (course['course_name'], course['teacher_name'])
        if group_key not in course_groups:
            course_groups[group_key] = []
        course_groups[group_key].append(course)

    start_time = time.time()  # 记录开始时间
    await feishu("曲阜师范大学教务系统抢课脚本", "选课开始")

    session = await get_session()

    async def process_group(group_courses, round_id, round_name):
        """
        处理单个课程组：组内串行执行
        """
        group_attempted = False
        for course in group_courses:
            course_key = get_course_key(course)
            
            # 如果该课程已经选上或永久失败，则跳过
            if course_status[course_key] is not False:
                continue

            # 如果该课程已经锁定了轮次，只在锁定的轮次尝试
            if locked_rounds[course_key] is not None:
                if locked_rounds[course_key] != round_id:
                    continue
            
            group_attempted = True
            try:
                result = await search_and_select_course(course)
                
                if result is True:
                    course_status[course_key] = True
                    locked_rounds[course_key] = round_id
                    logger.info(f"课程【{course['course_name']}-{course['teacher_name']}】在轮次【{round_name}】选课成功，已锁定该轮次")
                elif result == "permanent_failure":
                    course_status[course_key] = "permanent_failure"
                    logger.critical(f"课程【{course['course_name']}-{course['teacher_name']}】永久失败，不再重试")
                else:
                    logger.info(f"课程【{course['course_name']}-{course['teacher_name']}】在轮次【{round_name}】选课失败，将尝试下一轮次")

            except Exception as e:
                logger.error(f"课程【{course['course_name']}】选课异常: {str(e)}")
        
        return group_attempted

    # 蹲课模式：持续执行选课操作
    while True:
        # 检查是否所有课程都已选上或永久失败
        active_courses = [status for status in course_status.values() if status is False]
        if not active_courses:
            end_time = time.time()  # 记录结束时间
            success_count = sum(1 for status in course_status.values() if status is True)
            failed_count = sum(1 for status in course_status.values() if status == "permanent_failure")
            
            logger.info("所有课程处理完成，程序即将退出...")
            logger.info(f"总耗时: {end_time - start_time:.2f} 秒")
            logger.info(f"成功选上: {success_count} 门课程")
            if failed_count > 0:
                logger.info(f"永久失败: {failed_count} 门课程")
            
            await feishu(
                "曲阜师范大学教务系统抢课脚本",
                f"所有课程处理完成\n成功选上: {success_count} 门\n永久失败: {failed_count} 门\n总耗时: {end_time - start_time:.2f} 秒",
            )
            return True
        
        # 获取所有选课轮次
        all_rounds = await get_jx0502zbid(session)
        if not all_rounds:
            logger.warning(
                "获取选课轮次失败，1秒后重试...若持续失败，可能是账号被踢，请重新运行脚本"
            )
            await asyncio.sleep(1)
            continue

        logger.info(f"获取到 {len(all_rounds)} 个选课轮次")

        # 遍历每个轮次
        for round_info in all_rounds:
            round_id = round_info["jx0502zbid"]
            round_name = round_info["name"]
            
            logger.info(f"正在尝试轮次: {round_name} (ID: {round_id})")

            # 访问选课页面
            try:
                response = await session.get(
                    f"http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xsxk_index?jx0502zbid={round_id}"
                )
                logger.debug(f"选课页面响应状态码: {response.status_code}")
            except Exception as e:
                logger.error(f"访问选课页面失败: {e}")
                continue

            # 创建并发任务：每个课程组作为一个任务并行执行
            group_tasks = []
            for group_courses in course_groups.values():
                group_tasks.append(process_group(group_courses, round_id, round_name))

            if group_tasks:
                # 并发执行所有组
                results = await asyncio.gather(*group_tasks, return_exceptions=True)
                
                # 检查是否有任何组进行了尝试
                round_had_attempts = any(res is True for res in results if not isinstance(res, Exception))
                
                if not round_had_attempts:
                    logger.debug(f"轮次【{round_name}】没有需要尝试的课程，跳过")
            else:
                 logger.debug(f"轮次【{round_name}】没有任务")

            # 每个轮次之间稍微停顿一下，避免过快请求
            await asyncio.sleep(0.5)

        logger.info("所有轮次尝试完成，准备重新开始...")
        await asyncio.sleep(0.5)


async def main_async():
    """
    主函数，协调整个程序的执行流程
    """
    try:
        print_welcome()

        print(
            "本项目具有严重的安全风险和非预期运行，有极大概率无法正常的选课，为避免影响正常选课，请勿继续使用，相关代码仅供学习研究使用，请勿用于实际的选课环境中，使用脚本造成的一切后果与开发者无关。\n"
        )
        # input在async中会阻塞，这里简单处理，实际可替换为非阻塞方式或直接去掉等待
        await asyncio.to_thread(input, "按回车键继续...")

        # 获取环境变量
        user_account, user_password, courses = get_user_config()

        # 添加文件日志
        start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join("logs", f"{user_account}_{start_time}.log")
        logger.add(
            log_file_path,
            encoding="utf-8",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )

        if user_account:
            logger.info("成功获取配置文件")
            logger.info(f"用户名: {user_account}")

        while True:  # 添加外层循环
            try:
                # 模拟登录
                if not await simulate_login(user_account, user_password):
                    logger.error("无法建立会话，请检查网络连接或教务系统的可用性。")
                    await asyncio.sleep(1)  # 添加重试间隔
                    continue  # 重试登录

                session = await get_session()
                if not session:
                    logger.error("无法建立会话，请检查网络连接或教务系统的可用性。")
                    await asyncio.sleep(1)
                    continue

                # 访问主页和选课页面
                for page_url in [
                    "http://zhjw.qfnu.edu.cn/jsxsd/framework/xsMain.jsp",
                    "http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xklc_list",
                ]:
                    for attempt in range(3):
                        try:
                            response = await session.get(page_url)
                            logger.debug(f"页面响应状态码: {response.status_code}")
                            if response.status_code == 200:
                                break
                        except Exception as e:
                            if attempt == 2:
                                logger.error(f"访问页面失败: {str(e)}")
                                raise
                            logger.warning(
                                f"访问页面失败，正在进行第{attempt + 2}次尝试"
                            )
                            continue

                # 获取选课轮次列表
                all_rounds = await get_jx0502zbid(session)
                while not all_rounds:
                    logger.warning("获取选课轮次失败，1秒后重试...")
                    await asyncio.sleep(1)
                    all_rounds = await get_jx0502zbid(session)

                logger.critical(f"成功获取到 {len(all_rounds)} 个选课轮次")
                for round_info in all_rounds:
                    logger.info(f"轮次: {round_info['name']} (ID: {round_info['jx0502zbid']})")
                
                await select_courses(courses)
                break  # 成功后退出循环

            except Exception as e:
                logger.error(f"发生错误: {str(e)}，正在重新登录...")
                await asyncio.sleep(1)
                continue  # 重新登录
    except KeyboardInterrupt:
        logger.info("用户手动终止程序")
        # await asyncio.to_thread(input, "按回车键退出程序...")
    except Exception as e:
        logger.error(f"程序发生未预期的错误: {str(e)}")
        logger.error(traceback.format_exc())
        await asyncio.to_thread(input, "按回车键退出程序...")


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        # 处理 Ctrl+C
        pass

if __name__ == "__main__":
    main()
