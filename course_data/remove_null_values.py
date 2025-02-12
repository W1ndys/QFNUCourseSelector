import json
import glob
import os


def remove_null_values(obj):
    """递归删除字典或列表中的 null 值"""
    if isinstance(obj, dict):
        # 创建要删除的键的列表
        keys_to_delete = []
        for key, value in obj.items():
            if value is None:
                keys_to_delete.append(key)
            elif isinstance(value, (dict, list)):
                obj[key] = remove_null_values(value)

        # 删除值为 null 的键
        for key in keys_to_delete:
            del obj[key]
        return obj

    elif isinstance(obj, list):
        # 过滤掉列表中的 null 值，并处理剩余项
        return [remove_null_values(item) for item in obj if item is not None]

    return obj


def process_json_file(file_path):
    """处理单个 JSON 文件"""
    try:
        # 读取 JSON 文件
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 删除 null 值
        cleaned_data = remove_null_values(data)

        # 保存处理后的文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

        print(f"成功处理文件: {file_path}")
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")


def main():
    # 获取当前目录下所有 JSON 文件
    json_files = glob.glob("*.json")

    if not json_files:
        print("当前目录下没有找到 JSON 文件")
        return

    for file_path in json_files:
        print(f"正在处理文件: {file_path}")
        process_json_file(file_path)


if __name__ == "__main__":
    main()
