@echo off
chcp 65001 >nul
REM Stop Smart Assistant - No Confirmation
taskkill /F /IM pythonw.exe >nul 2>&1
if errorlevel 1 (
    echo [Info] Assistant is not running or already stopped.
) else (
    echo [Success] Assistant stopped successfully!
)
timeout /t 2 /nobreak >nul
exit /b 0
