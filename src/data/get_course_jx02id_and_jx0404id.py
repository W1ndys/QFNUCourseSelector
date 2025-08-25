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

        # 检查是否存在需要同时选择讲课学时和实验学时的情况
        # 查找同一个课程号、同一个老师的多个课程记录
        matching_courses = []
        for data in course_data:
            if (
                data.get("kch") == course["course_id_or_name"]
                or data.get("kcmc") == course["course_id_or_name"]
            ) and data.get("skls") == course["teacher_name"]:
                matching_courses.append(data)

        # 如果找到多个匹配的课程，检查是否包含讲课学时和实验学时
        if len(matching_courses) > 1:
            lecture_course = None
            lab_course = None

            # 分离讲课学时和实验学时课程
            lecture_courses = []
            lab_courses = []

            # 增加标记集合
            lecture_markers = ("[讲课学时]",)
            lab_markers = ("[实验学时]", "[实践学时]")

            for data in matching_courses:
                course_name = data.get("kcmc", "")
                if any(marker in course_name for marker in lecture_markers):
                    lecture_courses.append(data)
                elif any(marker in course_name for marker in lab_markers):
                    lab_courses.append(data)

            # 选择讲课学时课程（优先使用配置中的偏好时间）
            if lecture_courses:
                if len(lecture_courses) == 1:
                    lecture_course = lecture_courses[0]
                else:
                    # 如果有多个讲课学时，优先选择符合配置偏好的
                    lecture_course = select_best_course(
                        lecture_courses, course, "lecture"
                    )

            # 选择实验学时课程（优先使用配置中的偏好时间）
            if lab_courses:
                if len(lab_courses) == 1:
                    lab_course = lab_courses[0]
                else:
                    # 如果有多个实验学时，优先选择符合配置偏好的
                    lab_course = select_best_course(lab_courses, course, "lab")

            # 如果同时找到讲课学时和实验学时，返回组合信息
            if lecture_course and lab_course:
                logging.critical(
                    f"发现需要同时选择的课程：【{course['course_id_or_name']}-{course['teacher_name']}】"
                    f"讲课学时: {lecture_course.get('jx02id')}-{lecture_course.get('jx0404id')}, "
                    f"实验学时: {lab_course.get('jx02id')}-{lab_course.get('jx0404id')}"
                )
                return {
                    "jx02id": lecture_course.get("jx02id"),
                    "jx0404id": lecture_course.get("jx0404id"),
                    "xxrs": lecture_course.get("xxrs"),
                    "skls": lecture_course.get("skls"),
                    "kcmc": lecture_course.get("kcmc"),
                    "needs_both": True,
                    "lecture_course": {
                        "jx02id": lecture_course.get("jx02id"),
                        "jx0404id": lecture_course.get("jx0404id"),
                        "cfbs": lecture_course.get("cfbs", "1"),
                    },
                    "lab_course": {
                        "jx02id": lab_course.get("jx02id"),
                        "jx0404id": lab_course.get("jx0404id"),
                        "cfbs": lab_course.get("cfbs", "4"),
                    },
                }

        # 如果只有一组数据，检查是否需要强制搜索组合课程
        if len(course_data) == 1:
            data = course_data[0]
            course_name = data.get("kcmc", "")

            # 如果课程名称包含[讲课学时]或[实验学时]，说明可能需要同时选课
            # 此时不要直接返回，而是标记需要进一步搜索
            if (
                ("[讲课学时]" in course_name)
                or ("[实验学时]" in course_name)
                or ("[实践学时]" in course_name)
            ):
                logging.info(
                    f"发现可能需要同时选课的课程：【{course['course_id_or_name']}-{course['teacher_name']}】，"
                    f"但当前搜索结果只有一条记录，标记需要进一步搜索"
                )
                return {"needs_further_search": True, "current_course": data}

            # 如果课程名称不包含学时标识，按原来的逻辑处理
            if (
                data.get("kch") == course["course_id_or_name"]
                or data.get("kcmc") == course["course_id_or_name"]
            ) and data.get("skls") == course["teacher_name"]:
                jx02id = data.get("jx02id")
                jx0404id = data.get("jx0404id")
                xxrs_value = data["xxrs"]
                skls_value = data["skls"]
                kcmc_value = data["kcmc"]
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
                        "needs_both": False,
                    }

        # 处理周次信息
        def parse_weeks(weeks_str):
            weeks = set()
            if not weeks_str:
                return weeks

            # 处理常见的周次格式
            if "周" in weeks_str:
                weeks_str = weeks_str.split("周")[0]

            # 处理范围格式，如 "1-18"
            if "-" in weeks_str:
                try:
                    start, end = map(int, weeks_str.split("-"))
                    weeks.update(range(start, end + 1))
                except ValueError:
                    pass
            # 处理单个数字
            elif weeks_str.isdigit():
                weeks.add(int(weeks_str))
            # 处理逗号分隔的格式，如 "1,3,5"
            elif "," in weeks_str:
                try:
                    for week in weeks_str.split(","):
                        if week.strip().isdigit():
                            weeks.add(int(week.strip()))
                except ValueError:
                    pass

            return weeks

        def check_weeks_match(target_weeks, actual_weeks):
            if not target_weeks or not actual_weeks:
                return True

            target_set = set(target_weeks)
            actual_set = set(actual_weeks)

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
                return {"jx02id": jx02id, "jx0404id": jx0404id, "needs_both": False}

        logging.warning(f"未找到匹配的课程数据")
        return None

    except Exception as e:
        logging.error(f"查找课程jx02id和jx0404id时发生错误: {str(e)}")
        return None


