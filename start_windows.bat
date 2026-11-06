@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Install Python 3.12 or 3.13 with the Windows Python Launcher.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto :failed
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :failed
.venv\Scripts\python.exe scripts\setup_local.py
if errorlevel 1 goto :failed
echo Open http://127.0.0.1:8000 in your browser. Stop with Ctrl+C.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
exit /b
:failed
echo Setup did not complete. See the error above and README_RU.md.
pause
exit /b 1
