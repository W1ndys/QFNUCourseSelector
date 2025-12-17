@echo off
:: 设置控制台编码为UTF-8
chcp 65001 >nul 2>&1
:: 检查是否成功设置
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 无法设置UTF-8编码，可能影响中文显示
    :: UTF-8失败时的GBK fallback
    chcp 936 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [提示] 已切换到GBK编码
    )
)
setlocal enabledelayedexpansion

:: 批量设置安装路径检查函数
:check_uv_path
if exist "%~1" (
    set "PATH=%~1;!PATH!"
    goto :eof
)

:: 检查 uv 是否已安装
where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [信息] 检测到 uv 已安装：
    uv --version
    echo.
    goto :Run
)

echo [警告] 系统内未检测到 uv 环境。
echo 本项目依赖 uv 进行环境管理。
set /p "choice=是否现在安装 uv? (Y/N): "
if /i "!choice!"=="Y" (
    echo 正在通过 PowerShell 安装 uv...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    
    echo.
    echo 正在验证安装...
    
    :: 批量检查常见安装路径
    call :check_uv_path "%USERPROFILE%\.cargo\bin"
    call :check_uv_path "%LOCALAPPDATA%\bin"

    uv --version >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo uv 安装验证成功:
        uv --version
        echo.
    ) else (
        echo [提示] uv 可能已安装，但在当前窗口无法识别。
        echo 请关闭当前窗口，重新运行此脚本即可。
        pause
        exit /b
    )
) else (
    echo 您选择了不安装 uv。脚本无法继续运行。
    pause
    exit /b
)

:Run
echo 正在启动 QFNUCourseGrabberPy...
uv run main.py
pause