def select_best_course(courses, course_config, course_type):
    """选择最佳的课程（基于配置偏好）"""
    if not courses:
        return None

    if len(courses) == 1:
        return courses[0]

    # 获取偏好设置
    if course_type == "lecture":
        # 讲课学时使用主要配置
        preferred_week_day = course_config.get("week_day")
        preferred_weeks = course_config.get("weeks")
        preferred_class_period = course_config.get("class_period")
    else:
        # 实验学时使用lab_preference配置
        lab_pref = course_config.get("lab_preference", {})
        preferred_week_day = lab_pref.get("week_day")
        preferred_weeks = lab_pref.get("weeks")
        preferred_class_period = lab_pref.get("class_period")

    # 计算每个课程的匹配分数
    best_course = None
    best_score = -1

    for course in courses:
        score = 0
        sksj = course.get("sksj", "")

        # 检查星期匹配
        if preferred_week_day and preferred_week_day in sksj:
            score += 10

        # 检查节次匹配
        if preferred_class_period and preferred_class_period in sksj:
            score += 10

        # 检查周次匹配
        if preferred_weeks and "周" in sksj:
            try:
                # 解析配置中的周次
                config_weeks = parse_weeks(preferred_weeks)
                # 解析课程中的周次
                course_weeks = parse_weeks(sksj)
                # 计算重叠程度
                overlap = len(config_weeks.intersection(course_weeks))
                if overlap > 0:
                    score += overlap
            except:
                pass

        # 如果分数更高，更新最佳课程
        if score > best_score:
            best_score = score
            best_course = course

    # 如果没有找到匹配的，返回第一个
    return best_course if best_course else courses[0]


def parse_weeks(weeks_str):
    """解析周次字符串"""
    weeks = set()
    if not weeks_str:
        return weeks

    # 处理常见的周次格式
    if "周" in weeks_str:
        weeks_str = weeks_str.split("周")[0]

    # 处理范围格式，如 "1-18"
    if "-" in weeks_str:
        try:
            start, end = map(int, weeks_str.split("-"))
            weeks.update(range(start, end + 1))
        except ValueError:
            pass
    # 处理单个数字
    elif weeks_str.isdigit():
        weeks.add(int(weeks_str))
    # 处理逗号分隔的格式，如 "1,3,5"
    elif "," in weeks_str:
        try:
            for week in weeks_str.split(","):
                if week.strip().isdigit():
                    weeks.add(int(week.strip()))
        except ValueError:
            pass

    return weeks


