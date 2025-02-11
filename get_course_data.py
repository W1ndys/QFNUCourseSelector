import os
import logging
import json
def get_xsxkGgxxkxk_course_info(course):
    try:
        xsxkGgxxkxk_json_path = os.path.join(
            os.path.dirname(__file__), "course_data", "xsxkGgxxkxk_course_info.json"
        )
        with open(xsxkGgxxkxk_json_path, "r", encoding="utf-8") as file:
            xsxkGgxxkxk_json_data = json.load(file)
        for course_item in xsxkGgxxkxk_json_data["aaData"]:
            if (
                course_item["kch"] == course["course_id"]
                and course_item["skls"] == course["teacher_name"]
                and course_item["sksj"].replace("&nbsp;", "") == course["course_time"]
            ):
                course_data = {
                    "jx02id": course_item["jx02id"],
                    "jx0404id": course_item["jx0404id"],
                }

                if course_data["jx02id"] and course_data["jx0404id"]:
                    logging.info(
                        f"找到课程: {course['course_id']}的jx02id: {course_data['jx02id']}, jx0404id: {course_data['jx0404id']}"
                    )
                    return course_data

    except Exception as e:
        logging.error(f"获取公选课选课页面数据失败: {e}")
        return None
