@echo off
setlocal
cd /d "C:\Users\fico8\OneDrive\Documentos\meta90_app"
"C:\Users\fico8\OneDrive\Documentos\meta90_app\venv\Scripts\python.exe" "C:\Users\fico8\OneDrive\Documentos\meta90_app\scripts\postdeploy_check.py"
exit /b %ERRORLEVEL%
