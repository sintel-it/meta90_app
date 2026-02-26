@echo off
setlocal
cd /d "%~dp0\.."
if not exist "logs" mkdir "logs"
venv\Scripts\python.exe scripts\db_backup.py >> logs\db_backup.log 2>&1
if errorlevel 1 (
  echo Error en backup. Revisa logs\db_backup.log
  exit /b 1
)
echo Backup completado.
exit /b 0
