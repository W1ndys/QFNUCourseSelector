@echo off
chcp 65001 >nul
setlocal

:: 检查 uv 是否已安装
where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    goto :Run
)

echo [警告] 系统内未检测到 uv 环境。
echo 本项目依赖 uv 进行环境管理。
set /p "choice=是否现在安装 uv? (Y/N): "
if /i "%choice%"=="Y" (
    echo 正在通过 PowerShell 安装 uv...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    
    echo.
    echo 正在验证安装...
    
    :: 尝试查找默认安装路径并添加到临时 PATH，以便在当前会话中使用
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
        set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
    )
    if exist "%LOCALAPPDATA%\bin\uv.exe" (
        set "PATH=%LOCALAPPDATA%\bin;%PATH%"
    )

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