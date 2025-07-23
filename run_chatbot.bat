@echo off
title SK HPC Services - Unified Application
echo ================================================================
echo   SK (Shame Kitten) HPC Services - Unified Application
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

if not exist "app.py" (
    echo ERROR: app.py not found.
    pause
    exit /b 1
)

:menu
echo.
echo Choose an option:
echo 1. Start Unified Application (Recommended)
echo 2. Start CLI Chatbot Only
echo 3. Install Dependencies
echo 4. View Available Services
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto unified
if "%choice%"=="2" goto cli
if "%choice%"=="3" goto install
if "%choice%"=="4" goto services
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
goto menu

:unified
echo.
echo Starting Unified Application...
echo.
echo Available Services:
echo - Chat Interface: http://localhost:5000
echo - Data Dashboard: http://localhost:5000/dashboard
echo - API Documentation: http://localhost:5000/api/
echo - Debug Console: http://localhost:5000/debug/history
echo.
echo Press Ctrl+C to stop the server.
echo ----------------------------------------------------------------
"%PYTHON_EXE%" app.py
goto menu

:cli
echo.
echo Starting CLI Chatbot (Direct)...
echo Type 'quit' to exit the chatbot.
echo ----------------------------------------------------------------
"%PYTHON_EXE%" hpc_chatbot.py
goto menu

:services
echo.
echo ================================================================
echo   Available Services (when app.py is running)
echo ================================================================
echo.
echo Main Services:
echo   http://localhost:5000                  - Chat Interface
echo   http://localhost:5000/dashboard        - Data Dashboard
echo.
echo API Endpoints:
echo   http://localhost:5000/api/             - API Documentation
echo   http://localhost:5000/api/chat         - Chat API
echo   http://localhost:5000/api/search_gpus  - GPU Search
echo.
echo Debug Tools:
echo   http://localhost:5000/debug/history    - Conversation History
echo   http://localhost:5000/debug/sessions   - Active Sessions
echo.
pause
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
