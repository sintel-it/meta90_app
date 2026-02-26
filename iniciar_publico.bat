@echo off
setlocal

cd /d "C:\Users\fico8\OneDrive\Documentos\meta90_app"

if not exist "venv\Scripts\python.exe" (
    echo No se encontro venv\Scripts\python.exe
    pause
    exit /b 1
)

where ngrok >nul 2>nul
if errorlevel 1 (
    echo No se encontro ngrok en PATH.
    echo Instala ngrok o abre PowerShell y ejecuta: winget install ngrok.ngrok
    pause
    exit /b 1
)

echo Iniciando servidor Flask en nueva ventana...
start "Meta90 App" cmd /k "cd /d C:\Users\fico8\OneDrive\Documentos\meta90_app && venv\Scripts\python.exe app.py"

echo Esperando a que la app responda en 127.0.0.1:5000...
set /a _tries=0
:wait_port
set /a _tries+=1
powershell -NoProfile -Command "if ((Test-NetConnection -ComputerName 127.0.0.1 -Port 5000).TcpTestSucceeded) { exit 0 } else { exit 1 }" >nul 2>nul
if %errorlevel%==0 goto port_ok
if %_tries% GEQ 20 (
    echo No se pudo detectar la app en el puerto 5000.
    echo Revisa la ventana 'Meta90 App' para ver si hubo error.
    pause
    exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_port

:port_ok

echo Iniciando tunel ngrok en nueva ventana...
start "Meta90 ngrok" cmd /k "ngrok http http://127.0.0.1:5000"

echo Listo. Revisa la ventana 'Meta90 ngrok' para copiar la URL publica.
pause
