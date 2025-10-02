import os
import json
from src.utils.session_manager import get_session
import logging


def find_course_jx02id_and_jx0404id(course, course_data):
    """在课程数据中查找课程的jx02id和jx0404id"""
    try:
        # 如果course_data为空，直接返回None
        if not course_data:
            return None

        # 如果只有一组数据，并且课程号或课程ID和教师姓名都匹配，直接返回
        if (
            len(course_data) == 1
            and (
                course_data[0].get("kch") == course["course_id_or_name"]
                or course_data[0].get("kcmc") == course["course_id_or_name"]
            )
            and course_data[0].get("skls") == course["teacher_name"]
        ):
            data = course_data[0]
            jx02id = data.get("jx02id")
            jx0404id = data.get("jx0404id")
            # 提取 xxrs (选课人数)
            # 路径: data -> 'aaData' -> 列表第1个元素[0] -> 'xxrs'
            xxrs_value = course_data[0]["xxrs"]
            # 提取 skls (授课老师)
            # 路径: data -> 'aaData' -> 列表第1个元素[0] -> 'skls'
            skls_value = course_data[0]["skls"]
            # 提取 kcmc (课程名称)
            # 路径: data -> 'aaData' -> 列表第1个元素[0] -> 'kcmc'
            kcmc_value = course_data[0]["kcmc"]
            if jx02id and jx0404id:
                logging.critical(
                    f"仅有一组数据，直接匹配课程 【{course['course_id_or_name']}-{course['teacher_name']}】 的jx02id: {jx02id} 和 jx0404id: {jx0404id}"
                )
                return {
                    "jx02id": jx02id,
                    "jx0404id": jx0404id,
                    "xxrs": xxrs_value,
                    "skls": skls_value,
                    "kcmc": kcmc_value,
                }

        # 处理周次信息
        def parse_weeks(weeks_str):
            weeks = set()
            # 处理多个周次范围（用逗号分隔）
            for part in weeks_str.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    weeks.update(range(start, end + 1))
                else:
                    weeks.add(int(part))
            return weeks

        def check_weeks_match(target_weeks, actual_weeks):
            """检查实际周次是否匹配目标周次"""
            target_set = parse_weeks(target_weeks)
            actual_set = actual_weeks
            # 判断实际周次是否完全包含目标周次
            return target_set.issubset(actual_set)

        # 遍历所有匹配的课程数据
        for data in course_data:
            # 提取jx02id和jx0404id
            jx02id = data.get("jx02id")
            jx0404id = data.get("jx0404id")

            # 基本信息匹配，先判断名称老师是否匹配，以防后面匹配周次强包容性无问题但名称老师不匹配
            if (
                data.get("kch") != course["course_id_or_name"]
                or data.get("skls") != course["teacher_name"]
            ):
                continue

            # 从sksj中提取周次信息
            sksj = data.get("sksj", "")

            # 判断是否匹配周次
            weeks_match = True
            if "weeks" in course and "周" in sksj:  # 使用新的weeks字段
                # 处理可能包含多个时间段的情况
                time_slots = []
                for part in sksj.split("<br>"):
                    time_slots.extend(part.strip().split("、"))

                # 合并所有时间段的周次
                actual_weeks = set()
                for slot in time_slots:
                    if "周" not in slot:
                        continue
                    weeks_str = slot.split("周")[0].strip()
                    actual_weeks.update(parse_weeks(weeks_str))

                # 检查是否匹配目标周次
                weeks_match = check_weeks_match(course["weeks"], actual_weeks)

            # 确保两个ID都存在且周次匹配
            if jx02id and jx0404id and weeks_match:
                logging.critical(
                    f"找到课程 【{course['course_id_or_name']}-{course['teacher_name']}】 的jx02id: {jx02id} 和 jx0404id: {jx0404id}"
                )
                return {"jx02id": jx02id, "jx0404id": jx0404id}

        logging.warning(f"未找到匹配的课程数据")
        return None

    except Exception as e:
        logging.error(f"查找课程jx02id和jx0404id时发生错误: {str(e)}")
        return None


