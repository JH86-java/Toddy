@echo off
REM 工作追踪快捷脚本
REM 使用方法:
REM   w add "完成了XX功能"
REM   w quick "开会讨论需求"
REM   w done 3
REM   w list
REM   w report

python "%~dp0work_tracker.py" %*
