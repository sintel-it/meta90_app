@echo off
setlocal
cd /d "%~dp0\.."
if not exist "logs" mkdir "logs"
venv\Scripts\python.exe scripts\db_restore_verify.py >> logs\db_restore_verify.log 2>&1
if errorlevel 1 (
  echo Error en verificacion de restore. Revisa logs\db_restore_verify.log
  exit /b 1
)
echo Verificacion de restore completada.
exit /b 0
