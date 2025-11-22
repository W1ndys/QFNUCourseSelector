import json
from src.utils.session_manager import get_session
import logging


def get_course_capacity_by_ids(jx02id, jx0404id):
    """
    通过jx02id和jx0404id直接获取课程剩余容量信息
    
    Args:
        jx02id: 课程的jx02id
        jx0404id: 课程的jx0404id
        
    Returns:
        dict: 包含课程信息的字典，如果失败返回None
            - xxrs: 剩余容量
            - kcmc: 课程名称
            - skls: 授课老师
    """
    try:
        session = get_session()
        
        # 尝试不同的选课API来获取课程信息
        apis = [
            ("专业内跨年级选课", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInKnjxk", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkKnjxk"),
            ("本学期计划选课", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInBxqjhxk", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkBxqjhxk"),
            ("选修选课", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInXxxk", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkXxxk"),
            ("公选课选课", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInGgxxkxk", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk"),
            ("计划外选课", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/comeInFawxk", "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkFawxk"),
        ]
        
        for api_name, page_url, search_url in apis:
            try:
                # 访问选课页面
                response = session.get(page_url)
                if response.status_code != 200:
                    continue
                
                # 使用jx02id搜索课程（jx02id通常对应课程编号）
                # 发送搜索请求，不需要其他参数
                response = session.post(
                    search_url,
                    params={
                        "kcxx": "",  # 空的课程信息，会返回所有课程
                        "skls": "",
                        "skxq": "",
                        "skjc": "",
                        "sfym": "false",
                        "sfct": "false",
                        "sfxx": "false",
                    },
                    data={
                        "sEcho": "1",
                        "iColumns": "12",
                        "sColumns": "",
                        "iDisplayStart": "0",
                        "iDisplayLength": "500",  # 获取更多结果
                        "mDataProp_0": "kch",
                        "mDataProp_1": "kcmc",
                        "mDataProp_2": "fzmc",
                        "mDataProp_3": "xf",
                        "mDataProp_4": "skls",
                        "mDataProp_5": "sksj",
                        "mDataProp_6": "skdd",
                        "mDataProp_7": "xqmc",
                        "mDataProp_8": "xkrs",
                        "mDataProp_9": "syrs",
                        "mDataProp_10": "ctsm",
                        "mDataProp_11": "czOper",
                    },
                )
                
                if response.status_code != 200:
                    continue
                
                response_data = json.loads(response.text)
                course_list = response_data.get("aaData", [])
                
                # 在返回的课程列表中查找匹配的课程
                for course in course_list:
                    if course.get("jx02id") == jx02id and course.get("jx0404id") == jx0404id:
                        logging.info(f"通过{api_name}找到课程信息")
                        return {
                            "xxrs": course.get("xxrs", "未知"),
                            "kcmc": course.get("kcmc", "未知"),
                            "skls": course.get("skls", "未知"),
                        }
            except Exception as e:
                logging.debug(f"尝试{api_name}获取课程信息失败: {e}")
                continue
        
        logging.warning(f"未能通过任何API找到jx02id={jx02id}, jx0404id={jx0404id}的课程信息")
        return None
        
    except Exception as e:
        logging.error(f"获取课程容量信息失败: {e}")
        return None
