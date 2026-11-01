@echo off
title ADSA Contact Management System
echo =======================================================
echo   ADSA Contact Management System (NexusContacts)
echo   FastAPI + In-Memory ADSA Engine + SQLite + Modern Web UI
echo =======================================================
echo.

set PYTHON_EXE=C:\Users\Sourabh\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PYTHON_EXE%" (
    echo Python 3.12 not found at default path. Checking system python...
    set PYTHON_EXE=python
)

echo Starting backend server on http://localhost:8000 ...
cd /d "%~dp0\backend"

:: Launch browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

:: Start Uvicorn
"%PYTHON_EXE%" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
