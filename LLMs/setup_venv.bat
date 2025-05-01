@echo off
SET VENV_NAME=venv

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv %VENV_NAME%

REM Activate virtual environment
echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate.bat

REM Check for requirements.txt and install packages
IF EXIST requirements.txt (
    echo Installing dependencies from requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt
) ELSE (
    echo No requirements.txt found. Skipping package installation.
)

echo.
echo Virtual environment setup complete!
echo To activate later, run: call %VENV_NAME%\Scripts\activate.bat
pause
