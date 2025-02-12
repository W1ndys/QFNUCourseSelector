import re
import logging
from typing import Optional
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


def get_jx0502zbid(session, select_course_id_or_name: str) -> Optional[str]:
    """
    获取教务系统中的选课轮次编号
    Args:
        session: 请求会话
        cookies: cookies信息
        select_course_id_or_name: 选课名称，用于匹配正确的选课轮次
    Returns:
        Optional[str]: 选课轮次编号(jx0502zbid)，如果未找到返回None
    Raises:
        ValueError: 当输入参数无效时
        RequestException: 当网络请求失败时
    """
    # 参数验证
    if not select_course_id_or_name or not isinstance(select_course_id_or_name, str):
        raise ValueError("选课名称不能为空且必须是字符串类型")

    url = "http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xklc_list"
    jx0502zbid_pattern = re.compile(r"jx0502zbid=([^&]+)")

    try:
        response = session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr")

        for row in rows:
            try:
                cells = row.find_all("td")
                if not cells or len(cells) < 2:
                    continue

                if select_course_id_or_name in cells[1].text.strip():
                    link = row.find("a", href=True)
                    if link and "jx0502zbid" in link["href"]:
                        match = jx0502zbid_pattern.search(link["href"])
                        if match:
                            return match.group(1)
            except (AttributeError, IndexError) as e:
                logging.warning(f"解析行数据时出错: {str(e)}")
                continue

        return None

    except RequestException as e:
        logging.error(f"请求选课页面失败: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"获取选课轮次时发生未知错误: {str(e)}")
        raise


def get_xxxk_course_list(session):
    """
    获取选修选课课程列表

    Args:
        session: 请求会话
        cookies: cookies信息

    Returns:
        str: 选修选课课程列表的响应内容

    Raises:
        RequestException: 当网络请求失败时
        Exception: 其他未知错误
    """
    try:
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
        }

        url = f"http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkXxxk"

        params = {
            "kcxx": "",
            "skls": "",
            "skxq": "",
            "sfym": "false",
            "sfct": "false",
            "sfxx": "true",
        }

        data = {
            "sEcho": "1",
            "iColumns": "11",
            "sColumns": "",
            "iDisplayStart": "0",
            "iDisplayLength": "15",
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
        response = session.post(url, data=data, headers=headers, params=params)
        response.raise_for_status()
        return response.text

    except RequestException as e:
        logging.error(f"获取选修选课课程列表失败: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"获取选修选课课程列表时发生未知错误: {str(e)}")
        raise
