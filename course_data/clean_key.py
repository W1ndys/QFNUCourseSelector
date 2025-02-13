import json
import glob
import os


def clean_zcxqjclist(file_path):
    # 读取JSON文件
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 递归函数来处理嵌套的字典
    def process_dict(d):
        if isinstance(d, dict):
            # 如果找到zcxqjcList键，将其值设为空列表
            if "ctsm" in d:
                d["ctsm"] = []
            # 递归处理所有值
            for value in d.values():
                if isinstance(value, (dict, list)):
                    process_dict(value)
        elif isinstance(d, list):
            # 递归处理列表中的所有元素
            for item in d:
                if isinstance(item, (dict, list)):
                    process_dict(item)

    # 处理数据
    process_dict(data)

    # 保存修改后的文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    # 获取当前目录下所有JSON文件
    json_files = glob.glob("*.json")

    for file_path in json_files:
        try:
            print(f"处理文件: {file_path}")
            clean_zcxqjclist(file_path)
            print(f"成功处理文件: {file_path}")
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")


if __name__ == "__main__":
    main()
