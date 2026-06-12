@echo off
REM 智能助手诊断脚本
echo ========================================
echo 智能桌面助手 - 诊断工具
echo ========================================
echo.

echo 1. 检查Python版本...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)
echo ✅ Python已安装
echo.

echo 2. 检查tkinter模块...
python -c "import tkinter; print('tkinter版本:', tkinter.TkVersion)"
if errorlevel 1 (
    echo ❌ tkinter模块未安装
    echo 请重新安装Python并确保勾选tcl/tk选项
    pause
    exit /b 1
)
echo ✅ tkinter模块正常
echo.

echo 3. 检查文件完整性...
if exist "smart_assistant.py" (
    echo ✅ smart_assistant.py 存在
) else (
    echo ❌ smart_assistant.py 不存在
)

if exist ".work_data" (
    echo ✅ .work_data 目录存在
) else (
    echo ⚠️  .work_data 目录不存在（将自动创建）
)
echo.

echo 4. 尝试启动程序...
echo 如果看到窗口弹出，说明启动成功！
echo 如果5秒后没有反应，请关闭窗口并按Ctrl+C
echo.

start pythonw smart_assistant.py
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 诊断完成
echo ========================================
echo.
echo 如果窗口没有出现，可能的原因：
echo 1. 你正在使用远程桌面/SSH（GUI无法显示）
echo 2. Python tkinter有问题
echo 3. 防火墙阻止了窗口显示
echo.
echo 建议：
echo 1. 直接在Windows桌面上双击"启动助手.bat"
echo 2. 不要通过远程连接启动
echo.
pause
