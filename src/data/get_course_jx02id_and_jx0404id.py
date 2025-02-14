import os
import logging
import json

# 添加一个全局缓存字典
course_cache = {}
# 添加一个全局变量用于缓存整个文件数据
all_courses_data_cache = None


def get_course_jx02id_and_jx0404id(course):
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

        for course_item in all_courses_data_cache["aaData"]:
            if (
                course_item["kch"] == course["course_id_or_name"]
                and course_item["skls"] == course["teacher_name"]
                and course_item["sksj"].replace("&nbsp;", "").replace(" ", "")
                == course["course_time"].replace(" ", "")
            ):
                course_jx02id_and_jx0404id = {
                    "jx02id": course_item["jx02id"],
                    "jx0404id": course_item["jx0404id"],
                }

                if (
                    course_jx02id_and_jx0404id["jx02id"]
                    and course_jx02id_and_jx0404id["jx0404id"]
                ):
                    logging.info(
                        f"找到课程: {course['course_id_or_name']}的jx02id: {course_jx02id_and_jx0404id['jx02id']}, jx0404id: {course_jx02id_and_jx0404id['jx0404id']}"
                    )
                    # 将结果存入缓存
                    course_cache[cache_key] = course_jx02id_and_jx0404id
                    return course_jx02id_and_jx0404id

    except Exception as e:
        logging.error(f"获取公选课选课页面数据失败: {e}")
        return None
