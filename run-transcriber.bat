@echo off
REM Double-click this file to launch the Local Transcriber web app.
REM It will open in your default browser automatically.
cd /d "%~dp0"
echo Starting Local Transcriber...
echo (A browser tab will open. To stop the app, close this window or press Ctrl+C.)
echo.
python app.py
pause
