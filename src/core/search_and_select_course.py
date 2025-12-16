from loguru import logger
from .send_course_data import (
    send_ggxxkxkOper_course_jx02id_and_jx0404id,
    send_knjxkOper_course_jx02id_and_jx0404id,
    send_bxqjhxkOper_course_jx02id_and_jx0404id,
    send_xxxkOper_course_jx02id_and_jx0404id,
    send_fawxkOper_course_jx02id_and_jx0404id,
)
from ..utils.feishu import feishu
from ..utils.session_manager import get_session


def search_course_in_url(session, url, course_id, teacher_name, week_day, class_period):
    """
    在指定URL搜索课程

    Args:
        session: requests session
        url: 搜索接口URL
        course_id: 课程编号
        teacher_name: 教师姓名
        week_day: 星期几
        class_period: 节次范围

    Returns:
        list: 搜索结果列表
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

        params = {
            "kcxx": course_id,
            "skls": teacher_name,
            "skxq": week_day,
            "skjc": class_period,
            "sfym": "false",
            "sfct": "false",
            "sfxx": "false",
        }

        data = {
            "iDisplayStart": "0",
            "iDisplayLength": "30000",
        }

        response = session.post(
            url, data=data, headers=headers, params=params
        )
        if response.status_code == 200:
            result = response.json()
            if "aaData" in result and result["aaData"]:
                logger.info(f"在接口 {url} 找到 {len(result['aaData'])} 个课程")
                return result["aaData"]
        
        return []

    except Exception as e:
        logger.debug(f"搜索接口 {url} 失败: {str(e)}")
        return []


def find_matching_course_in_results(results, course):
    """
    在搜索结果中查找匹配的课程ID
    匹配优先级：课程ID > 教师 > 所有时间节点(class_times)

    Args:
        results: 搜索结果列表
        course: 课程配置信息

    Returns:
        list: 包含jx02id和jx0404id的字典列表
    """
    target_course_id = course.get("course_id", "").strip()
    target_teacher = course.get("teacher_name", "").strip()
    
    matches = []

    def normalize_str(val):
        """
        数据清洗与归一化：统一转成字符串，去空格，去前导0
        例如: "09" -> "9", " 1 " -> "1"
        """
        if val is None:
            return ""
        s = str(val).strip()
        # 如果是数字字符串，转int再转str可去除前导0
        if s.isdigit():
            return str(int(s))
        return s
    
    # 构建必需时间集合 (week, week_day, class_period)
    # 集合元素为元组: (week, week_day, class_period)
    required_times = set()
    for t in course.get("class_times", []):
        w = normalize_str(t.get("week", ""))
        wd = normalize_str(t.get("week_day", ""))
        cp = normalize_str(t.get("class_period", ""))
        
        if w and wd and cp:
            required_times.add((w, wd, cp))

    for result in results:
        # 1. 优先匹配课程ID (kch)
        result_kch = str(result.get("kch") or "").strip()
        if target_course_id and target_course_id not in result_kch:
            continue

        # 2. 匹配教师姓名
        result_skls = str(result.get("skls") or "").strip()
        if target_teacher and target_teacher not in result_skls:
            continue

        # 3. 匹配时间 (验证搜索结果是否包含所有必需时间节点)
        zcxqjcList = result.get("zcxqjcList", [])
        if not zcxqjcList:
            # 如果结果没有时间表，但我们需要匹配时间，则跳过
            if required_times:
                continue

        # 构建搜索结果的时间集合
        result_times = set()
        for item in zcxqjcList:
            # 字段映射: zc -> week, xq -> week_day, jc -> class_period
            w = normalize_str(item.get("zc", ""))
            wd = normalize_str(item.get("xq", ""))
            cp = normalize_str(item.get("jc", ""))
            
            if w and wd and cp:
                result_times.add((w, wd, cp))

        # 检查必需时间集合是否是结果时间集合的子集
        # 利用集合特性：判断配置的锚点是否全都在这个集合里
        if required_times.issubset(result_times):
            jx02id = result.get("jx02id", "")
            jx0404id = result.get("jx0404id", "")

            if jx02id and jx0404id:
                logger.info(
                    f"找到匹配的课程: {result.get('kcmc', '未知')}, "
                    f"jx02id={jx02id}, jx0404id={jx0404id}"
                )
                matches.append({"jx02id": jx02id, "jx0404id": jx0404id})
    
    return matches


def search_and_select_course(course):
    """
    根据配置进行选课：
    1. 如果配置了jx02id和jx0404id, 直接发送选课请求
    2. 如果未配置, 则依次在各模块搜索, 搜到即选
    """
    try:
        logger.info(
            f"开始处理课程: 【{course['course_name']}-{course['teacher_name']}】"
        )

        # 验证基础必填字段
        base_required_keys = ["course_name", "course_id", "teacher_name"]
        if not all(key in course for key in base_required_keys):
            logger.error(
                f"课程信息缺少必要的字段, 需要: {', '.join(base_required_keys)}"
            )
            return False

        # 获取jx02id和jx0404id
        jx02id = course.get("jx02id", "").strip()
        jx0404id = course.get("jx0404id", "").strip()

        # 定义选课模块配置 (名称, 搜索URL, 选课函数)
        # 顺序：专业内跨年级 -> 本学期计划 -> 公选课 -> 选修 -> 计划外
        modules = [
            {
                "name": "专业内跨年级选课",
                "search_url": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkKnjxk",
                "select_func": send_knjxkOper_course_jx02id_and_jx0404id
            },
            {
                "name": "本学期计划选课",
                "search_url": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkBxqjhxk",
                "select_func": send_bxqjhxkOper_course_jx02id_and_jx0404id
            },
            {
                "name": "公选课选课",
                "search_url": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk",
                "select_func": send_ggxxkxkOper_course_jx02id_and_jx0404id
            },
            {
                "name": "选修选课",
                "search_url": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkXxxk",
                "select_func": send_xxxkOper_course_jx02id_and_jx0404id
            },
            {
                "name": "计划外选课",
                "search_url": "http://zhjw.qfnu.edu.cn/jsxsd/xsxkkc/xsxkFawxk",
                "select_func": send_fawxkOper_course_jx02id_and_jx0404id
            }
        ]

        error_messages = []

        # 模式1: 直接使用配置的ID
        if jx02id and jx0404id:
            logger.info(f"使用直接ID模式: jx02id={jx02id}, jx0404id={jx0404id}")
            course_data = {"jx02id": jx02id, "jx0404id": jx0404id}
            
            # 尝试所有选课方式
            for module in modules:
                method_name = module["name"]
                method_func = module["select_func"]
                
                try:
                    result_data = method_func(course["course_id"], course_data)
                    if result_data is None:
                        error_messages.append(f"【{method_name}】异常: 返回None")
                        continue
                    
                    result, message = result_data
                    if result is True:
                        success_msg = f"课程【{course['course_name']}-{course['teacher_name']}】通过【{method_name}】选课成功！"
                        feishu("选课成功 🎉", success_msg)
                        return True
                    elif result == "permanent_failure":
                        logger.success(f"永久失败: {message}")
                        return "permanent_failure"
                    else:
                        error_messages.append(f"【{method_name}】失败: {message}")
                except Exception as e:
                    error_messages.append(f"【{method_name}】异常: {str(e)}")

        # 模式2: 搜索并选课 (优化：按模块搜到即选)
        else:
            logger.info("使用搜索模式: 逐个模块搜索并尝试选课...")
            session = get_session()
            
            course_id_param = course.get("course_id", "")
            teacher_name_param = course.get("teacher_name", "")
            week_day_param = course.get("week_day", "").strip()
            class_period_param = course.get("class_period", "").strip()

            search_found = False

            for module in modules:
                module_name = module["name"]
                search_url = module["search_url"]
                select_func = module["select_func"]

                # 1. 搜索
                results = search_course_in_url(
                    session, search_url, course_id_param, teacher_name_param, week_day_param, class_period_param
                )

                if not results:
                    # 当前模块未搜到, 继续下一个模块
                    continue
                
                search_found = True
                
                # 2. 匹配
                matched_list = find_matching_course_in_results(results, course)
                if not matched_list:
                    logger.debug(f"在【{module_name}】搜到课程但不匹配期望时间")
                    continue
                
                # 3. 选课 (遍历所有匹配项)
                for match_item in matched_list:
                    current_jx02id = match_item["jx02id"]
                    current_jx0404id = match_item["jx0404id"]
                    course_data = {"jx02id": current_jx02id, "jx0404id": current_jx0404id}
                    
                    logger.info(f"在【{module_name}】找到课程, 尝试选课: jx02id={current_jx02id}, jx0404id={current_jx0404id}")
                    
                    try:
                        result_data = select_func(course["course_id"], course_data)
                        
                        if result_data is None:
                            error_messages.append(f"【{module_name}】选课异常: 返回None")
                            continue

                        result, message = result_data
                        
                        if result is True:
                            success_msg = f"课程【{course['course_name']}-{course['teacher_name']}】通过【{module_name}】选课成功！"
                            feishu("选课成功 🎉", success_msg)
                            return True
                        elif result == "permanent_failure":
                            perm_msg = f"课程【{course['course_name']}】在【{module_name}】永久失败: {message}"
                            logger.success(perm_msg)
                            feishu("选课永久失败 ⛔", perm_msg)
                            return "permanent_failure"
                        else:
                            error_messages.append(f"【{module_name}】选课失败: {message}")
                            # 继续尝试下一个匹配项
                            continue
                            
                    except Exception as e:
                        error_messages.append(f"【{module_name}】执行异常: {str(e)}")
                        continue

            if not search_found:
                 logger.warning(f"课程【{course['course_name']}-{course['teacher_name']}】在所有模块均未搜索到")

        if error_messages:
            error_summary = (
                f"课程【{course['course_name']}-{course['teacher_name']}】选课失败, 错误汇总：\n"
                + "\n".join(error_messages)
            )
            logger.error(error_summary)
        
        return False

    except Exception as e:
        logger.error(f"选课流程发生未捕获异常: {str(e)}")
        return False
