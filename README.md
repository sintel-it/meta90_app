# Meta90 App

Aplicacion web para gestionar metas de ahorro, calendario de eventos, mensajes internos y notificaciones automaticas (push, email y SMS).

## Requisitos

- Windows + PowerShell
- Python 3.11+ (recomendado)
- `ngrok` (opcional para exponer la app por internet)

## Ejecucion Local

1. Crear/activar entorno virtual:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Configurar variables:

- Copia `.env.example` a `.env` y completa credenciales necesarias.

4. Iniciar aplicacion:

```powershell
venv\Scripts\python.exe app.py
```

- URL local: `http://127.0.0.1:5000`

## Exponer La App (Ngrok)

Comando recomendado:

```powershell
ngrok http http://127.0.0.1:5000
```

Tambien puedes usar:

```powershell
iniciar_publico.bat
```

## Notificaciones Automaticas

Runner:

- `enviar_notificaciones_programadas.py`
- `run_notificaciones.bat`

Log:

- `logs/notificaciones_scheduler.log`

Tareas programadas esperadas:

- `Meta90_Notificaciones_Manana` (08:00)
- `Meta90_Notificaciones_Noche` (20:00)

Notas:

- El control de duplicados trabaja por franja (`manana` / `noche`).
- Para entorno productivo:
  - `NOTIFICATIONS_FORCE_EACH_RUN=0`
  - `FORCE_NOTIFICATIONS_TEST=0`

## Salud y Seguridad

- Healthcheck publico:
  - `GET /health`
- Healthcheck detallado (solo admin autenticado):
  - `GET /health/details`
- Ejecucion manual admin de notificaciones multicanal:
  - `POST /admin/notificaciones/ejecutar`
- Dashboard admin operativo:
  - `GET /admin/dashboard`
  - incluye filtros de auditoria (fecha/usuario/modulo/accion) y export CSV
  - incluye paginacion de auditoria (anterior/siguiente)
  - export: `GET /admin/audit/export.csv`
  - usuarios/roles: `GET /admin/usuarios` y `POST /admin/usuarios/<id>/rol`
  - reportes: `GET /admin/reportes/excel` y `GET /admin/reportes/pdf`

Detalles de seguridad y operacion:

- `docs/OPERACION_SEGURIDAD.md`

## Backup y Restore DB

Backup manual:

```powershell
venv\Scripts\python.exe scripts\db_backup.py
```

Restore manual desde ultimo backup:

```powershell
venv\Scripts\python.exe scripts\db_restore.py --from backups\metas_latest.db --to metas.db --make-safety-copy
```

Wrappers en Windows:

- `scripts\db_backup.bat`
- `scripts\db_restore_latest.bat`
- `scripts\db_restore_verify.bat` (verifica restore en DB temporal)

## Checklist Diario (2 Minutos)

1. Verificar app local:

```powershell
Test-NetConnection 127.0.0.1 -Port 5000
```

2. Verificar tareas:

```powershell
schtasks /Query /TN "\Meta90_Notificaciones_Manana" /V /FO LIST
schtasks /Query /TN "\Meta90_Notificaciones_Noche" /V /FO LIST
```

3. Revisar log de scheduler:

```powershell
Get-Content "C:\Users\fico8\OneDrive\Documentos\meta90_app\logs\notificaciones_scheduler.log" -Tail 30
```

4. Prueba manual rapida:

```powershell
schtasks /Run /TN "\Meta90_Notificaciones_Manana"
```

## Estructura Rapida

- `app.py`: orquestacion principal y registro de blueprints.
- `routes/`: endpoints por modulo.
- `modules/`: logica interna desacoplada.
- `services/`: integraciones externas (mail/push/sms/whatsapp).
- `migrations.py`: migraciones SQLite.
- `templates/`: vistas separadas por modulo.
- `static/`: CSS, JS e imagenes.
- `docs/ESTRUCTURA_PROYECTO.md`: mapa tecnico detallado.

## Modulos Funcionales

