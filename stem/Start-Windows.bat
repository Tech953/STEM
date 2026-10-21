@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py
) else (
  python server.py
)
if errorlevel 1 echo STEM could not start. Read the error above. Python 3.10 or newer is required.
pause
