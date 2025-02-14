#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"
echo "已切换到脚本所在目录"

# 检查虚拟环境目录是否存在
if [ ! -f "venv/bin/activate" ]; then
    echo "错误：找不到虚拟环境目录 venv/bin/activate"
    echo "请确保已经创建了虚拟环境"
    read -p "按回车键退出..."
    exit 1
fi

# 激活 Python 虚拟环境
source venv/bin/activate
echo "已激活 Python 虚拟环境"

# 检查 main.py 是否存在
if [ ! -f "main.py" ]; then
    echo "错误：找不到 main.py 文件"
    echo "请确保 main.py 文件存在于当前目录中"
    read -p "按回车键退出..."
    exit 1
fi

# 运行 Python 脚本
python3 main.py

read -p "按回车键退出..." 