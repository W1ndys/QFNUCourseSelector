import time
from loguru import logger
from ..utils.session_manager import get_session


# 永久失败关键词集合
PERMANENT_FAILURE_KEYWORDS = {
    "此课堂选课人数已满",
    "此课堂已设置选课限制",
    "冲突",
    "教学班",
}


def check_permanent_failure(message):
    """
    检查消息中是否包含永久失败关键词
    
    Args:
        message: 响应消息字符串
        
    Returns:
        tuple: (是否为永久失败, 匹配的关键词)
    """
    if not message or not isinstance(message, str):
        return False, None
    
    for keyword in PERMANENT_FAILURE_KEYWORDS:
        if keyword in message:
            return True, keyword
    
    return False, None


async def send_ggxxkxkOper_course_jx02id_and_jx0404id(
    course_name, course_jx02id_and_jx0404id
):
    """发送公选课选课请求"""
    try:
        session = await get_session()

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

        response = await session.get(url, params=params, headers=headers)
        response_json = response.json()

        logger.info(
            f"已发送【{course_name}】的公选课选课请求, 响应代码: {response.status_code}"
        )

        if "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logger.info(f"【{course_name}】的公选课选课成功: {message}")
                return True, None
            else:
                # 检查是否为永久失败
                is_permanent, keyword = check_permanent_failure(message)
                if is_permanent:
                    logger.critical(f"【{course_name}】的公选课选课永久失败（检测到关键词：{keyword}）: {message}")
                    return "permanent_failure", message
                logger.warning(f"【{course_name}】的公选课选课失败: {message}")
                return False, message

        logger.warning(f"【{course_name}】的公选课选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"发送【{course_name}】的公选课选课请求数据失败: {error_msg}")
        return None, error_msg


async def send_knjxkOper_course_jx02id_and_jx0404id(course_name, course_jx02id_and_jx0404id):
    """发送专业内跨年级选课请求"""
    try:
        session = await get_session()

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

        response = await session.get(url, params=params, headers=headers)
        response_json = response.json()

        logger.info(
            f"已发送【{course_name}】的专业内跨年级选课请求, 响应代码: {response.status_code}"
        )

        if "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logger.info(f"【{course_name}】的专业内跨年级选课成功: {message}")
                return True, None
            else:
                # 检查是否为永久失败
                is_permanent, keyword = check_permanent_failure(message)
                if is_permanent:
                    logger.critical(f"【{course_name}】的专业内跨年级选课永久失败（检测到关键词：{keyword}）: {message}")
                    return "permanent_failure", message
                logger.warning(f"【{course_name}】的专业内跨年级选课失败: {message}")
                return False, message

        logger.warning(f"【{course_name}】的专业内跨年级选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"发送【{course_name}】的专业内跨年级选课请求数据失败: {error_msg}"
        )
        return None, error_msg


async def send_bxqjhxkOper_course_jx02id_and_jx0404id(
    course_name, course_jx02id_and_jx0404id
):
    """发送本学期计划选课请求"""
    try:
        session = await get_session()

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

        response = await session.get(url, params=params, headers=headers)
        response_json = response.json()

        logger.info(
            f"已发送【{course_name}】的本学期计划选课请求, 响应代码: {response.status_code}"
        )

        if "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logger.info(f"【{course_name}】的本学期计划选课成功: {message}")
                return True, None
            else:
                # 检查是否为永久失败
                is_permanent, keyword = check_permanent_failure(message)
                if is_permanent:
                    logger.critical(f"【{course_name}】的本学期计划选课永久失败（检测到关键词：{keyword}）: {message}")
                    return "permanent_failure", message
                logger.warning(f"【{course_name}】的本学期计划选课失败: {message}")
                return False, message

        logger.warning(f"【{course_name}】的本学期计划选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"发送【{course_name}】的本学期计划选课请求数据失败: {error_msg}")
        return None, error_msg


async def send_xxxkOper_course_jx02id_and_jx0404id(course_name, course_jx02id_and_jx0404id):
    """发送选修选课请求"""
    try:
        session = await get_session()

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
        response = await session.get(url, params=params, headers=headers)
        response_json = response.json()

        logger.info(
            f"已发送【{course_name}】的选修选课请求, 响应代码: {response.status_code}"
        )

        if "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logger.info(f"【{course_name}】的选修选课成功: {message}")
                return True, None
            else:
                # 检查是否为永久失败
                is_permanent, keyword = check_permanent_failure(message)
                if is_permanent:
                    logger.critical(f"【{course_name}】的选修选课永久失败（检测到关键词：{keyword}）: {message}")
                    return "permanent_failure", message
                logger.warning(f"【{course_name}】的选修选课失败: {message}")
                return False, message

        logger.warning(f"【{course_name}】的选修选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"发送【{course_name}】的选修选课请求数据失败: {error_msg}")
        return None, error_msg


async def send_fawxkOper_course_jx02id_and_jx0404id(course_name, course_jx02id_and_jx0404id):
    """发送计划外选课请求"""
    try:
        session = await get_session()

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

        response = await session.get(url, params=params, headers=headers)
        response_json = response.json()

        logger.info(
            f"已发送【{course_name}】的计划外选课请求, 响应代码: {response.status_code}"
        )

        if "success" in response_json:
            message = response_json.get("message", "未知原因")
            if isinstance(response_json["success"], list):
                success = all(response_json["success"])
            else:
                success = response_json["success"]

            if success:
                logger.info(f"【{course_name}】的计划外选课成功: {message}")
                return True, None
            else:
                # 检查是否为永久失败
                is_permanent, keyword = check_permanent_failure(message)
                if is_permanent:
                    logger.critical(f"【{course_name}】的计划外选课永久失败（检测到关键词：{keyword}）: {message}")
                    return "permanent_failure", message
                logger.warning(f"【{course_name}】的计划外选课失败: {message}")
                return False, message

        logger.warning(f"【{course_name}】的计划外选课失败: {response_json}")
        return False, str(response_json)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"发送【{course_name}】的计划外选课请求数据失败: {error_msg}")
        return None, error_msg
