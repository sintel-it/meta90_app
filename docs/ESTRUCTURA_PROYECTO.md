# Estructura Del Proyecto (Meta90 App)

## 1. Vista General

- `app.py`: orquestador principal de la aplicacion (config, servicios, logica y registro de blueprints).
- `routes/`: blueprints por modulo (auth, metas, calendario, mensajes, notificaciones, perfil).
- `modules/`: logica reutilizable interna (composicion de notificaciones y utilidades de dominio).
- `services/`: integraciones externas (correo, push, sms, whatsapp).
- `templates/`: vistas HTML separadas por modulo.
- `static/`: CSS, JS e imagenes.
- `migrations.py`: migraciones SQLite versionadas.
- `enviar_notificaciones_programadas.py`: runner de notificaciones automaticas.

## 2. Estructura De Templates

- `templates/base.html`
- `templates/auth/login.html`
- `templates/auth/registro.html`
- `templates/auth/registro_whatsapp.html`
- `templates/auth/recuperar.html`
- `templates/auth/restablecer.html`
- `templates/metas/inicio.html`
- `templates/metas/ver_metas.html`
- `templates/metas/editar.html`
- `templates/calendario/calendario.html`
- `templates/mensajes/mensajes.html`
- `templates/notificaciones/notificaciones.html`
- `templates/perfil/perfil.html`
- `templates/admin/dashboard.html`

## 3. Modulos (Blueprints)

- `auth_bp`: login/registro/OAuth/recuperacion.
- `metas_bp`: crear, listar, editar, eliminar metas.
- `calendario_bp`: crear, editar, eliminar y exportar eventos.
- `mensajes_bp`: entrada, enviados, papelera, editar y eliminar.
- `notificaciones_bp`: centro de alertas, push, descarte individual y masivo de alertas.
- `perfil_bp`: datos de usuario y actualizacion de perfil.
- `admin_dashboard` (ruta en `app.py`): monitoreo operativo y auditoria.

## 4. Modulos Internos (`modules/`)

- `modules/notificaciones_compose.py`:
  - calcula total de alertas
  - compone resumen push
  - compone contenido de email
  - compone items SMS
  - desacopla esta logica de `app.py`
- `modules/metas_logic.py`:
  - transforma filas de base de datos de metas para vista (`progreso`, `ahorro_diario`, formato de fecha).
- `modules/calendario_logic.py`:
  - construye contexto de redireccion del calendario (anio/mes/filtros/pagina) reutilizable.
- `modules/calendario_queries.py`:
  - consultas y transformacion de datos para el modulo calendario (filtros, lista, matriz mensual).
- `modules/mensajes_logic.py`:
  - utilidades y consultas del modulo mensajes (carpeta, busqueda, conteos, paginacion).

## 5. Migraciones

Definidas en `migrations.py` y aplicadas automaticamente al iniciar:

1. `001_base_tables`
2. `002_usuarios_extra`
3. `003_metas_user_id`
4. `004_usuarios_social`
5. `005_indexes`
6. `006_web_push`
7. `007_web_push_log`
8. `008_email_log`
9. `009_sms_log`
10. `010_calendario_eventos`
11. `011_mensajes`
12. `012_notificaciones_descartadas`
13. `013_roles_usuarios`
14. `014_audit_log`

## 6. Notificaciones Automaticas

- Script: `enviar_notificaciones_programadas.py`
- Lanzador: `run_notificaciones.bat`
- Log: `logs/notificaciones_scheduler.log`
- Tareas Windows recomendadas:
  - `Meta90_Notificaciones_Manana` (08:00)
  - `Meta90_Notificaciones_Noche` (20:00)

## 7. Convenciones Recomendadas

- Nuevas vistas: crear carpeta por modulo dentro de `templates/`.
- Nuevas rutas: agregar en `routes/` y registrar dependencias en `app.py`.
- Nuevas tablas/cambios SQL: agregar una nueva migracion al final de `MIGRATIONS`.
- Integraciones externas: encapsular en `services/`.
