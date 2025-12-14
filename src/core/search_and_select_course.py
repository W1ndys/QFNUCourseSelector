from loguru import logger
from .get_course_capacity import get_course_capacity_by_ids
from .send_course_data import (
    send_ggxxkxkOper_course_jx02id_and_jx0404id,
    send_knjxkOper_course_jx02id_and_jx0404id,
    send_bxqjhxkOper_course_jx02id_and_jx0404id,
    send_xxxkOper_course_jx02id_and_jx0404id,
    send_fawxkOper_course_jx02id_and_jx0404id,
)
from ..utils.feishu import feishu
from ..utils.session_manager import get_session


def search_course_by_params(course_id, teacher_name, skxq, skjc):
    """
    根据课程ID、教师名、星期几、节次范围搜索课程信息

    Args:
        course_id: 课程编号
        teacher_name: 教师姓名
        skxq: 星期几（1-7）
        skjc: 节次范围（如0102, 0304等）

    Returns:
        list: 搜索到的课程列表，每个元素包含课程信息（包括jx02id, jx0404id, zcxqjcList等）
    """
    try:
        session = get_session()

        # 搜索请求URL列表 - 尝试不同的选课类型接口
        search_urls = [
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkXxxk",      # 选修选课
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk",   # 公选课选课
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkKnjxk",     # 专业内跨年级选课
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkBxqjhxk",   # 本学期计划选课
            "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkFawxk",     # 计划外选课
        ]

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        }

        params = {
            "kcxx": course_id,
            "skls": teacher_name,
            "skxq": skxq,
            "skjc": skjc,
            "sfym": "false",
            "sfct": "false",
            "sfxx": "false",
        }

        data = {
            "sEcho": "1",
            "iColumns": "11",
            "sColumns": "",
            "iDisplayStart": "0",
            "iDisplayLength": "50",
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
        }

        all_results = []
        for url in search_urls:
            try:
                response = session.post(url, data=data, headers=headers, params=params)
                if response.status_code == 200:
                    result = response.json()
                    if "aaData" in result and result["aaData"]:
                        logger.info(f"在接口 {url} 找到 {len(result['aaData'])} 个课程")
                        all_results.extend(result["aaData"])
            except Exception as e:
                logger.debug(f"搜索接口 {url} 失败: {str(e)}")
                continue

        return all_results

    except Exception as e:
        logger.error(f"搜索课程失败: {str(e)}")
        return []


def find_course_ids_by_search(course):
    """
    通过搜索功能查找课程的jx02id和jx0404id

    Args:
        course: 课程配置信息，包含:
            - course_id: 课程编号
            - teacher_name: 教师姓名
            - skxq: 星期几
            - skjc: 节次范围
            - first_week: 第一节课所在周次
            - first_xq: 第一节课星期几
            - first_jc: 第一节课节次

    Returns:
        dict: 包含jx02id和jx0404id的字典，如果未找到则返回None
    """
    course_id = course.get("course_id", "")
    teacher_name = course.get("teacher_name", "")
    skxq = course.get("skxq", "").strip()
    skjc = course.get("skjc", "").strip()
    first_week = course.get("first_week", "").strip()
    first_xq = course.get("first_xq", "").strip()
    first_jc = course.get("first_jc", "").strip()

    logger.info(
        f"正在搜索课程: 课程ID={course_id}, 教师={teacher_name}, "
        f"星期={skxq}, 节次范围={skjc}"
    )
    logger.info(
        f"匹配条件: 第一节课周次={first_week}, 星期={first_xq}, 节次={first_jc}"
    )

    # 搜索课程
    search_results = search_course_by_params(course_id, teacher_name, skxq, skjc)

    if not search_results:
        logger.warning(f"未搜索到课程【{course['course_name']}-{teacher_name}】")
        return None

    logger.info(f"搜索到 {len(search_results)} 个候选课程")

    # 遍历搜索结果，根据zcxqjcList匹配
    for result in search_results:
        zcxqjcList = result.get("zcxqjcList", [])

        if not zcxqjcList:
            logger.debug(f"课程 {result.get('kcmc', '未知')} 没有 zcxqjcList 数据")
            continue

        # 获取第一个元组进行匹配
        first_schedule = zcxqjcList[0]
        zc = first_schedule.get("zc", "")  # 周次
        xq = first_schedule.get("xq", "")  # 星期
        jc = first_schedule.get("jc", "")  # 节次

        logger.debug(
            f"比对课程 {result.get('kcmc', '未知')}: "
            f"周次={zc}(期望{first_week}), 星期={xq}(期望{first_xq}), 节次={jc}(期望{first_jc})"
        )

        # 对比第一节课信息
        if str(zc) == str(first_week) and str(xq) == str(first_xq) and str(jc) == str(first_jc):
            jx02id = result.get("jx02id", "")
            jx0404id = result.get("jx0404id", "")

            if jx02id and jx0404id:
                logger.info(
                    f"找到匹配的课程: {result.get('kcmc', '未知')}, "
                    f"jx02id={jx02id}, jx0404id={jx0404id}"
                )
                return {"jx02id": jx02id, "jx0404id": jx0404id}
            else:
                logger.warning(f"课程匹配但缺少jx02id或jx0404id")

    logger.warning(
        f"未找到符合条件的课程【{course['course_name']}-{teacher_name}】\n"
        f"期望第一节课: 周次={first_week}, 星期={first_xq}, 节次={first_jc}"
    )
    return None


