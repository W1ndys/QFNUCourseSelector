import os
import json
from src.utils.session_manager import get_session
import logging


def find_course_jx02id_and_jx0404id(course, course_data):
    """在课程数据中查找课程的jx02id和jx0404id"""
    try:
        # 由于course_data只包含一条数据，直接获取第一条
        data = course_data[0]

        # 提取jx02id和jx0404id
        jx02id = data.get("jx02id")
        jx0404id = data.get("jx0404id")

        # 确保两个ID都存在
        if jx02id and jx0404id:
            logging.critical(
                f"找到课程 {course['course_id_or_name']} 的jx02id: {jx02id} 和 jx0404id: {jx0404id}"
            )
            return {"jx02id": jx02id, "jx0404id": jx0404id}
        else:
            logging.warning(f"课程数据中缺少jx02id或jx0404id: {data}")
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


def get_course_jx02id_and_jx0404id(course):
    """通过API获取课程的jx02id和jx0404id"""
    try:
        result = get_course_jx02id_and_jx0404id_by_api(course)
        if result:
            return result

        logging.warning(
            f"未能找到课程: {course['course_id_or_name']}的jx02id和jx0404id"
        )
        return None
    except Exception as e:
        logging.error(f"获取课程jx02id和jx0404id时发生错误: {str(e)}")
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
                "szjylb": "",
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
                "mDataProp_2": "xf",
                "mDataProp_3": "skls",
                "mDataProp_4": "sksj",
                "mDataProp_5": "skdd",
                "mDataProp_6": "xqmc",
                "mDataProp_7": "xxrs",
                "mDataProp_8": "xkrs",
                "mDataProp_9": "syrs",
                "mDataProp_10": "ctsm",
                "mDataProp_11": "szkcflmc",
                "mDataProp_12": "czOper",
            },
        )

        logging.info(f"获取公选选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)
        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning("公选选课的API返回的aaData为空，可能该课程不在该分类")
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
            logging.warning("选修选课的API返回的aaData为空，可能该课程不在该分类")
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
            logging.warning("本学期计划选课的API返回的aaData为空，可能该课程不在该分类")
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
                logging.warning(
                    "专业内跨年级选课的API返回的aaData为空，可能该课程不在该分类"
                )
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
            logging.warning("计划外选课的API返回的aaData为空，可能该课程不在该分类")
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取计划外选课的jx02id和jx0404id失败: {e}")
        return None
