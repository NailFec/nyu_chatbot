@echo off
echo ================================================================
echo   SK HPC Services - Unified Application Server
echo ================================================================
echo Starting Unified Application...
echo.
echo Available at:
echo   http://localhost:5000          - Chat Interface
echo   http://localhost:5000/dashboard - Data Dashboard
echo   http://localhost:5000/api/     - API Documentation
echo.
echo Press Ctrl+C to stop the server.
echo ================================================================
python app.py
