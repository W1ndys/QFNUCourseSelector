from src.data.get_course_capacity import get_course_capacity_by_ids
from src.core.send_course_data import (
    send_ggxxkxkOper_course_jx02id_and_jx0404id,
    send_knjxkOper_course_jx02id_and_jx0404id,
    send_bxqjhxkOper_course_jx02id_and_jx0404id,
    send_xxxkOper_course_jx02id_and_jx0404id,
    send_fawxkOper_course_jx02id_and_jx0404id,
)
from src.utils.feishu import feishu
import logging


def search_and_select_course(course):
    """
    使用配置的jx02id和jx0404id直接进行选课请求
    通过ID查询课程剩余容量信息

    Args:
        course (dict): 包含课程信息的字典，必须包含以下键：
            - course_id_or_name: 课程编号（用于日志输出）
            - teacher_name: 教师姓名（用于日志输出）
            - jx02id: 课程jx02id（必填，用于选课请求和查询剩余量）
            - jx0404id: 课程jx0404id（必填，用于选课请求和查询剩余量）

    Returns:
        bool: 如果成功选择课程返回True，否则返回False
    """
    try:
        logging.info(f"开始处理课程: 【{course['course_id_or_name']}-{course['teacher_name']}】")
        
        # 验证必填字段
        required_keys = ["course_id_or_name", "teacher_name", "jx02id", "jx0404id"]
        if not all(key in course for key in required_keys):
            logging.error(f"课程信息缺少必要的字段，需要: {', '.join(required_keys)}")
            return False

        # 验证jx02id和jx0404id不为空
        if not course["jx02id"].strip() or not course["jx0404id"].strip():
            logging.error(
                f"课程【{course['course_id_or_name']}-{course['teacher_name']}】的jx02id或jx0404id为空，请检查配置文件"
            )
            return False

        # 通过jx02id和jx0404id直接查询课程剩余容量信息（仅用于日志记录）
        remaining_capacity = None
        logging.info(f"正在通过ID查询课程【{course['course_id_or_name']}-{course['teacher_name']}】的剩余容量...")
        course_info = get_course_capacity_by_ids(course["jx02id"], course["jx0404id"])
        if course_info:
            remaining_capacity = course_info.get("xxrs", "未知")
            course_name = course_info.get("kcmc", course["course_id_or_name"])
            teacher_name = course_info.get("skls", course["teacher_name"])
            logging.info(
                f"课程信息: 课程名称：{course_name}，剩余容量：{remaining_capacity}，授课老师：{teacher_name}"
            )
        else:
            logging.warning(
                f"无法获取课程【{course['course_id_or_name']}-{course['teacher_name']}】的剩余容量信息，将继续选课"
            )

        # 准备选课数据
        course_data = {
            "jx02id": course["jx02id"],
            "jx0404id": course["jx0404id"]
        }

        error_messages = []  # 用于收集所有错误信息
        selection_methods = [
            ("专业内跨年级选课", send_knjxkOper_course_jx02id_and_jx0404id),
            ("本学期计划选课", send_bxqjhxkOper_course_jx02id_and_jx0404id),
            ("公选课选课", send_ggxxkxkOper_course_jx02id_and_jx0404id),
            ("选修选课", send_xxxkOper_course_jx02id_and_jx0404id),
            ("计划外选课", send_fawxkOper_course_jx02id_and_jx0404id),
        ]

        # 使用配置的jx02id和jx0404id直接尝试不同的选课方式
        logging.info(f"使用配置的jx02id={course['jx02id']}和jx0404id={course['jx0404id']}直接选课")
        for method_name, method_func in selection_methods:
            result, message = method_func(course["course_id_or_name"], course_data)
            if result is True:
                success_message = f"课程【{course['course_id_or_name']}-{course['teacher_name']}】选课成功！"
                if remaining_capacity:
                    success_message += f" (选课前剩余容量: {remaining_capacity})"
                feishu("选课成功 🎉 ✨ 🌟 🎊", success_message)
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
            logging.error(error_summary)
        return False

    except Exception as e:
        error_msg = str(e)
        logging.error(f"选课失败: {error_msg}")
        return False
