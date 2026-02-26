@echo off
setlocal
cd /d "C:\Users\fico8\OneDrive\Documentos\meta90_app"
if not exist logs mkdir logs
echo ==== [%date% %time%] INICIO REPORTE DIARIO ====>> "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\reporte_diario.log"
"C:\Users\fico8\OneDrive\Documentos\meta90_app\venv\Scripts\python.exe" "C:\Users\fico8\OneDrive\Documentos\meta90_app\scripts\reporte_diario.py" >> "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\reporte_diario.log" 2>&1
set _EXITCODE=%ERRORLEVEL%
echo ==== [%date% %time%] FIN REPORTE DIARIO (exit=%_EXITCODE%) ====>> "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\reporte_diario.log"
exit /b %_EXITCODE%
