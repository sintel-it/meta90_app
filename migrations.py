def _columnas_tabla(cursor, tabla):
    cursor.execute(f"PRAGMA table_info({tabla})")
    return {fila["name"] for fila in cursor.fetchall()}


def _migration_001_base_tables(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meta TEXT NOT NULL,
            monto REAL NOT NULL,
            ahorrado REAL NOT NULL,
            fecha_limite TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rate_limits (
            accion TEXT NOT NULL,
            ip TEXT NOT NULL,
            intentos INTEGER NOT NULL DEFAULT 0,
            ventana_inicio INTEGER NOT NULL,
            bloqueado_hasta INTEGER,
            PRIMARY KEY (accion, ip)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS whatsapp_notificaciones_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meta_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fecha_envio TEXT NOT NULL,
            creado_en TEXT NOT NULL
        )
        """
    )


def _migration_002_usuarios_extra(cursor):
    columnas = _columnas_tabla(cursor, "usuarios")
    if "email" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN email TEXT")
    if "reset_token" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN reset_token TEXT")
    if "reset_expira" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN reset_expira TEXT")


def _migration_003_metas_user_id(cursor):
    columnas = _columnas_tabla(cursor, "metas")
    if "user_id" not in columnas:
        cursor.execute("ALTER TABLE metas ADD COLUMN user_id INTEGER")


def _migration_004_usuarios_social(cursor):
    columnas = _columnas_tabla(cursor, "usuarios")
    if "facebook_id" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN facebook_id TEXT")
    if "telefono" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN telefono TEXT")


def _migration_005_indexes(cursor):
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_email_unique "
        "ON usuarios(email) WHERE email IS NOT NULL"
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_facebook_unique "
        "ON usuarios(facebook_id) WHERE facebook_id IS NOT NULL"
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_telefono_unique "
        "ON usuarios(telefono) WHERE telefono IS NOT NULL"
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_whatsapp_noti_unica_dia "
        "ON whatsapp_notificaciones_log(user_id, meta_id, tipo, fecha_envio)"
    )


def _migration_006_web_push(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS web_push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            endpoint TEXT NOT NULL UNIQUE,
            p256dh TEXT NOT NULL,
            auth TEXT NOT NULL,
            creado_en TEXT NOT NULL DEFAULT (datetime('now')),
            actualizado_en TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_web_push_user_id "
        "ON web_push_subscriptions(user_id)"
    )


def _migration_007_web_push_log(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS web_push_notificaciones_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fecha_envio TEXT NOT NULL,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_web_push_noti_unica_dia "
        "ON web_push_notificaciones_log(user_id, fecha_envio)"
    )


def _migration_008_email_log(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS email_notificaciones_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fecha_envio TEXT NOT NULL,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_email_noti_unica_dia "
        "ON email_notificaciones_log(user_id, fecha_envio)"
    )


def _migration_009_sms_log(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sms_notificaciones_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meta_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fecha_envio TEXT NOT NULL,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_sms_noti_unica_dia "
        "ON sms_notificaciones_log(user_id, meta_id, tipo, fecha_envio)"
    )


def _migration_010_calendario_eventos(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS calendario_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            fecha_evento TEXT NOT NULL,
            hora_evento TEXT,
            grupo TEXT,
            lugar TEXT,
            tipo TEXT,
            descripcion TEXT,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_calendario_user_fecha "
        "ON calendario_eventos(user_id, fecha_evento)"
    )


def _migration_011_mensajes(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            carpeta TEXT NOT NULL,
            remitente TEXT,
            destinatario TEXT,
            asunto TEXT NOT NULL,
            cuerpo TEXT NOT NULL,
            leido INTEGER NOT NULL DEFAULT 0,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_mensajes_user_carpeta "
        "ON mensajes(user_id, carpeta, creado_en)"
    )


def _migration_012_notificaciones_descartadas(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notificaciones_descartadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            referencia TEXT NOT NULL,
            fecha_alerta TEXT NOT NULL,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_noti_desc_unique "
        "ON notificaciones_descartadas(user_id, tipo, referencia, fecha_alerta)"
    )


def _migration_013_roles_usuarios(cursor):
    columnas = _columnas_tabla(cursor, "usuarios")
    if "rol" not in columnas:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT 'user'")

    cursor.execute("UPDATE usuarios SET rol = 'user' WHERE rol IS NULL OR trim(rol) = ''")
    cursor.execute("UPDATE usuarios SET rol = 'admin' WHERE lower(username) = 'admin'")


def _migration_014_audit_log(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_user_id INTEGER NOT NULL,
            modulo TEXT NOT NULL,
            accion TEXT NOT NULL,
            entidad TEXT NOT NULL,
            entidad_id INTEGER,
            detalle TEXT,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_actor_fecha "
        "ON audit_log(actor_user_id, creado_en DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_modulo_fecha "
        "ON audit_log(modulo, creado_en DESC)"
    )


def _migration_015_user_notification_prefs(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_notification_prefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            allow_email INTEGER NOT NULL DEFAULT 1,
            allow_sms INTEGER NOT NULL DEFAULT 1,
            allow_push INTEGER NOT NULL DEFAULT 1,
            morning_hour INTEGER NOT NULL DEFAULT 8,
            night_hour INTEGER NOT NULL DEFAULT 20,
            quiet_days TEXT,
            actualizado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_noti_prefs_user ON user_notification_prefs(user_id)"
    )


def _migration_016_saved_audit_filters(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_audit_filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            fecha_desde TEXT,
            fecha_hasta TEXT,
            actor TEXT,
            modulo TEXT,
            accion TEXT,
            detalle_q TEXT,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_saved_audit_filters_user ON saved_audit_filters(user_id, creado_en DESC)"
    )


def _migration_017_user_module_permissions(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_module_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            modulo TEXT NOT NULL,
            can_view INTEGER NOT NULL DEFAULT 1,
            can_edit INTEGER NOT NULL DEFAULT 1,
            actualizado_en TEXT NOT NULL,
            UNIQUE(user_id, modulo)
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_user_module_perm_user ON user_module_permissions(user_id)"
    )


def _migration_018_auth_login_attempts(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip TEXT NOT NULL,
            success INTEGER NOT NULL DEFAULT 0,
            creado_en TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_auth_attempts_fecha ON auth_login_attempts(creado_en DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_auth_attempts_success ON auth_login_attempts(success, creado_en DESC)"
    )


def _migration_019_api_tokens(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS api_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT,
            token_hash TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_used_at TEXT
        )
        """
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_api_tokens_user ON api_tokens(user_id, active)"
    )


