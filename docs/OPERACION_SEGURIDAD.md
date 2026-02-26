# Operacion y Seguridad

## 1) Roles

- `usuarios.rol` soporta `admin` y `user`.
- El usuario `admin` queda forzado como `admin` por migracion.
- Endpoints sensibles:
  - `GET /health/details` (solo admin)
  - `POST /admin/notificaciones/ejecutar` (solo admin)

## 2) CSRF

- Todos los `POST` de usuarios autenticados validan CSRF.
- El token va en:
  - campo oculto `_csrf_token` (formularios)
  - header `X-CSRF-Token` (fetch/AJAX)
- En `TESTING` la validacion CSRF esta desactivada para no romper pruebas.

## 3) Secretos y rotacion

- `.env` ya esta en `.gitignore`. Nunca subir credenciales reales.
- Rotar inmediatamente si algun secreto se compartio en chat o capturas:
  - `FLASK_SECRET_KEY`
  - `TWILIO_AUTH_TOKEN`
  - `RESEND_API_KEY`
  - OAuth client secrets (Google/Facebook/Microsoft)
  - `PUSH_VAPID_PRIVATE_KEY`
- Flujo recomendado de rotacion:
  1. Generar secreto nuevo en proveedor.
  2. Actualizar `.env`.
  3. Reiniciar app/tareas.
  4. Probar canal afectado.
  5. Revocar secreto anterior.

## 4) Backups y restore

- Backup manual:
  - `venv\Scripts\python.exe scripts\db_backup.py`
- Restore manual:
  - `venv\Scripts\python.exe scripts\db_restore.py --from backups\metas_latest.db --to metas.db --make-safety-copy`

- Wrappers:
  - `scripts\db_backup.bat`
  - `scripts\db_restore_latest.bat`

- Programar backup diario (ejemplo 02:00):
  - `schtasks /Create /SC DAILY /ST 02:00 /TN "Meta90_DB_Backup" /TR "C:\Users\fico8\OneDrive\Documentos\meta90_app\scripts\db_backup.bat" /RL HIGHEST /F`

## 5) Healthcheck

- `GET /health`: estado basico (db + canales).
- `GET /health/details`: incluye rutas/configuracion, solo admin.

## 6) Notificaciones (UX)

- En `/notificaciones`:
  - `Descartar todo (hoy)`
  - `Restaurar descartadas (hoy)`

## 7) CI

- Workflow: `.github/workflows/ci.yml`
- Ejecuta `python scripts/predeploy_check.py` en push y pull request.
