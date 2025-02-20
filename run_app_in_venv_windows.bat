@echo off
chcp 65001
:: 切换到脚本所在目录
cd /d %~dp0
echo 已切换到脚本所在目录

:: 检查虚拟环境目录是否存在
if not exist "venv\Scripts\activate" (
    echo 错误：找不到虚拟环境目录 venv\Scripts\activate
    echo 请确保已经创建了虚拟环境
    pause
    exit /b 1
)

:: 激活 Python 虚拟环境
call venv\Scripts\activate
echo 已激活 Python 虚拟环境

:: 检查 Python 版本
python -c "import sys; ver=sys.version_info; exit(1) if ver.major==3 and ver.minor>12 else exit(0)"
if %errorlevel% equ 1 (
    echo 错误：Python 版本不能高于 3.12
    echo 当前环境的 Python 版本过高，请使用 3.12 或更低版本
    pause
    exit /b 1
)

:: 检查 main.py 是否存在
if not exist "main.py" (
    echo 错误：找不到 main.py 文件
    echo 请确保 main.py 文件存在于 app 目录中
    pause
    exit /b 1
)

:: 运行 Python 脚本
python main.py