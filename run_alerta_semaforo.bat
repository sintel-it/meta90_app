@echo off
setlocal
cd /d "C:\Users\fico8\OneDrive\Documentos\meta90_app"
if not exist logs mkdir logs
"C:\Users\fico8\OneDrive\Documentos\meta90_app\venv\Scripts\python.exe" "C:\Users\fico8\OneDrive\Documentos\meta90_app\scripts\alerta_semaforo.py" >> "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\semaforo_alerta.log" 2>&1
exit /b %ERRORLEVEL%
