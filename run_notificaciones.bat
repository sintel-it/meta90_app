@echo off
cd /d "C:\Users\fico8\OneDrive\Documentos\meta90_app"
if not exist logs mkdir logs
echo ==== [%date% %time%] INICIO ====>> "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\notificaciones_scheduler.log"
"C:\Users\fico8\OneDrive\Documentos\meta90_app\venv\Scripts\python.exe" "C:\Users\fico8\OneDrive\Documentos\meta90_app\enviar_notificaciones_programadas.py" >> "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\notificaciones_scheduler.log" 2>&1
set _EXITCODE=%ERRORLEVEL%
echo ==== [%date% %time%] FIN (exit=%_EXITCODE%) ====>> "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\notificaciones_scheduler.log"
exit /b %_EXITCODE%
