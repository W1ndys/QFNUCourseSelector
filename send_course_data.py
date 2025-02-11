import time
import logging
from session_manager import get_session


def send_ggxxkxkOper_course_data(course_data):
    """发送公选课选课请求"""
    try:
        session = get_session()

        url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/ggxxkxkOper"
        params = {
            "kcid": course_data["jx02id"],
            "cfbs": "null",
            "jx0404id": course_data["jx0404id"],
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

        logging.info(
            f"已发送选课请求, 响应代码: {response.status_code}, 响应内容: {response.text}"
        )
        return response
    except Exception as e:
        logging.error(f"发送选课请求数据失败: {e}")
        return None
