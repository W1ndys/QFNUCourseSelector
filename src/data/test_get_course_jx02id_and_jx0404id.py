import logging


def find_course_jx02id_and_jx0404id(course, course_data):
    """在课程数据中查找课程的jx02id和jx0404id"""
    try:
        # 如果course_data为空，直接返回None
        if not course_data:
            return None

        # 如果只有一组数据，直接返回
        if len(course_data) == 1:
            data = course_data[0]
            jx02id = data.get("jx02id")
            jx0404id = data.get("jx0404id")
            if jx02id and jx0404id:
                logging.critical(
                    f"仅有一组数据，直接匹配课程 【{course['course_id_or_name']}-{course['teacher_name']}】 的jx02id: {jx02id} 和 jx0404id: {jx0404id}"
                )
                return {"jx02id": jx02id, "jx0404id": jx0404id}

        # 处理周次信息
        def parse_weeks(weeks_str):
            weeks = set()
            # 处理多个周次范围（用逗号分隔）
            for part in weeks_str.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    weeks.update(range(start, end + 1))
                else:
                    weeks.add(int(part))
            return weeks

        def check_weeks_match(target_weeks, actual_weeks):
            """检查实际周次是否匹配目标周次"""
            target_set = parse_weeks(target_weeks)
            actual_set = actual_weeks
            # 判断实际周次是否完全包含目标周次
            return target_set.issubset(actual_set)

        # 遍历所有匹配的课程数据
        for data in course_data:
            # 提取jx02id和jx0404id
            jx02id = data.get("jx02id")
            jx0404id = data.get("jx0404id")

            # 基本信息匹配，先判断名称老师是否匹配，以防后面匹配周次强包容性无问题但名称老师不匹配
            if (
                data.get("kch") != course["course_id_or_name"]
                or data.get("skls") != course["teacher_name"]
            ):
                continue

            # 从sksj中提取周次信息
            sksj = data.get("sksj", "")

            # 判断是否匹配周次
            weeks_match = True
            if "weeks" in course and "周" in sksj:  # 使用新的weeks字段
                # 处理可能包含多个时间段的情况
                time_slots = []
                for part in sksj.split("<br>"):
                    time_slots.extend(part.strip().split("、"))

                # 合并所有时间段的周次
                actual_weeks = set()
                for slot in time_slots:
                    if "周" not in slot:
                        continue
                    weeks_str = slot.split("周")[0].strip()
                    actual_weeks.update(parse_weeks(weeks_str))

                # 检查是否匹配目标周次
                weeks_match = check_weeks_match(course["weeks"], actual_weeks)

            # 确保两个ID都存在且周次匹配
            if jx02id and jx0404id and weeks_match:
                logging.critical(
                    f"找到课程 【{course['course_id_or_name']}-{course['teacher_name']}】 的jx02id: {jx02id} 和 jx0404id: {jx0404id}"
                )
                return {"jx02id": jx02id, "jx0404id": jx0404id}

        logging.warning(f"未找到匹配的课程数据")
        return None

    except Exception as e:
        logging.error(f"查找课程jx02id和jx0404id时发生错误: {str(e)}")
        return None