def get_course_jx02id_and_jx0404id_by_api(course):
    """通过教务系统API获取课程的jx02id和jx0404id"""
    try:
        # 定义最大重试次数
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 首先尝试精确搜索（使用时间限制）
                result = get_course_jx02id_and_jx0404id_xsxkKnjxk_by_api(course)
                if result:
                    result = find_course_jx02id_and_jx0404id(course, result["aaData"])
                    if result:
                        # 检查是否需要进一步搜索
                        if result.get("needs_further_search"):
                            logging.info(f"需要进一步搜索组合课程，跳过精确搜索结果")
                        else:
                            return result

                result = get_course_jx02id_and_jx0404id_xsxkBxqjhxk_by_api(course)
                if result:
                    result = find_course_jx02id_and_jx0404id(course, result["aaData"])
                    if result:
                        if result.get("needs_further_search"):
                            logging.info(f"需要进一步搜索组合课程，跳过精确搜索结果")
                        else:
                            return result

                result = get_course_jx02id_and_jx0404id_xsxkXxxk_by_api(course)
                if result:
                    result = find_course_jx02id_and_jx0404id(course, result["aaData"])
                    if result:
                        if result.get("needs_further_search"):
                            logging.info(f"需要进一步搜索组合课程，跳过精确搜索结果")
                        else:
                            return result

                result = get_course_jx02id_and_jx0404id_xsxkGgxxkxk_by_api(course)
                if result:
                    result = find_course_jx02id_and_jx0404id(course, result["aaData"])
                    if result:
                        if result.get("needs_further_search"):
                            logging.info(f"需要进一步搜索组合课程，跳过精确搜索结果")
                        else:
                            return result

                result = get_course_jx02id_and_jx0404id_xsxkFawxk_by_api(course)
                if result:
                    result = find_course_jx02id_and_jx0404id(course, result["aaData"])
                    if result:
                        if result.get("needs_further_search"):
                            logging.info(f"需要进一步搜索组合课程，跳过精确搜索结果")
                        else:
                            return result

                # 如果精确搜索没有找到，或者标记需要进一步搜索，尝试无时间限制搜索
                if (
                    course.get("week_day")
                    or course.get("weeks")
                    or course.get("class_period")
                ):
                    logging.info(f"尝试无时间限制搜索: {course['course_id_or_name']}")

                    # 创建无时间限制的搜索参数
                    course_no_time = {
                        "course_id_or_name": course["course_id_or_name"],
                        "teacher_name": course["teacher_name"],
                    }

                    # 重新尝试无时间限制搜索
                    result = get_course_jx02id_and_jx0404id_xsxkKnjxk_by_api(
                        course_no_time
                    )
                    if result:
                        result = find_course_jx02id_and_jx0404id(
                            course, result["aaData"]
                        )
                        if result:
                            return result

                    result = get_course_jx02id_and_jx0404id_xsxkBxqjhxk_by_api(
                        course_no_time
                    )
                    if result:
                        result = find_course_jx02id_and_jx0404id(
                            course, result["aaData"]
                        )
                        if result:
                            return result

                    result = get_course_jx02id_and_jx0404id_xsxkXxxk_by_api(
                        course_no_time
                    )
                    if result:
                        result = find_course_jx02id_and_jx0404id(
                            course, result["aaData"]
                        )
                        if result:
                            return result

                    result = get_course_jx02id_and_jx0404id_xsxkGgxxkxk_by_api(
                        course_no_time
                    )
                    if result:
                        result = find_course_jx02id_and_jx0404id(
                            course, result["aaData"]
                        )
                        if result:
                            return result

                    result = get_course_jx02id_and_jx0404id_xsxkFawxk_by_api(
                        course_no_time
                    )
                    if result:
                        result = find_course_jx02id_and_jx0404id(
                            course, result["aaData"]
                        )
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

        # 只有当配置了时间信息时才使用时间参数
        class_period = course.get("class_period", "")
        week_day = course.get("week_day", "")

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
        )
        if response.status_code == 404:
            raise Exception("404 Not Found")
        logging.info(f"获取公选选课页面响应值: {response.status_code}")

        # 构建搜索参数
        search_params = {
            "kcxx": course_id,
            "skls": teacher_name,
            "szjylb": "",
            "sfym": "false",
            "sfct": "true",
            "sfxx": "true",
        }

        # 只有当配置了时间信息时才添加时间参数
        if week_day:
            search_params["skxq"] = week_day
        if class_period:
            search_params["skjc"] = class_period

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk",
            params=search_params,
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

        # 只有当配置了时间信息时才使用时间参数
        class_period = course.get("class_period", "")
        week_day = course.get("week_day", "")

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
        )
        logging.info(f"获取选修选课页面响应值: {response.status_code}")

        # 构建搜索参数
        search_params = {
            "kcxx": course_id,  # 课程名称
            "skls": teacher_name,  # 教师姓名
            "sfym": "false",  # 是否已满
            "sfct": "false",  # 是否冲突
            "sfxx": "false",  # 是否限选
        }

        # 只有当配置了时间信息时才添加时间参数
        if week_day:
            search_params["skxq"] = week_day
        if class_period:
            search_params["skjc"] = class_period

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkXxxk",
            params=search_params,
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

        # 只有当配置了时间信息时才使用时间参数
        class_period = course.get("class_period", "")
        week_day = course.get("week_day", "")

        # 选修选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk",
        )
        logging.info(f"获取本学期计划选课页面响应值: {response.status_code}")

        # 构建搜索参数
        search_params = {
            "kcxx": course_id,  # 课程名称
            "skls": teacher_name,  # 教师姓名
            "sfym": "false",  # 是否已满
            "sfct": "false",  # 是否冲突
            "sfxx": "false",  # 是否限选
        }

        # 只有当配置了时间信息时才添加时间参数
        if week_day:
            search_params["skxq"] = week_day
        if class_period:
            search_params["skjc"] = class_period

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkBxqjhxk",
            params=search_params,
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

        # 只有当配置了时间信息时才使用时间参数
        class_period = course.get("class_period", "")
        week_day = course.get("week_day", "")

        # 专业内跨年级选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInKnjxk",
        )
        if response.status_code == 404:
            raise Exception("404 Not Found")
        logging.info(f"获取专业内跨年级选课页面响应值: {response.status_code}")

        # 构建搜索参数
        search_params = {
            "kcxx": course_id,
            "skls": teacher_name,
            "sfym": "false",
            "sfct": "false",
            "sfxx": "false",
        }

        # 只有当配置了时间信息时才添加时间参数
        if week_day:
            search_params["skxq"] = week_day
        if class_period:
            search_params["skjc"] = class_period

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkKnjxk",
            params=search_params,
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

        if response.status_code == 404:
            raise Exception("404 Not Found")

        logging.info(f"获取专业内跨年级选课列表数据响应值: {response.status_code}")
        response_data = json.loads(response.text)

        # 检查aaData是否为空
        if not response_data.get("aaData"):
            logging.warning(
                "专业内跨年级选课的API返回的aaData为空，可能该课程不在该分类"
            )
            return None

        return response_data
    except Exception as e:
        logging.error(f"获取专业内跨年级选课的jx02id和jx0404id失败: {e}")
        return None


def get_course_jx02id_and_jx0404id_xsxkFawxk_by_api(course):
    """通过教务系统API获取计划外选课课程的jx02id和jx0404id"""
    try:
        session = get_session()
        course_id = course["course_id_or_name"]
        teacher_name = course["teacher_name"]

        # 只有当配置了时间信息时才使用时间参数
        class_period = course.get("class_period", "")
        week_day = course.get("week_day", "")

        # 计划外选课页面
        response = session.get(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk",
        )
        logging.info(f"获取计划外选课页面响应值: {response.status_code}")

        # 构建搜索参数
        search_params = {
            "kcxx": course_id,  # 课程名称
            "skls": teacher_name,  # 教师姓名
            "sfym": "false",  # 是否已满
            "sfct": "false",  # 是否冲突
            "sfxx": "false",  # 是否限选
        }

        # 只有当配置了时间信息时才添加时间参数
        if week_day:
            search_params["skxq"] = week_day
        if class_period:
            search_params["skjc"] = class_period

        # 请求选课列表数据
        response = session.post(
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkFawxk",
            params=search_params,
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