- Auth: login, registro, recuperacion, OAuth.
- Metas: dashboard inicial (KPIs, actividad, accesos), crear, ver, editar y eliminar metas.
- Calendario: crear, editar, eliminar y exportar eventos.
- Mensajes: entrada, enviados, papelera, editar y eliminar.
- Notificaciones: metas + calendario + mensajes, con descarte visual.
- Perfil: datos de usuario y actualizacion.
- Busqueda global: `GET /buscar?q=...` en metas/eventos/mensajes.

## UX Profesional

- Toggle de `modo compacto` en la barra superior (persistente por navegador).
- KPIs globales en todas las pantallas autenticadas.
- Badges de estado consistentes (urgente/por vencer/hoy/sin leer).
- Microinteraccion de carga en botones al enviar formularios.
- Busqueda global desde barra superior (`/buscar`).

## Monitor de tareas (alerta por correo)

- Script: `scripts/monitor_tareas_programadas.py`
- Runner: `run_task_monitor.bat`
- Log: `logs/task_monitor.log`
- Configurar destinatario de alerta:
  - `ALERT_EMAIL_TO=tu_correo@dominio.com`

## Migraciones Actuales

Versiones aplicadas en `migrations.py`:

- `001_base_tables`
- `002_usuarios_extra`
- `003_metas_user_id`
- `004_usuarios_social`
- `005_indexes`
- `006_web_push`
- `007_web_push_log`
- `008_email_log`
- `009_sms_log`
- `010_calendario_eventos`
- `011_mensajes`
- `012_notificaciones_descartadas`
- `013_roles_usuarios`
- `014_audit_log`

## Errores Frecuentes Y Solucion

### 1. Ngrok `ERR_NGROK_3200` (endpoint offline)

Causa:

- El tunel ngrok ya no esta corriendo.

Solucion:

```powershell
ngrok http http://127.0.0.1:5000
```

Usa la URL nueva que entrega ngrok.

### 2. Ngrok `ERR_NGROK_8012` (upstream refused)

Causa:

- La app local no esta levantada en puerto `5000`.

Solucion:

```powershell
venv\Scripts\python.exe app.py
ngrok http http://127.0.0.1:5000
```

Tip:

- Evita `localhost` si resuelve a `::1`; usa `127.0.0.1`.

### 3. SMS Twilio error `21608` (trial)

Causa:

- Cuenta Twilio Trial no puede enviar a numeros no verificados.

Solucion:

- Verificar el numero destino en Twilio (Verified Caller IDs), o
- actualizar cuenta Twilio a pago.

### 4. No llegan correos SMTP

Checklist:

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
- Si usas Gmail, usar App Password (no password normal).
- Revisar carpeta Spam/Promociones.

### 5. Push no se activa / claves VAPID invalidas

Checklist:

- `PUSH_VAPID_PUBLIC_KEY`
- `PUSH_VAPID_PRIVATE_KEY`
- `PUSH_VAPID_SUBJECT`

Validar:

- activa push desde `/notificaciones`
- revisa mensaje de estado del boton Push.

### 6. Tareas programadas no corren solas

Checklist:

- Verificar tareas:
  - `Meta90_Notificaciones_Manana`
  - `Meta90_Notificaciones_Noche`
- En Programador de tareas:
  - habilitadas
  - ejecutando como `SYSTEM` o "tanto si el usuario inicio sesion como si no".

Comando de prueba:

```powershell
schtasks /Run /TN "\Meta90_Notificaciones_Manana"
Get-Content "logs/notificaciones_scheduler.log" -Tail 40
```

## Predeploy Check

Antes de publicar cambios ejecuta:

```powershell
venv\Scripts\python.exe scripts\predeploy_check.py
```

O doble clic:

```text
scripts\predeploy_check.bat
```

## CI

GitHub Actions:

- `.github/workflows/ci.yml`
- Ejecuta `scripts/predeploy_check.py` en `push` y `pull_request`.

## Release Final

Checklist completo:

- `docs/RELEASE_CHECKLIST.md`