if __name__ == "__main__":
    # 测试数据集
    test_cases = [
        {
            "name": "测试1：单周课程周次匹配",
            "course": {
                "course_id_or_name": "530009",
                "teacher_name": "李大新",
                "class_period": "3-4",
                "week_day": "3",
                "weeks": "1,3,5,7,9,11,13,15,17",  # 新增weeks字段
            },
            "expected_sksj": "1,3,5,7,9,11,13,15,17周 星期三 3-4节",
            "expected_jx0404id": "202420252014272",
        },
        {
            "name": "测试2：双周课程周次匹配",
            "course": {
                "course_id_or_name": "530009",
                "teacher_name": "李大新",
                "class_period": "3-4",
                "week_day": "3",
                "weeks": "2,4,6,8,10,12,14,16,18",  # 新增weeks字段
            },
            "expected_sksj": "2,4,6,8,10,12,14,16,18周 星期三 3-4节",
            "expected_jx0404id": "202420252014273",
        },
        {
            "name": "测试3：连续周次范围匹配",
            "course": {
                "course_id_or_name": "530009",
                "teacher_name": "张三",
                "class_period": "1-2",
                "week_day": "1",
                "weeks": "1-18",  # 新增weeks字段
            },
            "expected_sksj": "1-18周 星期一 1-2节",
            "expected_jx0404id": "202420252014274",
        },
        {
            "name": "测试4：前半学期周次匹配",
            "course": {
                "course_id_or_name": "530010",
                "teacher_name": "李四",
                "class_period": "5-6",
                "week_day": "2",
                "weeks": "1-8",  # 新增weeks字段
            },
            "expected_sksj": "1-8周 星期二 5-6节",
            "expected_jx0404id": "202420252014275",
        },
        {
            "name": "测试5：后半学期周次匹配",
            "course": {
                "course_id_or_name": "530011",
                "teacher_name": "王五",
                "class_period": "7-8",
                "week_day": "4",
                "weeks": "11-18",  # 新增weeks字段
            },
            "expected_sksj": "11-18周 星期四 7-8节",
            "expected_jx0404id": "202420252014276",
        },
        {
            "name": "测试6：中间周次范围匹配",
            "course": {
                "course_id_or_name": "530012",
                "teacher_name": "赵六",
                "class_period": "9-10",
                "week_day": "5",
                "weeks": "6-13",  # 新增weeks字段
            },
            "expected_sksj": "6-13周 星期五 9-10节",
            "expected_jx0404id": "202420252014277",
        },
        {
            "name": "测试7：部分周次匹配（子集）",
            "course": {
                "course_id_or_name": "530009",
                "teacher_name": "李大新",
                "class_period": "3-4",
                "week_day": "3",
                "weeks": "1,3,5",  # 只匹配部分单周
            },
            "expected_sksj": "1,3,5,7,9,11,13,15,17周 星期三 3-4节",
            "expected_jx0404id": "202420252014272",
        },
        {
            "name": "测试8：混合周次格式匹配",
            "course": {
                "course_id_or_name": "530013",
                "teacher_name": "钱七",
                "class_period": "1-2",
                "week_day": "1",
                "weeks": "1-4,6,8-10",
            },
            "expected_sksj": "1-4,6,8-10周 星期一 1-2节",
            "expected_jx0404id": "202420252014278",
        },
    ]

    # 测试数据
    course_data = [
        {
            # 单周课程
            "kch": "530009",
            "kcmc": "体育-定向运动提高课",
            "skls": "李大新",
            "sksj": "1,3,5,7,9,11,13,15,17周 星期三 3-4节",
            "skdd": "体育场",
            "jx0404id": "202420252014272",
            "jx02id": "2D711AA59296468EA1E1B9B7B2B6B0D2",
        },
        {
            # 双周课程
            "kch": "530009",
            "kcmc": "体育-定向运动提高课",
            "skls": "李大新",
            "sksj": "2,4,6,8,10,12,14,16,18周 星期三 3-4节",
            "skdd": "体育场",
            "jx0404id": "202420252014273",
            "jx02id": "3E822BB60307579FB2F2C0C8C3C7C1E3",
        },
        {
            # 全周课程（1-18周）
            "kch": "530009",
            "kcmc": "大学英语",
            "skls": "张三",
            "sksj": "1-18周 星期一 1-2节",
            "skdd": "教学楼A-101",
            "jx0404id": "202420252014274",
            "jx02id": "4F933CC71418680GC3G3D1D9D4D8D2F4",
        },
        {
            # 前八周课程
            "kch": "530010",
            "kcmc": "高等数学",
            "skls": "李四",
            "sksj": "1-8周 星期二 5-6节",
            "skdd": "教学楼B-202",
            "jx0404id": "202420252014275",
            "jx02id": "5G044DD82529791HD4H4E2E0E5E9E3G5",
        },
        {
            # 后八周课程
            "kch": "530011",
            "kcmc": "大学物理",
            "skls": "王五",
            "sksj": "11-18周 星期四 7-8节",
            "skdd": "教学楼C-303",
            "jx0404id": "202420252014276",
            "jx02id": "6H155EE93630802IE5I5F3F1F6F0F4H6",
        },
        {
            # 中间八周课程
            "kch": "530012",
            "kcmc": "程序设计",
            "skls": "赵六",
            "sksj": "6-13周 星期五 9-10节",
            "skdd": "教学楼D-404",
            "jx0404id": "202420252014277",
            "jx02id": "7I266FF04741913JF6J6G4G2G7G1G5I7",
        },
        {
            # 混合周次格式课程
            "kch": "530013",
            "kcmc": "高等数学B",
            "skls": "钱七",
            "sksj": "1-4,6,8-10周 星期一 1-2节",
            "skdd": "教学楼E-505",
            "jx0404id": "202420252014278",
            "jx02id": "8J377GG15852024KG7K7H5H3H8H2H6J8",
        },
        # 添加干扰数据：相同课程号不同老师
        {
            "kch": "530009",
            "kcmc": "体育-定向运动提高课",
            "skls": "王教练",  # 不同老师
            "sksj": "1,3,5,7,9,11,13,15,17周 星期三 3-4节",
            "skdd": "体育场",
            "jx0404id": "202420252014279",
            "jx02id": "9K488HH26963135LH8L8I6I4I9I3I7K9",
        },
        # 添加干扰数据：相同老师不同课程号
        {
            "kch": "530099",  # 不同课程号
            "kcmc": "体育-篮球提高课",
            "skls": "李大新",
            "sksj": "1,3,5,7,9,11,13,15,17周 星期三 3-4节",
            "skdd": "体育馆",
            "jx0404id": "202420252014280",
            "jx02id": "0L599II37074246MI9M9J7J5J0J4J8L0",
        },
        # 添加干扰数据：相同课程号相同老师但不同节次
        {
            "kch": "530009",
            "kcmc": "体育-定向运动提高课",
            "skls": "李大新",
            "sksj": "1,3,5,7,9,11,13,15,17周 星期三 5-6节",  # 不同节次
            "skdd": "体育场",
            "jx0404id": "202420252014281",
            "jx02id": "1M600JJ48185357NJ0N0K8K6K1K5K9M1",
        },
        # 添加干扰数据：相同课程号相同老师但不同周次
        {
            "kch": "530009",
            "kcmc": "体育-定向运动提高课",
            "skls": "李大新",
            "sksj": "2,4,6,8,10,12,14,16周 星期三 3-4节",  # 不同周次
            "skdd": "体育场",
            "jx0404id": "202420252014282",
            "jx02id": "2N711KK59296468OK1O1L9L7L2L6L0N2",
        },
        # 添加干扰数据：部分重叠的周次
        {
            "kch": "530010",
            "kcmc": "高等数学",
            "skls": "李四",
            "sksj": "1-10周 星期二 5-6节",  # 与1-8周部分重叠
            "skdd": "教学楼B-202",
            "jx0404id": "202420252014283",
            "jx02id": "3O822LL60307579PL2P2M0M8M3M7M1O3",
        },
        # 添加干扰数据：完全不同的时间但相同课程和老师
        {
            "kch": "530011",
            "kcmc": "大学物理",
            "skls": "王五",
            "sksj": "1-8周 星期二 1-2节",  # 完全不同的时间
            "skdd": "教学楼C-303",
            "jx0404id": "202420252014284",
            "jx02id": "4P933MM71418680QM3Q3N1N9N4N8N2P4",
        },
        # 添加干扰数据：多时间段课程
        {
            "kch": "530013",
            "kcmc": "高等数学B",
            "skls": "钱七",
            "sksj": "1-4周 星期一 1-2节<br>6-8周 星期一 1-2节",  # 多时间段
            "skdd": "教学楼E-505",
            "jx0404id": "202420252014285",
            "jx02id": "5Q044NN82529791RN4R4O2O0O5O9O3Q5",
        },
    ]

    # 运行测试
    print("开始测试...\n")
    for test_case in test_cases:
        print(f"执行: {test_case['name']}")
        print(f"查找课程: {test_case['course']['course_id_or_name']}")
        print(f"教师: {test_case['course']['teacher_name']}")
        print(f"预期上课时间: {test_case['expected_sksj']}")
        print(f"预期jx0404id: {test_case['expected_jx0404id']}")

        result = find_course_jx02id_and_jx0404id(test_case["course"], course_data)

        if result:
            matched_course = next(
                (c for c in course_data if c["jx0404id"] == result["jx0404id"]), None
            )
            print(
                f"实际上课时间: {matched_course['sksj'] if matched_course else 'Not found'}"
            )
            print(f"实际jx0404id: {result['jx0404id']}")
            print(
                f"测试结果: {'通过' if result['jx0404id'] == test_case['expected_jx0404id'] else '失败'}"
            )
        else:
            print("测试结果: 失败 - 未找到匹配课程")

        print("-" * 50 + "\n")
