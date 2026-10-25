@echo off
cd /d "%~dp0"
echo =====================================
echo         AutoNorm Launcher
echo =====================================
if not exist "venv\Scripts\python.exe" (
    echo Creating Python environment...
    py -m venv venv
    if errorlevel 1 (
        echo Could not create environment. Make sure Python is installed.
        pause
        exit /b 1
    )
)
echo Installing required packages...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo Package installation failed. Check internet connection and try again.
    pause
    exit /b 1
)
echo Starting AutoNorm...
venv\Scripts\python.exe app.py
pause
