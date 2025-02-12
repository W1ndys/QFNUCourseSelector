import json
import time
import ujson  # 需要先安装: pip install ujson
import rapidjson  # 需要先安装: pip install python-rapidjson


def test_json_read(parser_name="json"):
    parsers = {"json": json, "ujson": ujson, "rapidjson": rapidjson}
    parser = parsers[parser_name]

    start_time = time.time()

    # 读取文件
    with open("0.json", "r", encoding="utf-8") as f:
        file_read_time = time.time()
        content = f.read()
        read_complete_time = time.time()

        # JSON解析
        data = parser.loads(content)
        parse_complete_time = time.time()

    # 计算各阶段耗时
    file_read_duration = (read_complete_time - file_read_time) * 1000
    parse_duration = (parse_complete_time - read_complete_time) * 1000
    total_duration = (parse_complete_time - start_time) * 1000

    print(f"使用 {parser_name}:")
    print(f"文件读取耗时: {file_read_duration:.2f}ms")
    print(f"JSON解析耗时: {parse_duration:.2f}ms")
    print(f"总耗时: {total_duration:.2f}ms")
    print("-" * 40)


# 测试所有解析器
for parser in ["json", "ujson", "rapidjson"]:
    test_json_read(parser)
