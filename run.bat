@echo off
REM Single-command launcher for Windows (Batch script)
TITLE AI Loan Default Prediction Launcher

echo ========================================================
echo   Starting AI Loan Default Prediction Ecosystem
echo ========================================================

IF EXIST ".venv\Scripts\python.exe" (
    echo Using project virtual environment (.venv)...
    ".venv\Scripts\python.exe" run.py
) ELSE (
    echo Using system Python...
    python run.py
)

pause
