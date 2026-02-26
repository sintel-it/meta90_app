# Release Checklist (Meta90)

## 1) Seguridad

- Rotar todos los secretos expuestos historicamente:
  - `FLASK_SECRET_KEY`
  - `TWILIO_AUTH_TOKEN`
  - `WHATSAPP_TOKEN`
  - OAuth secrets (Google/Facebook/Microsoft)
  - `SMTP_PASSWORD` / `RESEND_API_KEY`
  - `PUSH_VAPID_PRIVATE_KEY`
- Confirmar:
  - `FLASK_DEBUG=0`
  - `COOKIE_SECURE=1`
  - `ENABLE_TEST_NOTIFICATIONS=0`
  - `FORCE_NOTIFICATIONS_TEST=0`
  - `NOTIFICATIONS_FORCE_EACH_RUN=0`

## 2) Integridad funcional

- Ejecutar:
  - `venv\Scripts\python.exe scripts\predeploy_check.py`
- Debe terminar con:
  - `OK: predeploy check completo.`

## 3) Hardening release

- Ejecutar:
  - `venv\Scripts\python.exe scripts\release_hardening_check.py --strict --env .env`
- O todo junto:
  - `scripts\release_final_check.bat`

## 4) Operacion programada

- Validar tareas:
  - `\Meta90_Notificaciones_Manana`
  - `\Meta90_Notificaciones_Noche`
  - `\Meta90_DB_Backup`
  - `\Meta90_DB_Restore_Verify`
  - `\Meta90_Task_Monitor`
- Recomendado:
  - ejecutar como `SYSTEM`
  - modo `Interactivo/En segundo plano`

## 5) Observabilidad

- Verificar dashboard:
  - `/admin/dashboard`
- Revisar logs:
  - `logs/notificaciones_scheduler.log`
  - `logs/db_backup.log`
  - `logs/db_restore_verify.log`
  - `logs/task_monitor.log`

## 6) Smoke en entorno publico

- Login/logout normal
- Crear/editar/eliminar meta
- Crear/editar/eliminar evento
- Mensaje interno (entrada/enviados/papelera)
- Notificacion manual admin
- Export CSV auditoria y reporte operativo

## 7) Staging antes de produccion

- Publicar primero con `render.staging.yaml`.
- Ejecutar smoke completo en staging.
- Solo luego publicar con `render.yaml`.

## 8) Migracion a Postgres (opcional recomendado)

- Definir `DATABASE_URL`.
- Ejecutar:
  - `venv\Scripts\python.exe scripts\sqlite_to_postgres.py`
- Verificar consistencia de datos y autenticacion.
