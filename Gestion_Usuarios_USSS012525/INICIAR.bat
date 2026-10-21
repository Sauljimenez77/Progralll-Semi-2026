@echo off
cd /d "%~dp0"
py -3.14 -m pip install -r requirements.txt
if errorlevel 1 pause & exit /b 1
py -3.14 server.py
pause
