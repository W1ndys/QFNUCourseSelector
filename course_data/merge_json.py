import json
import os


def load_json_file(file_path):
    """加载JSON文件并返回aaData内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("aaData", [])
    except Exception as e:
        print(f"加载文件 {file_path} 时出错: {e}")
        return []


def merge_json_files(directory):
    """合并指定目录下所有JSON文件的aaData内容"""
    # 用于存储所有课程数据的集合，使用jx0404id作为唯一标识
    merged_data = {}

    # 遍历目录下的所有JSON文件
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            aaData = load_json_file(file_path)

            # 使用jx0404id作为唯一标识符合并数据
            for course in aaData:
                course_id = course.get("jx0404id")
                if course_id:
                    merged_data[course_id] = course

    # 将合并后的数据转换为列表
    result = {
        "aaData": list(merged_data.values()),
        "iTotalRecords": len(merged_data),
        "iTotalDisplayRecords": len(merged_data),
    }

    # 保存合并后的数据
    output_path = os.path.join(directory, "merged_courses.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"合并完成，共处理 {len(merged_data)} 条课程数据")
    print(f"结果已保存至: {output_path}")


if __name__ == "__main__":
    # 指定JSON文件所在的目录
    directory = "./"
    merge_json_files(directory)
