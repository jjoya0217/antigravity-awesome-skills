@echo off
chcp 65001 >nul
echo ============================================
echo   YouTube Daily Briefing Agent - Setup
echo   Windows Task Scheduler Registration
echo ============================================
echo.

set AGENT_DIR=%~dp0
set PYTHON_PATH=python

REM 가상환경이 있으면 사용
if exist "%AGENT_DIR%venv\Scripts\python.exe" (
    set PYTHON_PATH=%AGENT_DIR%venv\Scripts\python.exe
)

echo [1/3] Setting up virtual environment...
%PYTHON_PATH% -m venv "%AGENT_DIR%venv" 2>nul
call "%AGENT_DIR%venv\Scripts\activate.bat"

echo [2/3] Installing dependencies...
pip install -r "%AGENT_DIR%requirements.txt" -q

echo [3/3] Registering scheduled task...
echo.

REM Windows Task Scheduler에 등록
schtasks /create /tn "YouTubeDailyBriefing" /tr "\"%AGENT_DIR%venv\Scripts\python.exe\" \"%AGENT_DIR%main.py\" --skip-notebooklm" /sc daily /st 08:00 /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ Scheduled task registered successfully!
    echo    Task name: YouTubeDailyBriefing
    echo    Schedule:  Every day at 08:00
    echo    Command:   python main.py --skip-notebooklm
    echo.
    echo To include NotebookLM analysis, run manually:
    echo    python main.py --show-browser
    echo.
    echo To check the task:
    echo    schtasks /query /tn "YouTubeDailyBriefing"
    echo.
    echo To delete the task:
    echo    schtasks /delete /tn "YouTubeDailyBriefing" /f
) else (
    echo.
    echo ❌ Failed to register scheduled task.
    echo    Try running this script as Administrator.
)

pause
