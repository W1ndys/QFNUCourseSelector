from src.data.get_course_jx02id_and_jx0404id import get_course_jx02id_and_jx0404id
from src.core.send_course_data import (
    send_ggxxkxkOper_course_data,
    send_knjxkOper_course_data,
    send_bxqjhxkOper_course_data,
    send_xxxkOper_course_data,
    send_fawxkOper_course_data,
)
import logging
from src.utils.dingtalk import dingtalk


def find_course_data(response, course):
    """
    从响应数据中查找指定课程的jx02id和jx0404id

    Args:
        response: 课程信息响应数据
        course: 要查找的课程信息字典

    Returns:
        dict: 包含jx02id和jx0404id的字典，如果未找到则返回None
    """
    for course_item in response:
        if (
            course_item["kch"] == course["course_id_or_name"]
            and course_item["skls"] == course["teacher_name"]
            and course_item["sksj"].replace("&nbsp;", "") == course["course_time"]
        ):
            return {
                "jx02id": course_item["jx02id"],
                "jx0404id": course_item["jx0404id"],
            }
    return None


def search_and_select_course(course):
    """
    通过依次从公选课选课、本学期计划选课、选修选课、专业内跨年级选课、计划外选课、辅修选课搜索课程

    Args:
        course (dict): 包含课程信息的字典，必须包含以下键：
            - course_id_or_name: 课程编号
            - teacher_name: 教师姓名
        可选键：
            - week_day: 上课星期
            - class_period: 上课时间
            - course_time: 完整的课程时间信息
            - jx02id: 课程jx02id
            - jx0404id: 课程jx0404id

    Returns:
        bool: 如果成功找到并选择课程返回True，否则返回False
    """
    try:
        logging.info(f"开始搜索课程: {course}")
        required_keys = ["course_id_or_name", "teacher_name"]
        if not all(key in course for key in required_keys):
            logging.error(f"课程信息缺少必要的字段，需要: {', '.join(required_keys)}")
            return False

        error_messages = []  # 用于收集所有错误信息

        # 已手动配置jx02id和jx0404id的情况
        if course.get("jx02id") is not None and course.get("jx0404id") is not None:
            logging.info(f"已手动配置jx02id和jx0404id，跳过搜索直接选课: {course}")

            # 依次尝试不同的选课方式
            selection_methods = [
                ("专业内跨年级选课", send_knjxkOper_course_data),
                ("本学期计划选课", send_bxqjhxkOper_course_data),
                ("公选课选课", send_ggxxkxkOper_course_data),
                ("选修选课", send_xxxkOper_course_data),
                ("计划外选课", send_fawxkOper_course_data),
            ]

            for method_name, method_func in selection_methods:
                result, message = method_func(course["course_id_or_name"], course)
                if result is True:
                    dingtalk(
                        "选课成功 🎉 ✨ 🌟 🎊",
                        f"课程【{course['course_id_or_name']}】选课成功！",
                    )
                    return True
                elif result is False:
                    error_messages.append(f"【{method_name}】失败: {message}")
                elif result is None:
                    error_messages.append(f"【{method_name}】发生异常: {message}")

        # 未手动配置jx02id和jx0404id的情况
        else:
            course_jx02id_and_jx0404id = get_course_jx02id_and_jx0404id(course)
            if course_jx02id_and_jx0404id:
                selection_methods = [
                    ("专业内跨年级选课", send_knjxkOper_course_data),
                    ("本学期计划选课", send_bxqjhxkOper_course_data),
                    ("公选课选课", send_ggxxkxkOper_course_data),
                    ("选修选课", send_xxxkOper_course_data),
                    ("计划外选课", send_fawxkOper_course_data),
                ]

                for method_name, method_func in selection_methods:
                    result, message = method_func(
                        course["course_id_or_name"], course_jx02id_and_jx0404id
                    )
                    if result is True:
                        dingtalk(
                            "选课成功 🎉 ✨ 🌟 🎊",
                            f"课程【{course['course_id_or_name']}】选课成功！",
                        )
                        return True
                    elif result is False:
                        error_messages.append(f"【{method_name}】失败: {message}")
                    elif result is None:
                        error_messages.append(f"【{method_name}】发生异常: {message}")

        # 如果所有尝试都失败，发送错误汇总
        if error_messages:
            error_summary = (
                f"课程【{course['course_id_or_name']}】选课失败，遇到以下错误：\n\n"
                + "\n\n".join(error_messages)
            )
            dingtalk("选课失败 😭 😢 😔", error_summary)
        return False

    except Exception as e:
        error_msg = str(e)
        logging.error(f"搜索选课失败: {error_msg}")
        dingtalk(
            "选课失败 😭 😢 😔",
            f"课程【{course['course_id_or_name']}】选课过程发生异常：{error_msg}",
        )
        return False
