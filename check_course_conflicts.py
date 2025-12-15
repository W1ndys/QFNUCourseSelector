import json
from pathlib import Path


def check_single_pair(course_a, course_b, is_mock=False):
    # 1. 检查课程名称是否相同
    if course_a.get('kcmc') != course_b.get('kcmc'):
        return False

    # 2. 检查课程ID是否相同 (使用 kch 作为课程ID)
    if course_a.get('kch') != course_b.get('kch'):
        return False

    # 3. 检查是否含有相同老师
    teachers_a = set(t.strip() for t in course_a.get('skls', '').split(',') if t.strip())
    teachers_b = set(t.strip() for t in course_b.get('skls', '').split(',') if t.strip())
    
    common_teachers = teachers_a.intersection(teachers_b)
    if not common_teachers:
        return False

    # 4. 检查具体上课时间冲突
    time_set_a = set()
    for t in course_a.get('zcxqjcList', []):
        time_key = (t.get('zc'), t.get('xq'), t.get('jc'))
        time_set_a.add(time_key)

    conflict_times = []
    for t in course_b.get('zcxqjcList', []):
        time_key = (t.get('zc'), t.get('xq'), t.get('jc'))
        if time_key in time_set_a:
            conflict_times.append(time_key)

    if conflict_times:
        title = "【模拟演示：发现符合条件的课程对】" if is_mock else "【发现符合条件的课程对】"
        print(f"\n{title}")
        print(f"课程名称: {course_a.get('kcmc')}")
        print(f"课程号 (kch): {course_a.get('kch')}")
        print(f"共有老师: {', '.join(common_teachers)}")
        print(f"\n--- 课程 A (jx0404id: {course_a.get('jx0404id')}) ---")
        print(f"老师: {course_a.get('skls')}")
        print(f"上课时间描述: {course_a.get('sksj')}")
        
        print(f"\n--- 课程 B (jx0404id: {course_b.get('jx0404id')}) ---")
        print(f"老师: {course_b.get('skls')}")
        print(f"上课时间描述: {course_b.get('sksj')}")

        print(f"\n--- 具体冲突的时间点 (周次, 星期, 节次) [共 {len(conflict_times)} 个] ---")
        for idx, (zc, xq, jc) in enumerate(conflict_times):
            if idx >= 10:
                print(f"... 等共 {len(conflict_times)} 个冲突时间点")
                break
            print(f"周次: {zc}, 星期: {xq}, 节次: {jc}")
        print("=" * 50)
        return True
    return False

def run_mock_demo():
    print("\n[Info] 正在生成模拟数据以演示格式...")
    mock_course_a = {
        "kcmc": "演示课程_计算机基础",
        "kch": "TEST_001",
        "skls": "张三, 李四",
        "jx0404id": "111111",
        "sksj": "1-2周 星期一 1-2节",
        "zcxqjcList": [
            {"zc": "1", "xq": "1", "jc": "01"},
            {"zc": "1", "xq": "1", "jc": "02"}
        ]
    }
    # 模拟一个完全一样的课程，或者部分重叠
    mock_course_b = {
        "kcmc": "演示课程_计算机基础",
        "kch": "TEST_001",
        "skls": "张三",
        "jx0404id": "222222",
        "sksj": "1周 星期一 1-2节",
        "zcxqjcList": [
            {"zc": "1", "xq": "1", "jc": "01"}, # 冲突
            {"zc": "1", "xq": "1", "jc": "02"}  # 冲突
        ]
    }
    check_single_pair(mock_course_a, mock_course_b, is_mock=True)

def check_conflicts():
    # 指定数据目录
    data_dir = Path('course_data')
    
    if not data_dir.exists():
        print(f"Error: Directory not found at {data_dir}")
        return

    # 获取所有 JSON 文件
    json_files = list(data_dir.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return

    print(f"Found {len(json_files)} JSON files to process.")
    
    any_conflicts_found = False

    for file_path in json_files:
        print(f"\n{'='*20} Processing: {file_path.name} {'='*20}")
        
        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
                course_list = data.get('aaData', [])
        except Exception as e:
            print(f"Error reading JSON {file_path.name}: {e}")
            continue

        print(f"Total courses found: {len(course_list)}")
        print("-" * 50)

        file_conflicts_found = False

        # 遍历所有课程对 (compare every pair)
        for i in range(len(course_list)):
            for j in range(i + 1, len(course_list)):
                if check_single_pair(course_list[i], course_list[j]):
                    file_conflicts_found = True
                    any_conflicts_found = True

        if not file_conflicts_found:
            print(f"文件 {file_path.name} 中未发现冲突。")

    if not any_conflicts_found:
        print("\n" + "=" * 50)
        print("所有文件中均未发现真实数据中同时满足 [同名、同ID、同老师、同时间] 的课程对。")
        run_mock_demo()

if __name__ == "__main__":
    check_conflicts()