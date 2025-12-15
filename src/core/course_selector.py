import re
from typing import Optional
from bs4 import BeautifulSoup
import httpx
from loguru import logger


async def get_jx0502zbid(session):
    """
    获取教务系统中的所有选课轮次编号列表
    Args:
        session: 请求会话
    Returns:
        list: 选课轮次编号列表, 每个元素是一个字典, 包含 jx0502zbid 和 name
    Raises:
        httpx.RequestError: 当网络请求失败时
    """
    url = "http://zhjw.qfnu.edu.cn/jsxsd/xsxk/xklc_list"
    jx0502zbid_pattern = re.compile(r"jx0502zbid=([^&]+)")

    try:
        response = await session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr")

        rounds = []
        for row in rows[1:]:  # 跳过表头行
            try:
                cells = row.find_all("td")
                if not cells or len(cells) < 2:
                    continue

                link = row.find("a", href=True)
                if link:
                    href = link.get("href")
                    if isinstance(href, str) and "jx0502zbid" in href:
                        match = jx0502zbid_pattern.search(href)
                        if match:
                            round_info = {
                                "jx0502zbid": match.group(1),
                                "name": cells[1].text.strip(),
                            }
                            rounds.append(round_info)
            except (AttributeError, IndexError) as e:
                logger.warning(f"解析行数据时出错: {str(e)}")
                continue

        return rounds

    except httpx.RequestError as e:
        logger.error(f"请求选课页面失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"获取选课轮次时发生未知错误: {str(e)}")
        raise
