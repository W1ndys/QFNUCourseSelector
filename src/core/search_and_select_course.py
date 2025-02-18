from src.data.get_course_jx02id_and_jx0404id import get_course_jx02id_and_jx0404id
from src.core.send_course_data import (
    send_ggxxkxkOper_course_jx02id_and_jx0404id,
    send_knjxkOper_course_jx02id_and_jx0404id,
    send_bxqjhxkOper_course_jx02id_and_jx0404id,
    send_xxxkOper_course_jx02id_and_jx0404id,
    send_fawxkOper_course_jx02id_and_jx0404id,
)
from src.utils.dingtalk import dingtalk
from src.utils.feishu import feishu
import logging


def search_and_select_course(course):
    """
    通过依次从公选课选课、本学期计划选课、选修选课、专业内跨年级选课、计划外选课、辅修选课搜索课程

    Args:
        course (dict): 包含课程信息的字典，必须包含以下键：
            - course_id_or_name: 课程编号
            - teacher_name: 教师姓名
        可选键：
            - week_day: 上课星期
            - class_period: 上课节次
            - weeks: 上课周次
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
        if (
            course.get("jx02id")
            and course.get("jx0404id")
            and course["jx02id"].strip() != ""
            and course["jx0404id"].strip() != ""
        ):
            logging.critical(f"已手动配置jx02id和jx0404id，跳过搜索直接选课: {course}")

            # 依次尝试不同的选课方式
            selection_methods = [
                ("专业内跨年级选课", send_knjxkOper_course_jx02id_and_jx0404id),
                ("本学期计划选课", send_bxqjhxkOper_course_jx02id_and_jx0404id),
                ("公选课选课", send_ggxxkxkOper_course_jx02id_and_jx0404id),
                ("选修选课", send_xxxkOper_course_jx02id_and_jx0404id),
                ("计划外选课", send_fawxkOper_course_jx02id_and_jx0404id),
            ]

            for method_name, method_func in selection_methods:
                result, message = method_func(course["course_id_or_name"], course)
                if result is True:
                    dingtalk(
                        "选课成功 🎉 ✨ 🌟 🎊",
                        f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课成功！",
                    )
                    feishu(
                        "选课成功 🎉 ✨ 🌟 🎊",
                        f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课成功！",
                    )
                    return True
                elif result is False:
                    error_messages.append(f"【{method_name}】失败: {message}")
                elif result is None:
                    error_messages.append(f"【{method_name}】发生异常: {message}")

        # 未手动配置jx02id和jx0404id的情况
        else:
            logging.critical(f"未手动配置jx02id和jx0404id，开始搜索课程: {course}")
            # 检查class_period和week_day是否填写
            if course.get("class_period") is None or course.get("week_day") is None:
                logging.error(
                    f"【{course['course_id_or_name']}-{course['teacher_name']}】的课程信息缺少必要的字段，需要: {', '.join(required_keys)}"
                )
                return False
            course_jx02id_and_jx0404id = get_course_jx02id_and_jx0404id(course)
            if course_jx02id_and_jx0404id:
                selection_methods = [
                    ("专业内跨年级选课", send_knjxkOper_course_jx02id_and_jx0404id),
                    ("本学期计划选课", send_bxqjhxkOper_course_jx02id_and_jx0404id),
                    ("公选课选课", send_ggxxkxkOper_course_jx02id_and_jx0404id),
                    ("选修选课", send_xxxkOper_course_jx02id_and_jx0404id),
                    ("计划外选课", send_fawxkOper_course_jx02id_and_jx0404id),
                ]

                for method_name, method_func in selection_methods:
                    result, message = method_func(
                        course["course_id_or_name"], course_jx02id_and_jx0404id
                    )
                    if result is True:
                        dingtalk(
                            "选课成功 🎉 ✨ 🌟 🎊",
                            f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课成功！",
                        )
                        feishu(
                            "选课成功 🎉 ✨ 🌟 🎊",
                            f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课成功！",
                        )
                        return True
                    elif result is False:
                        error_messages.append(f"【{method_name}】失败: {message}")
                    elif result is None:
                        error_messages.append(f"【{method_name}】发生异常: {message}")

        # 如果所有尝试都失败，发送错误汇总
        if error_messages:
            error_summary = (
                f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课失败，遇到以下错误：\n\n"
                + "\n\n".join(error_messages)
            )
            dingtalk("选课失败 😭 😢 😔", error_summary)
            feishu("选课失败 😭 😢 😔", error_summary)
        return False

    except Exception as e:
        error_msg = str(e)
        logging.error(f"搜索选课失败: {error_msg}")
        dingtalk(
            "选课失败 😭 😢 😔",
            f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课过程发生异常：{error_msg}",
        )
        feishu(
            "选课失败 😭 😢 😔",
            f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课过程发生异常：{error_msg}",
        )
        return False
