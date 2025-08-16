@echo off
echo Starting Judicial TTS System...
echo.

REM Set working directory to script location
cd /d "%~dp0"

REM Install all requirements
echo Installing/updating dependencies...
python -m pip install -r requirements.txt

REM Start the server
echo Starting TTS server on http://localhost:8000
echo Opening browser...
echo Ctrl+C to stop the server

REM Start server and open browser
start http://localhost:8000
.\python\python.exe app.py
timeout /t 3 /nobreak >nul
pause

