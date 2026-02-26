@echo off
setlocal
cd /d "%~dp0\.."
set BACKUP_FILE=backups\metas_latest.db
if not exist "%BACKUP_FILE%" (
  echo No existe %BACKUP_FILE%
  exit /b 1
)
venv\Scripts\python.exe scripts\db_restore.py --from "%BACKUP_FILE%" --to metas.db --make-safety-copy
if errorlevel 1 (
  echo Error en restore.
  exit /b 1
)
echo Restore completado.
exit /b 0
