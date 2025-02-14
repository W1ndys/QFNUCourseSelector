import os
import json
from src.utils.session_manager import get_session
import logging

# 添加一个全局缓存字典
course_cache = {}
# 添加一个全局变量用于缓存整个文件数据
all_courses_data_cache = None


def find_course_jx02id_and_jx0404id(course, course_data):
    """在课程数据中查找课程的jx02id和jx0404id"""
    try:
        for course_item in course_data:
            # 检查course_item是否为字典
            if not isinstance(course_item, dict):
                logging.error(f"课程项不是字典: {course_item}")
                continue
            try:
                if (
                    # 检查课程编号或课程名称是否匹配
                    (course_item.get("kch") or course_item.get("kcmc"))
                    == course["course_id_or_name"]
                    # 检查教师姓名是否匹配
                    and course_item.get("skls") == course["teacher_name"]
                    # 检查上课时间或上课节次是否匹配
                    and (
                        course_item.get("sksj", "")
                        .replace("&nbsp;", "")
                        .replace(" ", "")
                        == course["course_time"].replace(" ", "")
                        # 判断课程时间是否包含课程节次
                        or course["class_period"].rstrip("-")  # 修剪字符串末尾的-
                        in course_item.get("sksj")
                    )
                ):
                    return {
                        "jx02id": course_item.get("jx02id"),
                        "jx0404id": course_item.get("jx0404id"),
                    }
            except (KeyError, AttributeError) as e:
                logging.error(f"处理课程项时出错: {str(e)}")
                continue
        return None
    except Exception as e:
        logging.error(f"查找课程jx02id和jx0404id时发生错误: {str(e)}")
        return None


def get_course_jx02id_and_jx0404id_by_api(course):
    """通过教务系统API获取课程的jx02id和jx0404id"""
    try:
        # 依次从专业内跨年级选课、本学期计划选课、选修选课、公选课选课、计划外选课、辅修选课搜索课程
        result = get_course_jx02id_and_jx0404id_xsxkKnjxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkBxqjhxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkXxxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkGgxxkxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result

        result = get_course_jx02id_and_jx0404id_xsxkFawxk_by_api(course)
        if result:
            result = find_course_jx02id_and_jx0404id(course, result["aaData"])
            if result:
                return result
    except Exception as e:
        logging.error(f"获取课程的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_by_file(course):
    """通过本地文件获取课程的jx02id和jx0404id"""
    global all_courses_data_cache

    # 检查缓存中是否已有数据
    cache_key = (
        course["course_id_or_name"],
        course["teacher_name"],
        course["course_time"],
    )
    if cache_key in course_cache:
        logging.info(f"从缓存中获取课程: {course['course_id_or_name']}")
        return course_cache[cache_key]

    try:
        # 如果全局缓存为空，则读取文件
        if all_courses_data_cache is None:
            all_courses_json_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "course_data",
                    "all_courses.json",
                )
            )
            if not os.path.exists(all_courses_json_path):
                logging.error(f"课程数据文件不存在: {all_courses_json_path}")
                return None
            with open(all_courses_json_path, "r", encoding="utf-8") as file:
                all_courses_data_cache = json.load(file)

        course_jx02id_and_jx0404id = find_course_jx02id_and_jx0404id(
            course, all_courses_data_cache["aaData"]
        )
        if course_jx02id_and_jx0404id:
            # 将结果存入缓存
            course_cache[cache_key] = course_jx02id_and_jx0404id
            return course_jx02id_and_jx0404id

    except Exception as e:
        logging.error(f"获取公选课选课页面数据失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkGgxxkxk_by_api(course):
    """通过教务系统API获取公选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
        )
        logging.info(f"获取公选选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 13,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取公选选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取公选选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkXxxk_by_api(course):
    """通过教务系统API获取选修课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
        )
        logging.info(f"获取选修选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkXxxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 11,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取选修选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取选修选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkBxqjhxk_by_api(course):
    """通过教务系统API获取本学期计划选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk",
        )
        logging.info(f"获取本学期计划选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkBxqjhxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 12,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取本学期计划选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取本学期计划选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkKnjxk_by_api(course):
    """通过教务系统API获取专业内跨年级选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 专业内跨年级选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInKnjxk",
        )
        logging.info(f"获取专业内跨年级选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkKnjxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 12,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取专业内跨年级选课列表数据响应值: {response.status_code}")

        # 新增代码：检查响应内容是否为JSON格式
        try:
            response_data = json.loads(response.text)

            # 检查aaData是否为空
            if not response_data.get("aaData"):
                logging.warning("API返回的aaData为空")
                return None

            return response_data
        except ValueError:
            logging.error("API返回的数据不是有效的JSON格式")
            return None

    except Exception as e:
        logging.error(f"获取专业内跨年级选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkFawxk_by_api(course):
    """通过教务系统API获取计划外选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]
        class_period = course["class_period"]
        week_day = course["week_day"]

        # 计划外选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk",
        )
        logging.info(f"获取计划外选课页面响应值: {response.status_code}")

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkFawxk",
            params={
                "kcxx": course_id,  # 课程名称
                "skls": teacher_name,  # 教师姓名
                "skxq": week_day,  # 上课星期
                "skjc": class_period,  # 上课节次
                "sfym": "false",  # 是否已满
                "sfct": "false",  # 是否冲突
                "sfxx": "false",  # 是否限选
            },
            data={
                "sEcho": 1,
                "iColumns": 12,
                "sColumns": "",
                "iDisplayStart": 0,
                "iDisplayLength": 15,
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "ktmc",
                "mDataProp_4": "xf",
                "mDataProp_5": "skls",
                "mDataProp_6": "sksj",
                "mDataProp_7": "skdd",
                "mDataProp_8": "xqmc",
                "mDataProp_9": "ctsm",
                "mDataProp_10": "czOper",
            },
        )

        logging.info(f"获取计划外选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("API返回的aaData为空")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取计划外选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id(course):
    """优先通过API获取课程的jx02id和jx0404id，如果未找到，再从本地文件中查找"""

    # 尝试通过API获取
    result = get_course_jx02id_and_jx0404id_by_api(course)
    if result:
        logging.critical(
            f"通过API找到课程: 【{course['course_id_or_name']}】的 jx02id：{result['jx02id']} 和 jx0404id：{result['jx0404id']}"
        )
        return result

    # 如果API未找到，尝试从本地文件获取
    result = get_course_jx02id_and_jx0404id_by_file(course)
    if result:
        logging.critical(
            f"通过本地文件找到课程: 【{course['course_id_or_name']}】的 jx02id：{result['jx02id']} 和 jx0404id：{result['jx0404id']}"
        )
        return result

    logging.warning(f"未能找到课程: {course['course_id_or_name']}的jx02id和jx0404id")
    return None
