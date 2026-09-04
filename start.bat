@echo off
REM Double-click to start the personal chatbot server.
REM Keep this window OPEN while chatting. Close it to stop the server.
cd /d "%~dp0"
python main.py
pause