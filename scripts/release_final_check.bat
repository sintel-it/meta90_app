@echo off
setlocal
cd /d "%~dp0\.."
echo === Release final check ===
venv\Scripts\python.exe scripts\predeploy_check.py
if errorlevel 1 exit /b 1
venv\Scripts\python.exe scripts\release_hardening_check.py --strict --env .env
if errorlevel 1 exit /b 1
echo OK: release final check completo.
exit /b 0