Comando unico recomendado:

```powershell
scripts\release_final_check.bat
```

Incluye:

- compilacion + tests
- chequeo de secretos versionados
- hardening estricto de `.env` para release

## Staging

- Config de staging en Render:
  - `render.staging.yaml`
- Config de produccion:
  - `render.yaml`

## Migracion a Postgres (gestionado)

- Exportar SQLite a Postgres (cutover asistido):

```powershell
set DATABASE_URL=postgresql://USER:PASS@HOST:5432/DB
venv\Scripts\python.exe scripts\sqlite_to_postgres.py
```

- Validar OAuth Google en entorno objetivo:

```powershell
venv\Scripts\python.exe scripts\check_google_oauth.py
```

## Monitor de tareas

- Tarea recomendada:
  - `\Meta90_Task_Monitor` (cada hora)
- Alertas:
  - correo: `ALERT_EMAIL_TO`
  - webhook: `ALERT_WEBHOOK_URL`

## Reporte diario automatico (7 controles)

- Runner:
  - `run_reporte_diario.bat`
- Script:
  - `scripts/reporte_diario.py`
- Salidas:
  - `logs/reporte_diario.log`
  - `logs/reporte_diario_last.txt`
  - `logs/reporte_diario_last.json`

Tarea programada sugerida (22:10 diario):

```powershell
schtasks /Create /TN "Meta90_Reporte_Diario" /SC DAILY /ST 22:10 /RU SYSTEM /RL HIGHEST /TR "C:\Users\fico8\OneDrive\Documentos\meta90_app\run_reporte_diario.bat" /F
```

## Operacion pro (admin)

- Semaforo + historial 7 dias:
  - `GET /admin/dashboard`
- Estado JSON para auto-refresh:
  - `GET /admin/reporte-diario/status`
- Modo mantenimiento de notificaciones:
  - `POST /admin/notificaciones/mantenimiento` (desde dashboard)
- Export completo operativo:
  - `GET /admin/operacion/export.zip`
- Reporte avanzado:
  - `GET /admin/reportes/avanzado`
  - `GET /admin/reportes/avanzado.csv`
  - `GET /admin/reportes/avanzado.pdf`
- Restore de emergencia:
  - `POST /admin/db/restore-emergency`

## Rotacion y alertas

- Rotacion automatica de logs:
  - `scripts/rotate_logs.py`
  - `run_rotate_logs.bat`
- Alerta proactiva de semaforo rojo:
  - `scripts/alerta_semaforo.py`
  - `run_alerta_semaforo.bat`

Tareas sugeridas:

```powershell
schtasks /Create /TN "Meta90_Log_Rotation" /SC DAILY /ST 23:40 /TR "C:\Users\fico8\OneDrive\Documentos\meta90_app\run_rotate_logs.bat" /F
schtasks /Create /TN "Meta90_Semaforo_Alert" /SC MINUTE /MO 15 /TR "C:\Users\fico8\OneDrive\Documentos\meta90_app\run_alerta_semaforo.bat" /F
```

## Seguridad extra

- 2FA admin por email (login admin):
  - `ADMIN_2FA_REQUIRED=1`
  - ruta de verificacion: `GET/POST /auth/admin-2fa`

## Calendario masivo

- Importacion con vista previa:
  - `GET/POST /calendario/importar`
  - confirmar: `POST /calendario/importar/confirmar`
- Soporta:
  - CSV (`fecha,hora,titulo,grupo,lugar,tipo,descripcion`)
  - XLSX (mismas columnas)

## API privada y mobile lite

- Generar/revocar token en `Perfil`.
- Endpoint:
  - `GET /api/private/resumen` (Bearer token)
- Cliente movil ligero:
  - `GET /mobile`

## Postdeploy check

- Script:
  - `scripts/postdeploy_check.py`
  - `scripts/postdeploy_check.bat`
- Variables opcionales:
  - `POSTDEPLOY_BASE_URL`
  - `POSTDEPLOY_API_TOKEN`
