@echo off
chcp 65001 >nul
title Toddy Nuitka 打包工具

echo ========================================
echo   Toddy Nuitka 打包工具
echo ========================================
echo.
echo 正在使用 Nuitka 编译为单文件 exe...
echo.
echo 提示: 首次编译需要下载编译器，请耐心等待
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --include-package=pyperclip ^
    --output-dir=dist ^
    --output-filename=Toddy.exe ^
    --assume-yes-for-downloads ^
    smart_assistant.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   打包成功！
    echo ========================================
    echo.
    for %%F in (dist\Toddy.exe) do set SIZE=%%~zF
    set /a SIZE_MB=%SIZE%/1048576
    echo 输出位置: dist\Toddy.exe
    echo 文件大小: !SIZE_MB! MB
    echo.
    echo 提示:
    echo   - 这是单文件 exe，双击即可运行
    echo   - 首次启动可能需要几秒解压
    echo   - 运行时会在同目录创建 .work_data 和 workLog
    echo   - 可以将 exe 复制到任意位置使用
    echo.
) else (
    echo.
    echo ========================================
    echo   打包失败！
    echo ========================================
    echo.
    echo 请检查错误信息 above
    echo.
)

pause