def search_and_select_course(course):
    """
    根据配置进行选课：
    1. 如果配置了jx02id和jx0404id，直接发送选课请求
    2. 如果未配置，则通过搜索功能查找后再选课

    Args:
        course (dict): 包含课程信息的字典，必须包含以下键：
            - course_name: 课程名称（用于日志输出）
            - course_id: 课程编号
            - teacher_name: 教师姓名
            - jx02id: 课程jx02id（可选）
            - jx0404id: 课程jx0404id（可选）
            - skxq: 星期几（搜索模式必填）
            - skjc: 节次范围（搜索模式必填）
            - first_week: 第一节课所在周次（搜索模式必填）
            - first_xq: 第一节课星期几（搜索模式必填）
            - first_jc: 第一节课节次（搜索模式必填）

    Returns:
        True: 如果成功选择课程
        False: 如果选课失败（可重试）
        "permanent_failure": 如果遇到永久失败条件（不可重试）
    """
    try:
        logger.info(
            f"开始处理课程: 【{course['course_name']}-{course['teacher_name']}】"
        )

        # 验证基础必填字段
        base_required_keys = ["course_name", "course_id", "teacher_name"]
        if not all(key in course for key in base_required_keys):
            logger.error(f"课程信息缺少必要的字段，需要: {', '.join(base_required_keys)}")
            return False

        # 获取jx02id和jx0404id
        jx02id = course.get("jx02id", "").strip()
        jx0404id = course.get("jx0404id", "").strip()

        # 判断选课模式
        if jx02id and jx0404id:
            # 模式1: 直接使用配置的ID
            logger.info(
                f"使用直接ID模式: jx02id={jx02id}, jx0404id={jx0404id}"
            )
            course_ids = {"jx02id": jx02id, "jx0404id": jx0404id}
        else:
            # 模式2: 通过搜索查找ID
            logger.info("使用搜索模式查找课程ID...")
            course_ids = find_course_ids_by_search(course)

            if not course_ids:
                logger.warning(
                    f"课程【{course['course_name']}-{course['teacher_name']}】搜索未找到匹配的课程ID，稍后重试"
                )
                return False

            jx02id = course_ids["jx02id"]
            jx0404id = course_ids["jx0404id"]

        # 通过jx02id和jx0404id直接查询课程剩余容量信息（仅用于日志记录）
        remaining_capacity = None
        logger.info(
            f"正在通过ID查询课程【{course['course_name']}-{course['teacher_name']}】的剩余容量..."
        )
        course_info = get_course_capacity_by_ids(jx02id, jx0404id)
        if course_info:
            remaining_capacity = course_info.get("xxrs", "未知")
            course_name = course_info.get("kcmc", course["course_name"])
            teacher_name = course_info.get("skls", course["teacher_name"])
            logger.info(
                f"课程信息: 课程名称：{course_name}，剩余容量：{remaining_capacity}，授课老师：{teacher_name}"
            )
        else:
            logger.warning(
                f"无法获取课程【{course['course_name']}-{course['teacher_name']}】的剩余容量信息，将继续选课"
            )

        # 准备选课数据
        course_data = {"jx02id": jx02id, "jx0404id": jx0404id}

        error_messages = []  # 用于收集所有错误信息
        selection_methods = [
            ("专业内跨年级选课", send_knjxkOper_course_jx02id_and_jx0404id),
            ("本学期计划选课", send_bxqjhxkOper_course_jx02id_and_jx0404id),
            ("公选课选课", send_ggxxkxkOper_course_jx02id_and_jx0404id),
            ("选修选课", send_xxxkOper_course_jx02id_and_jx0404id),
            ("计划外选课", send_fawxkOper_course_jx02id_and_jx0404id),
        ]

        # 使用jx02id和jx0404id尝试不同的选课方式
        logger.info(
            f"使用jx02id={jx02id}和jx0404id={jx0404id}进行选课"
        )
        for method_name, method_func in selection_methods:
            result, message = method_func(course["course_id"], course_data)
            if result is True:
                success_message = f"课程【{course['course_name']}-{course['teacher_name']}】选课成功！"
                if remaining_capacity:
                    success_message += f" (选课前剩余容量: {remaining_capacity})"
                feishu("选课成功 🎉 ✨ 🌟 🎊", success_message)
                return True
            elif result == "permanent_failure":
                # 永久失败，停止重试
                permanent_failure_message = f"课程【{course['course_name']}-{course['teacher_name']}】遇到永久失败条件，停止重试。原因: {message}"
                logger.critical(permanent_failure_message)
                feishu("选课永久失败 ⛔", permanent_failure_message)
                return "permanent_failure"
            elif result is False:
                error_messages.append(f"【{method_name}】失败: {message}")
            elif result is None:
                error_messages.append(f"【{method_name}】发生异常: {message}")

        # 如果所有尝试都失败，发送错误汇总
        if error_messages:
            error_summary = (
                f"课程【{course['course_name']}-{course['teacher_name']}】选课失败，遇到以下错误：\n\n"
                + "\n\n".join(error_messages)
            )
            logger.error(error_summary)
        return False

    except Exception as e:
        error_msg = str(e)
        logger.error(f"选课失败: {error_msg}")
        return False