def get_course_jx02id_and_jx0404id_by_api(course):
    """通过教务系统API获取课程的jx02id和jx0404id"""
    try:
        # 定义最大重试次数
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
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

                # 如果所有请求都成功但没有找到结果，跳出循环
                break

            except Exception as e:
                if "404" in str(e):
                    retry_count += 1
                    if retry_count < max_retries:
                        logging.warning(
                            f"获取课程信息失败(404)，正在进行第{retry_count}次重试..."
                        )
                        continue
                logging.error(f"获取课程的jx02id和jx0404id失败: {e}")

        return None
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
            f"未能找到课程: 【{course['course_id_or_name']}-{course['teacher_name']}】的jx02id和jx0404id"
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
        if response.status_code == 404:
            raise Exception("404 Not Found")
        logging.info(f"获取公选选课页面响应值: {response.status_code}")
        # 打印当前会话的cookie
        logging.debug(f"当前会话的cookie: {get_session().cookies}")
        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk",
            params={
                "kcxx": course_id,
                "skls": teacher_name,
                "skxq": week_day,
                "skjc": class_period,
                "szjylb": "",
                "sfym": "false",
                "sfct": "true",
                "sfxx": "true",
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
        if response.status_code == 404:
            raise Exception("404 Not Found")

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
        # 打印当前会话的cookie
        logging.debug(f"当前会话的cookie: {get_session().cookies}")
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
                "sEcho": "1",
                "iColumns": "12",
                "sColumns": "",
                "iDisplayStart": "0",
                "iDisplayLength": "15",
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "xf",
                "mDataProp_4": "skls",
                "mDataProp_5": "sksj",
                "mDataProp_6": "skdd",
                "mDataProp_7": "xqmc",
                "mDataProp_8": "xkrs",
                "mDataProp_9": "syrs",
                "mDataProp_10": "ctsm",
                "mDataProp_11": "czOper",
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
        # 打印当前会话的cookie
        logging.debug(f"当前会话的cookie: {get_session().cookies}")
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
                "sEcho": "1",
                "iColumns": "12",
                "sColumns": "",
                "iDisplayStart": "0",
                "iDisplayLength": "15",
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "xf",
                "mDataProp_4": "skls",
                "mDataProp_5": "sksj",
                "mDataProp_6": "skdd",
                "mDataProp_7": "xqmc",
                "mDataProp_8": "xkrs",
                "mDataProp_9": "syrs",
                "mDataProp_10": "ctsm",
                "mDataProp_11": "czOper",
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
        # 打印当前会话的cookie
        logging.debug(f"当前会话的cookie: {get_session().cookies}")
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
                "sEcho": "1",
                "iColumns": "12",
                "sColumns": "",
                "iDisplayStart": "0",
                "iDisplayLength": "15",
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "xf",
                "mDataProp_4": "skls",
                "mDataProp_5": "sksj",
                "mDataProp_6": "skdd",
                "mDataProp_7": "xqmc",
                "mDataProp_8": "xkrs",
                "mDataProp_9": "syrs",
                "mDataProp_10": "ctsm",
                "mDataProp_11": "czOper",
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
        # 打印当前会话的cookie
        logging.debug(f"当前会话的cookie: {get_session().cookies}")
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
                "sEcho": "1",
                "iColumns": "12",
                "sColumns": "",
                "iDisplayStart": "0",
                "iDisplayLength": "15",
                "mDataProp_0": "kch",
                "mDataProp_1": "kcmc",
                "mDataProp_2": "fzmc",
                "mDataProp_3": "xf",
                "mDataProp_4": "skls",
                "mDataProp_5": "sksj",
                "mDataProp_6": "skdd",
                "mDataProp_7": "xqmc",
                "mDataProp_8": "xkrs",
                "mDataProp_9": "syrs",
                "mDataProp_10": "ctsm",
                "mDataProp_11": "czOper",
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
