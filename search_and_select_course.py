from get_course_data import get_course_jx02id_and_jx0404id
from send_course_data import (
    send_ggxxkxkOper_course_data,
    send_knjxkOper_course_data,
    send_bxqjhxkOper_course_data,
    send_xxxkOper_course_data,
    send_fawxkOper_course_data,
)
import logging


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
        # 只检查必需的键
        required_keys = ["course_id_or_name", "teacher_name"]
        if not all(key in course for key in required_keys):
            logging.error(f"课程信息缺少必要的字段，需要: {', '.join(required_keys)}")
            return False

        # 已手动配置jx02id和jx0404id，直接跳过搜索
        if course.get("jx02id") and course.get("jx0404id"):
            logging.info(f"已手动配置jx02id和jx0404id，跳过搜索直接选课: {course}")
            # 依次尝试不同的选课方式，直到成功
            # 优先选择本学期计划选课
            if send_bxqjhxkOper_course_data(course["course_id_or_name"], course):
                return True
            # 再尝试专业内跨年级选课
            if send_knjxkOper_course_data(course["course_id_or_name"], course):
                return True
            # 再尝试公选课选课请求
            if send_ggxxkxkOper_course_data(course["course_id_or_name"], course):
                return True
            # 再尝试选修选课
            if send_xxxkOper_course_data(course["course_id_or_name"], course):
                return True
            # 最后尝试计划外选课
            if send_fawxkOper_course_data(course["course_id_or_name"], course):
                return True
            # 如果所有尝试都失败，则返回False
            return False

        course_id_or_name = course.get("course_id_or_name", "")
        teacher_name = course.get("teacher_name", "")
        week_day = course.get("week_day", "")
        class_period = course.get("class_period", "")
        course_time = course.get("course_time", "")

        # 寻找课程的jx02id和jx0404id
        course_jx02id_and_jx0404id = get_course_jx02id_and_jx0404id(course)

        if course_jx02id_and_jx0404id:
            # 依次尝试不同的选课方式，直到成功
            # 优先选择本学期计划选课
            if send_bxqjhxkOper_course_data(
                course_id_or_name, course_jx02id_and_jx0404id
            ):
                return True
            # 再尝试专业内跨年级选课
            if send_knjxkOper_course_data(
                course_id_or_name, course_jx02id_and_jx0404id
            ):
                return True
            # 再尝试公选课选课请求
            if send_ggxxkxkOper_course_data(
                course_id_or_name, course_jx02id_and_jx0404id
            ):
                return True
            # 再尝试选修选课
            if send_xxxkOper_course_data(course_id_or_name, course_jx02id_and_jx0404id):
                return True
            # 最后尝试计划外选课
            if send_fawxkOper_course_data(
                course_id_or_name, course_jx02id_and_jx0404id
            ):
                return True
            # 如果所有尝试都失败，则返回False
            return False
        else:
            logging.error(f"未找到{course_id_or_name}的jx02id和jx0404id")
            return False

    except Exception as e:
        logging.error(f"搜索选课失败: {e}")
        return False
