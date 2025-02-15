def find_course_jx02id_and_jx0404id(course, course_data):
    """在课程数据中查找课程的jx02id和jx0404id"""
    try:
        # 如果course_data为空，直接返回None
        if not course_data:
            return None

        # 获取课程的单双周信息
        week_type = course.get(
            "week_type", "all"
        )  # 可选值: "odd"单周, "even"双周, "all"不限

        # 遍历所有匹配的课程数据
        for data in course_data:
            # 提取jx02id和jx0404id
            jx02id = data.get("jx02id")
            jx0404id = data.get("jx0404id")

            # 基本信息匹配
            if (
                data.get("kch") != course["course_id_or_name"]
                or data.get("skls") != course["teacher_name"]
            ):
                continue

            # 从sksj中提取周次信息
            sksj = data.get("sksj", "")

            # 判断是否匹配周次
            weeks_match = True
            if week_type != "all" and "周" in sksj:
                weeks_str = sksj.split("周")[0].strip()
                # 单周固定模式："1,3,5,7,9,11,13,15,17"
                # 双周固定模式："2,4,6,8,10,12,14,16,18"
                if week_type == "odd" and weeks_str != "1,3,5,7,9,11,13,15,17":
                    weeks_match = False
                elif week_type == "even" and weeks_str != "2,4,6,8,10,12,14,16,18":
                    weeks_match = False

            # 确保两个ID都存在且周次匹配
            if jx02id and jx0404id and weeks_match:
                print(
                    f"找到课程 {course['course_id_or_name']} 的jx02id: {jx02id} 和 jx0404id: {jx0404id}"
                )
                return {"jx02id": jx02id, "jx0404id": jx0404id}

        print(f"未找到匹配的课程数据")
        return None

    except Exception as e:
        print(f"查找课程jx02id和jx0404id时发生错误: {str(e)}")
        return None


if __name__ == "__main__":
    # 测试数据集
    test_cases = [
        {
            "name": "测试1：匹配单周课程",
            "course": {
                "course_id_or_name": "530009",
                "teacher_name": "李大新",
                "class_period": "3-4",
                "week_day": "3",
                "week_type": "odd",
            },
            "expected_sksj": "1,3,5,7,9,11,13,15,17周 星期三 3-4节",
            "expected_jx0404id": "202420252014272",
        },
        {
            "name": "测试2：匹配双周课程",
            "course": {
                "course_id_or_name": "530009",
                "teacher_name": "李大新",
                "class_period": "3-4",
                "week_day": "3",
                "week_type": "even",
            },
            "expected_sksj": "2,4,6,8,10,12,14,16,18周 星期三 3-4节",
            "expected_jx0404id": "202420252014273",
        },
        {
            "name": "测试3：匹配全周课程",
            "course": {
                "course_id_or_name": "530009",
                "teacher_name": "张三",
                "class_period": "1-2",
                "week_day": "1",
                "week_type": "all",
            },
            "expected_sksj": "1-18周 星期一 1-2节",
            "expected_jx0404id": "202420252014274",
        },
        {
            "name": "测试4：匹配前八周课程",
            "course": {
                "course_id_or_name": "530010",
                "teacher_name": "李四",
                "class_period": "5-6",
                "week_day": "2",
                "week_type": "all",
            },
            "expected_sksj": "1-8周 星期二 5-6节",
            "expected_jx0404id": "202420252014275",
        },
        {
            "name": "测试5：匹配后八周课程",
            "course": {
                "course_id_or_name": "530011",
                "teacher_name": "王五",
                "class_period": "7-8",
                "week_day": "4",
                "week_type": "all",
            },
            "expected_sksj": "11-18周 星期四 7-8节",
            "expected_jx0404id": "202420252014276",
        },
        {
            "name": "测试6：匹配中间周课程",
            "course": {
                "course_id_or_name": "530012",
                "teacher_name": "赵六",
                "class_period": "9-10",
                "week_day": "5",
                "week_type": "all",
            },
            "expected_sksj": "6-13周 星期五 9-10节",
            "expected_jx0404id": "202420252014277",
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
