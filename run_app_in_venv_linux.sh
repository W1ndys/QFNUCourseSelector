#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"
echo "已切换到脚本所在目录"

# 检查虚拟环境目录是否存在
if [ -f "venv/bin/activate" ]; then
    # 激活 Python 虚拟环境
    source venv/bin/activate
    echo "已激活 Python 虚拟环境"
else
    echo "警告：未找到虚拟环境，将使用主机 Python 环境"
fi

# 检查 Python 版本
python3 -c "import sys; ver=sys.version_info; exit(1) if ver.major==3 and ver.minor>12 else exit(0)"
if [ $? -eq 1 ]; then
    echo "错误：Python 版本不能高于 3.12"
    echo "当前环境的 Python 版本过高，请使用 3.12 或更低版本"
    read -p "按回车键退出..."
    exit 1
fi

# 检查 main.py 是否存在
if [ ! -f "main.py" ]; then
    echo "错误：找不到 main.py 文件"
    echo "请确保 main.py 文件存在于当前目录中"
    read -p "按回车键退出..."
    exit 1
fi

# 运行 Python 脚本
python3 main.py 