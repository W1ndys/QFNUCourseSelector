import time
import logging
from src.utils.session_manager import get_session


def send_ggxxkxkOper_course_jx02id_and_jx0404id(
    course_name, course_jx02id_and_jx0404id
):
    """发送公选课选课请求"""
    try:
        session = get_session()

        # 检查是否需要同时选择讲课学时和实验学时
        if course_jx02id_and_jx0404id.get("needs_both", False):
            logging.info(f"【{course_name}】需要同时选择讲课学时和实验学时")

            # 首先选择讲课学时
            lecture_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/ggxxkxkOper"
            lecture_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "cfbs": course_jx02id_and_jx0404id["lecture_course"]["cfbs"],
                "jx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "xkzy": "",
                "trjf": "",
                "_": str(int(time.time() * 1000)),
            }
            lecture_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInGgxxkxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            lecture_response = session.get(
                lecture_url, params=lecture_params, headers=lecture_headers
            )
            lecture_response_json = lecture_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时的公选课选课请求, 响应代码: {lecture_response.status_code}，响应内容: {lecture_response_json}"
            )

            # 检查讲课学时选课结果
            if "flag1" in lecture_response_json:
                if lecture_response_json["flag1"] == 3:
                    message = lecture_response_json.get("msgContent", "未知原因")
                    logging.warning(f"讲课学时选课登录状态异常: {message}")
                    return None, message
                elif lecture_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时选课成功")
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时选课失败: {lecture_response_json}"
                    )
                    return False, str(lecture_response_json)
            elif "success" in lecture_response_json:
                message = lecture_response_json.get("message", "未知原因")
                if isinstance(lecture_response_json["success"], list):
                    success = all(lecture_response_json["success"])
                else:
                    success = lecture_response_json["success"]

                if success:
                    logging.info(f"【{course_name}】讲课学时选课成功: {message}")
                else:
                    logging.warning(f"【{course_name}】讲课学时选课失败: {message}")
                    return False, message

            # 然后同时选择讲课学时和实验学时
            combined_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/ggxxkxkOper"
            combined_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "yxjx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "jx0404id": course_jx02id_and_jx0404id["lab_course"]["jx0404id"],
                "_": str(int(time.time() * 1000)),
            }
            combined_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInGgxxkxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            combined_response = session.get(
                combined_url, params=combined_params, headers=combined_headers
            )
            combined_response_json = combined_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时+实验学时的公选课选课请求, 响应代码: {combined_response.status_code}，响应内容: {combined_response_json}"
            )

            # 检查最终选课结果
            if "flag1" in combined_response_json:
                if combined_response_json["flag1"] == 3:
                    message = combined_response_json.get("msgContent", "未知原因")
                    logging.warning(f"最终选课登录状态异常: {message}")
                    return None, message
                elif combined_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时+实验学时选课成功")
                    return True, None
            elif "success" in combined_response_json:
                message = combined_response_json.get("message", "未知原因")
                if isinstance(combined_response_json["success"], list):
                    success = all(combined_response_json["success"])
                else:
                    success = combined_response_json["success"]

                if success:
                    logging.info(
                        f"【{course_name}】讲课学时+实验学时选课成功: {message}"
                    )
                    return True, None
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时+实验学时选课失败: {message}"
                    )
                    return False, message

            logging.warning(
                f"【{course_name}】讲课学时+实验学时选课失败: {combined_response_json}"
            )
            return False, str(combined_response_json)

        # 原有的单课程选课逻辑
        url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/ggxxkxkOper"
        params = {
            "kcid": course_jx02id_and_jx0404id["jx02id"],
            "cfbs": "null",
            "jx0404id": course_jx02id_and_jx0404id["jx0404id"],
            "xkzy": "",
            "trjf": "",
            "_": str(int(time.time() * 1000)),
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInGgxxkxk",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }

        response = session.get(url, params=params, headers=headers)
        response_json = response.json()

        logging.info(
            f"已发送【{course_name}】的公选课选课请求, 响应代码: {response.status_code}，响应内容: {response_json}"
        )

        if "flag1" in response_json:
            if response_json["flag1"] == 3:
                message = response_json.get("msgContent", "未知原因")
                logging.warning(f"登录状态异常: {message}")
                return None, message
            elif response_json["flag1"] == 1:
                logging.info(f"【{course_name}】的公选课选课成功")
                return True, None
        elif "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logging.info(f"【{course_name}】的公选课选课成功: {message}")
                return True, None
            else:
                logging.warning(f"【{course_name}】的公选课选课失败: {message}")
                return False, message

        logging.warning(f"【{course_name}】的公选课选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logging.error(f"发送【{course_name}】的公选课选课请求数据失败: {error_msg}")
        return None, error_msg


def send_knjxkOper_course_jx02id_and_jx0404id(course_name, course_jx02id_and_jx0404id):
    """发送专业内跨年级选课请求"""
    try:
        session = get_session()

        # 检查是否需要同时选择讲课学时和实验学时
        if course_jx02id_and_jx0404id.get("needs_both", False):
            logging.info(f"【{course_name}】需要同时选择讲课学时和实验学时")

            # 首先选择讲课学时
            lecture_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/knjxkOper"
            lecture_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "cfbs": course_jx02id_and_jx0404id["lecture_course"]["cfbs"],
                "jx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "xkzy": "",
                "trjf": "",
                "_": str(int(time.time() * 1000)),
            }
            lecture_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInKnjxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            lecture_response = session.get(
                lecture_url, params=lecture_params, headers=lecture_headers
            )
            lecture_response_json = lecture_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时的专业内跨年级选课请求, 响应代码: {lecture_response.status_code}，响应内容: {lecture_response_json}"
            )

            # 检查讲课学时选课结果
            if "flag1" in lecture_response_json:
                if lecture_response_json["flag1"] == 3:
                    message = lecture_response_json.get("msgContent", "未知原因")
                    logging.warning(f"讲课学时选课登录状态异常: {message}")
                    return None, message
                elif lecture_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时选课成功")
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时选课失败: {lecture_response_json}"
                    )
                    return False, str(lecture_response_json)
            elif "success" in lecture_response_json:
                message = lecture_response_json.get("message", "未知原因")
                if isinstance(lecture_response_json["success"], list):
                    success = all(lecture_response_json["success"])
                else:
                    success = lecture_response_json["success"]

                if success:
                    logging.info(f"【{course_name}】讲课学时选课成功: {message}")
                else:
                    logging.warning(f"【{course_name}】讲课学时选课失败: {message}")
                    return False, message

            # 然后同时选择讲课学时和实验学时
            combined_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/knjxkOper"
            combined_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "yxjx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "jx0404id": course_jx02id_and_jx0404id["lab_course"]["jx0404id"],
                "_": str(int(time.time() * 1000)),
            }
            combined_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInKnjxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            combined_response = session.get(
                combined_url, params=combined_params, headers=combined_headers
            )
            combined_response_json = combined_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时+实验学时的专业内跨年级选课请求, 响应代码: {combined_response.status_code}，响应内容: {combined_response_json}"
            )

            # 检查最终选课结果
            if "flag1" in combined_response_json:
                if combined_response_json["flag1"] == 3:
                    message = combined_response_json.get("msgContent", "未知原因")
                    logging.warning(f"最终选课登录状态异常: {message}")
                    return None, message
                elif combined_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时+实验学时选课成功")
                    return True, None
            elif "success" in combined_response_json:
                message = combined_response_json.get("message", "未知原因")
                if isinstance(combined_response_json["success"], list):
                    success = all(combined_response_json["success"])
                else:
                    success = combined_response_json["success"]

                if success:
                    logging.info(
                        f"【{course_name}】讲课学时+实验学时选课成功: {message}"
                    )
                    return True, None
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时+实验学时选课失败: {message}"
                    )
                    return False, message

            logging.warning(
                f"【{course_name}】讲课学时+实验学时选课失败: {combined_response_json}"
            )
            return False, str(combined_response_json)

        # 原有的单课程选课逻辑
        url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/knjxkOper"
        params = {
            "kcid": course_jx02id_and_jx0404id["jx02id"],
            "cfbs": "null",
            "jx0404id": course_jx02id_and_jx0404id["jx0404id"],
            "xkzy": "",
            "trjf": "",
            "_": str(int(time.time() * 1000)),
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInKnjxk",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }

        response = session.get(url, params=params, headers=headers)
        response_json = response.json()

        logging.info(
            f"已发送【{course_name}】的专业内跨年级选课请求, 响应代码: {response.status_code}，响应内容: {response_json}"
        )

        if "flag1" in response_json:
            if response_json["flag1"] == 3:
                message = response_json.get("msgContent", "未知原因")
                logging.warning(f"登录状态异常: {message}")
                return None, message
            elif response_json["flag1"] == 1:
                logging.info(f"【{course_name}】的专业内跨年级选课成功")
                return True, None
        elif "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logging.info(f"【{course_name}】的专业内跨年级选课成功: {message}")
                return True, None
            else:
                logging.warning(f"【{course_name}】的专业内跨年级选课失败: {message}")
                return False, message

        logging.warning(f"【{course_name}】的专业内跨年级选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logging.error(
            f"发送【{course_name}】的专业内跨年级选课请求数据失败: {error_msg}"
        )
        return None, error_msg


def send_bxqjhxkOper_course_jx02id_and_jx0404id(
    course_name, course_jx02id_and_jx0404id
):
    """发送本学期计划选课请求"""
    try:
        session = get_session()

        # 检查是否需要同时选择讲课学时和实验学时
        if course_jx02id_and_jx0404id.get("needs_both", False):
            logging.info(f"【{course_name}】需要同时选择讲课学时和实验学时")

            # 首先选择讲课学时
            lecture_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper"
            lecture_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "cfbs": course_jx02id_and_jx0404id["lecture_course"]["cfbs"],
                "jx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "xkzy": "",
                "trjf": "",
                "_": str(int(time.time() * 1000)),
            }
            lecture_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            lecture_response = session.get(
                lecture_url, params=lecture_params, headers=lecture_headers
            )
            lecture_response_json = lecture_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时的本学期计划选课请求, 响应代码: {lecture_response.status_code}，响应内容: {lecture_response_json}"
            )

            # 检查讲课学时选课结果
            if "flag1" in lecture_response_json:
                if lecture_response_json["flag1"] == 3:
                    message = lecture_response_json.get("msgContent", "未知原因")
                    logging.warning(f"讲课学时选课登录状态异常: {message}")
                    return None, message
                elif lecture_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时选课成功")
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时选课失败: {lecture_response_json}"
                    )
                    return False, str(lecture_response_json)
            elif "success" in lecture_response_json:
                message = lecture_response_json.get("message", "未知原因")
                if isinstance(lecture_response_json["success"], list):
                    success = all(lecture_response_json["success"])
                else:
                    success = lecture_response_json["success"]

                if success:
                    logging.info(f"【{course_name}】讲课学时选课成功: {message}")
                else:
                    logging.warning(f"【{course_name}】讲课学时选课失败: {message}")
                    return False, message

            # 然后同时选择讲课学时和实验学时
            combined_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper"
            combined_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "yxjx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "jx0404id": course_jx02id_and_jx0404id["lab_course"]["jx0404id"],
                "_": str(int(time.time() * 1000)),
            }
            combined_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            combined_response = session.get(
                combined_url, params=combined_params, headers=combined_headers
            )
            combined_response_json = combined_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时+实验学时的本学期计划选课请求, 响应代码: {combined_response.status_code}，响应内容: {combined_response_json}"
            )

            # 检查最终选课结果
            if "flag1" in combined_response_json:
                if combined_response_json["flag1"] == 3:
                    message = combined_response_json.get("msgContent", "未知原因")
                    logging.warning(f"最终选课登录状态异常: {message}")
                    return None, message
                elif combined_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时+实验学时选课成功")
                    return True, None
            elif "success" in combined_response_json:
                message = combined_response_json.get("message", "未知原因")
                if isinstance(combined_response_json["success"], list):
                    success = all(combined_response_json["success"])
                else:
                    success = combined_response_json["success"]

                if success:
                    logging.info(
                        f"【{course_name}】讲课学时+实验学时选课成功: {message}"
                    )
                    return True, None
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时+实验学时选课失败: {message}"
                    )
                    return False, message

            logging.warning(
                f"【{course_name}】讲课学时+实验学时选课失败: {combined_response_json}"
            )
            return False, str(combined_response_json)

        # 原有的单课程选课逻辑
        url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper"
        params = {
            "kcid": course_jx02id_and_jx0404id["jx02id"],
            "cfbs": "null",
            "jx0404id": course_jx02id_and_jx0404id["jx0404id"],
            "xkzy": "",
            "trjf": "",
            "_": str(int(time.time() * 1000)),
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }

        response = session.get(url, params=params, headers=headers)
        response_json = response.json()

        logging.info(
            f"已发送【{course_name}】的本学期计划选课请求, 响应代码: {response.status_code}，响应内容: {response_json}"
        )

        if "flag1" in response_json:
            if response_json["flag1"] == 3:
                message = response_json.get("msgContent", "未知原因")
                logging.warning(f"登录状态异常: {message}")
                return None, message
            elif response_json["flag1"] == 1:
                logging.info(f"【{course_name}】的本学期计划选课成功")
                return True, None
        elif "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logging.info(f"【{course_name}】的本学期计划选课成功: {message}")
                return True, None
            else:
                logging.warning(f"【{course_name}】的本学期计划选课失败: {message}")
                return False, message

        logging.warning(f"【{course_name}】的本学期计划选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logging.error(f"发送【{course_name}】的本学期计划选课请求数据失败: {error_msg}")
        return None, error_msg


def send_xxxkOper_course_jx02id_and_jx0404id(course_name, course_jx02id_and_jx0404id):
    """发送选修选课请求"""
    try:
        session = get_session()

        # 检查是否需要同时选择讲课学时和实验学时
        if course_jx02id_and_jx0404id.get("needs_both", False):
            logging.info(f"【{course_name}】需要同时选择讲课学时和实验学时")

            # 首先选择讲课学时
            lecture_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xxxkOper"
            lecture_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "cfbs": course_jx02id_and_jx0404id["lecture_course"]["cfbs"],
                "jx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "xkzy": "",
                "trjf": "",
                "_": str(int(time.time() * 1000)),
            }
            lecture_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            lecture_response = session.get(
                lecture_url, params=lecture_params, headers=lecture_headers
            )
            lecture_response_json = lecture_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时的选修选课请求, 响应代码: {lecture_response.status_code}，响应内容: {lecture_response_json}"
            )

            # 检查讲课学时选课结果
            if "flag1" in lecture_response_json:
                if lecture_response_json["flag1"] == 3:
                    message = lecture_response_json.get("msgContent", "未知原因")
                    logging.warning(f"讲课学时选课登录状态异常: {message}")
                    return None, message
                elif lecture_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时选课成功")
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时选课失败: {lecture_response_json}"
                    )
                    return False, str(lecture_response_json)
            elif "success" in lecture_response_json:
                message = lecture_response_json.get("message", "未知原因")
                if isinstance(lecture_response_json["success"], list):
                    success = all(lecture_response_json["success"])
                else:
                    success = lecture_response_json["success"]

                if success:
                    logging.info(f"【{course_name}】讲课学时选课成功: {message}")
                else:
                    logging.warning(f"【{course_name}】讲课学时选课失败: {message}")
                    return False, message

            # 然后同时选择讲课学时和实验学时
            combined_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xxxkOper"
            combined_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "yxjx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "jx0404id": course_jx02id_and_jx0404id["lab_course"]["jx0404id"],
                "_": str(int(time.time() * 1000)),
            }
            combined_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            combined_response = session.get(
                combined_url, params=combined_params, headers=combined_headers
            )
            combined_response_json = combined_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时+实验学时的选修选课请求, 响应代码: {combined_response.status_code}，响应内容: {combined_response_json}"
            )

            # 检查最终选课结果
            if "flag1" in combined_response_json:
                if combined_response_json["flag1"] == 3:
                    message = combined_response_json.get("msgContent", "未知原因")
                    logging.warning(f"最终选课登录状态异常: {message}")
                    return None, message
                elif combined_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时+实验学时选课成功")
                    return True, None
            elif "success" in combined_response_json:
                message = combined_response_json.get("message", "未知原因")
                if isinstance(combined_response_json["success"], list):
                    success = all(combined_response_json["success"])
                else:
                    success = combined_response_json["success"]

                if success:
                    logging.info(
                        f"【{course_name}】讲课学时+实验学时选课成功: {message}"
                    )
                    return True, None
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时+实验学时选课失败: {message}"
                    )
                    return False, message

            logging.warning(
                f"【{course_name}】讲课学时+实验学时选课失败: {combined_response_json}"
            )
            return False, str(combined_response_json)

        # 原有的单课程选课逻辑
        url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xxxkOper"
        params = {
            "kcid": course_jx02id_and_jx0404id["jx02id"],
            "cfbs": "null",
            "jx0404id": course_jx02id_and_jx0404id["jx0404id"],
            "xkzy": "",
            "trjf": "",
            "_": str(int(time.time() * 1000)),
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }
        response = session.get(url, params=params, headers=headers)
        response_json = response.json()

        logging.info(
            f"已发送【{course_name}】的选修选课请求, 响应代码: {response.status_code}，响应内容: {response_json}"
        )

        if "flag1" in response_json:
            if response_json["flag1"] == 3:
                message = response_json.get("msgContent", "未知原因")
                logging.warning(f"登录状态异常: {message}")
                return None, message
            elif response_json["flag1"] == 1:
                logging.info(f"【{course_name}】的选修选课成功")
                return True, None
        elif "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logging.info(f"【{course_name}】的选修选课成功: {message}")
                return True, None
            else:
                logging.warning(f"【{course_name}】的选修选课失败: {message}")
                return False, message

        logging.warning(f"【{course_name}】的选修选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logging.error(f"发送【{course_name}】的选修选课请求数据失败: {error_msg}")
        return None, error_msg


def send_fawxkOper_course_jx02id_and_jx0404id(course_name, course_jx02id_and_jx0404id):
    """发送计划外选课请求"""
    try:
        session = get_session()

        # 检查是否需要同时选择讲课学时和实验学时
        if course_jx02id_and_jx0404id.get("needs_both", False):
            logging.info(f"【{course_name}】需要同时选择讲课学时和实验学时")

            # 首先选择讲课学时
            lecture_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/fawxkOper"
            lecture_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "cfbs": course_jx02id_and_jx0404id["lecture_course"]["cfbs"],
                "jx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "xkzy": "",
                "trjf": "",
                "_": str(int(time.time() * 1000)),
            }
            lecture_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            lecture_response = session.get(
                lecture_url, params=lecture_params, headers=lecture_headers
            )
            lecture_response_json = lecture_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时的计划外选课请求, 响应代码: {lecture_response.status_code}，响应内容: {lecture_response_json}"
            )

            # 检查讲课学时选课结果
            if "flag1" in lecture_response_json:
                if lecture_response_json["flag1"] == 3:
                    message = lecture_response_json.get("msgContent", "未知原因")
                    logging.warning(f"讲课学时选课登录状态异常: {message}")
                    return None, message
                elif lecture_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时选课成功")
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时选课失败: {lecture_response_json}"
                    )
                    return False, str(lecture_response_json)
            elif "success" in lecture_response_json:
                message = lecture_response_json.get("message", "未知原因")
                if isinstance(lecture_response_json["success"], list):
                    success = all(lecture_response_json["success"])
                else:
                    success = lecture_response_json["success"]

                if success:
                    logging.info(f"【{course_name}】讲课学时选课成功: {message}")
                else:
                    logging.warning(f"【{course_name}】讲课学时选课失败: {message}")
                    return False, message

            # 然后同时选择讲课学时和实验学时
            combined_url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/fawxkOper"
            combined_params = {
                "kcid": course_jx02id_and_jx0404id["lecture_course"]["jx02id"],
                "yxjx0404id": course_jx02id_and_jx0404id["lecture_course"]["jx0404id"],
                "jx0404id": course_jx02id_and_jx0404id["lab_course"]["jx0404id"],
                "_": str(int(time.time() * 1000)),
            }
            combined_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            }

            combined_response = session.get(
                combined_url, params=combined_params, headers=combined_headers
            )
            combined_response_json = combined_response.json()

            logging.info(
                f"已发送【{course_name}】讲课学时+实验学时的计划外选课请求, 响应代码: {combined_response.status_code}，响应内容: {combined_response_json}"
            )

            # 检查最终选课结果
            if "flag1" in combined_response_json:
                if combined_response_json["flag1"] == 3:
                    message = combined_response_json.get("msgContent", "未知原因")
                    logging.warning(f"最终选课登录状态异常: {message}")
                    return None, message
                elif combined_response_json["flag1"] == 1:
                    logging.info(f"【{course_name}】讲课学时+实验学时选课成功")
                    return True, None
            elif "success" in combined_response_json:
                message = combined_response_json.get("message", "未知原因")
                if isinstance(combined_response_json["success"], list):
                    success = all(combined_response_json["success"])
                else:
                    success = combined_response_json["success"]

                if success:
                    logging.info(
                        f"【{course_name}】讲课学时+实验学时选课成功: {message}"
                    )
                    return True, None
                else:
                    logging.warning(
                        f"【{course_name}】讲课学时+实验学时选课失败: {message}"
                    )
                    return False, message

            logging.warning(
                f"【{course_name}】讲课学时+实验学时选课失败: {combined_response_json}"
            )
            return False, str(combined_response_json)

        # 原有的单课程选课逻辑
        url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/fawxkOper"
        params = {
            "kcid": course_jx02id_and_jx0404id["jx02id"],
            "cfbs": "null",
            "jx0404id": course_jx02id_and_jx0404id["jx0404id"],
            "xkzy": "",
            "trjf": "",
            "_": str(int(time.time() * 1000)),
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }

        response = session.get(url, params=params, headers=headers)
        response_json = response.json()

        logging.info(
            f"已发送【{course_name}】的计划外选课请求, 响应代码: {response.status_code}，响应内容: {response_json}"
        )

        if "flag1" in response_json:
            if response_json["flag1"] == 3:
                message = response_json.get("msgContent", "未知原因")
                logging.warning(f"登录状态异常: {message}")
                return None, message
            elif response_json["flag1"] == 1:
                logging.info(f"【{course_name}】的计划外选课成功")
                return True, None
        elif "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logging.info(f"【{course_name}】的计划外选课成功: {message}")
                return True, None
            else:
                logging.warning(f"【{course_name}】的计划外选课失败: {message}")
                return False, message

        logging.warning(f"【{course_name}】的计划外选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logging.error(f"发送【{course_name}】的计划外选课请求数据失败: {error_msg}")
        return None, error_msg