def _migration_020_roles_expand(cursor):
    cursor.execute("UPDATE usuarios SET rol = 'editor' WHERE lower(coalesce(rol, '')) = 'user'")
    cursor.execute("UPDATE usuarios SET rol = 'admin' WHERE lower(username) = 'admin'")


MIGRATIONS = [
    ("001_base_tables", _migration_001_base_tables),
    ("002_usuarios_extra", _migration_002_usuarios_extra),
    ("003_metas_user_id", _migration_003_metas_user_id),
    ("004_usuarios_social", _migration_004_usuarios_social),
    ("005_indexes", _migration_005_indexes),
    ("006_web_push", _migration_006_web_push),
    ("007_web_push_log", _migration_007_web_push_log),
    ("008_email_log", _migration_008_email_log),
    ("009_sms_log", _migration_009_sms_log),
    ("010_calendario_eventos", _migration_010_calendario_eventos),
    ("011_mensajes", _migration_011_mensajes),
    ("012_notificaciones_descartadas", _migration_012_notificaciones_descartadas),
    ("013_roles_usuarios", _migration_013_roles_usuarios),
    ("014_audit_log", _migration_014_audit_log),
    ("015_user_notification_prefs", _migration_015_user_notification_prefs),
    ("016_saved_audit_filters", _migration_016_saved_audit_filters),
    ("017_user_module_permissions", _migration_017_user_module_permissions),
    ("018_auth_login_attempts", _migration_018_auth_login_attempts),
    ("019_api_tokens", _migration_019_api_tokens),
    ("020_roles_expand", _migration_020_roles_expand),
]


def apply_migrations(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    cursor.execute("SELECT version FROM schema_migrations")
    applied = {fila["version"] for fila in cursor.fetchall()}

    for version, fn in MIGRATIONS:
        if version in applied:
            continue
        fn(cursor)
        cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
