import json

def extract_sksj(json_file):
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取所有课程的sksj
    sksj_list = []
    for course in data['aaData']:
        if 'sksj' in course and course['sksj'] and course['sksj'].strip() != '&nbsp;':
            sksj_list.append(course['sksj'])
    
    # 返回去重后的列表
    return list(set(sksj_list))

def save_to_txt(sksj_list, output_file='sksj_list.txt'):
    # 将结果保存到txt文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"共找到 {len(sksj_list)} 个不同的上课时间:\n")
        for sksj in sorted(sksj_list):
            f.write(f"{sksj}\n")

# 使用示例
sksj_list = extract_sksj('all_courses.json')

# 保存到文件
save_to_txt(sksj_list)

# 打印结果
print("结果已保存到 sksj_list.txt")