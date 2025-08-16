@echo off
echo Starting Judicial TTS System...
echo.

REM Set working directory to script location
cd /d "%~dp0"

REM Create venv if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv and install requirements
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo Installing/updating dependencies...
python -m pip install -r requirements.txt

REM Start the server
echo Starting TTS server on http://localhost:8000
echo Opening browser...
echo Ctrl+C to stop the server

REM Start server and open browser
start http://localhost:8000
python app.py
timeout /t 3 /nobreak >nul
pause

