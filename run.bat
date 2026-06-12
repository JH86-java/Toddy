@echo off
chcp 65001 >nul
REM Start Smart Assistant in Background
start "" pythonw "%~dp0smart_assistant.py"
exit
