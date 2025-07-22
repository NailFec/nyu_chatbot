@echo off
title SK HPC Services Chatbot
echo ================================================================
echo   SK (Shame Kitten) HPC Services - Chatbot System
echo ================================================================
echo.

REM Set the Python environment path
set PYTHON_EXE=%USERPROFILE%\miniconda3\envs\nyu\python.exe

REM Check if Python environment exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python environment not found at %PYTHON_EXE%
    echo Please make sure the 'nyu' conda environment is installed.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "nailfec.py" (
    echo ERROR: nailfec.py not found. Please create this file with your API keys.
    pause
    exit /b 1
)

if not exist "hpc_chatbot.py" (
    echo ERROR: hpc_chatbot.py not found.
    pause
    exit /b 1
)

:menu
echo.
echo Choose an option:
echo 1. Run CLI Chatbot
echo 2. Run Web Server + Dashboard
echo 3. Run Chat Interface Only
echo 4. Install Dependencies
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto cli
if "%choice%"=="2" goto web
if "%choice%"=="3" goto chat
if "%choice%"=="4" goto install
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
goto menu

:cli
echo.
echo Starting CLI Chatbot...
echo Type 'quit' to exit the chatbot.
echo ----------------------------------------------------------------
"%PYTHON_EXE%" hpc_chatbot.py
goto menu

:web
echo.
echo Starting Web Server...
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server.
echo ----------------------------------------------------------------
"%PYTHON_EXE%" web_server.py
goto menu

:chat
echo.
echo Starting Chat Interface...
echo Opening browser...
start "" "http://localhost:5000/chat_interface.html"
"%PYTHON_EXE%" web_server.py
goto menu

:install
echo.
echo Installing dependencies...
"%PYTHON_EXE%" -m pip install -r requirements.txt
echo.
echo Dependencies installation completed.
pause
goto menu

:exit
echo.
echo Thank you for using SK HPC Services!
pause
