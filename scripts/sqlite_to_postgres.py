import os
import sqlite3


def table_info_sqlite(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return cur.fetchall()


def table_columns_sqlite(conn, table):
    return [r[1] for r in table_info_sqlite(conn, table)]


def _map_sqlite_type_to_pg(sqlite_type):
    t = (sqlite_type or "").upper()
    if "INT" in t:
        return "BIGINT"
    if "REAL" in t or "FLOA" in t or "DOUB" in t:
        return "DOUBLE PRECISION"
    if "BLOB" in t:
        return "BYTEA"
    return "TEXT"


def ensure_pg_schema_from_sqlite(sqlite_conn, pg_conn, tables):
    with pg_conn.cursor() as cur:
        for table in tables:
            info = table_info_sqlite(sqlite_conn, table)
            if not info:
                continue

            pk_cols = [row[1] for row in sorted(info, key=lambda r: r[5]) if row[5]]
            col_defs = []
            for _, col_name, col_type, notnull, _, pk in info:
                pg_type = _map_sqlite_type_to_pg(col_type)
                col_def = f'"{col_name}" {pg_type}'
                if notnull:
                    col_def += " NOT NULL"
                if pk and len(pk_cols) == 1:
                    col_def += " PRIMARY KEY"
                col_defs.append(col_def)

            if len(pk_cols) > 1:
                cols = ", ".join(f'"{c}"' for c in pk_cols)
                col_defs.append(f"PRIMARY KEY ({cols})")

            cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(col_defs)})')


def fetch_all_sqlite(conn, table, cols):
    cur = conn.cursor()
    cur.execute(f"SELECT {', '.join(cols)} FROM {table}")
    return cur.fetchall()


def main():
    sqlite_path = os.getenv("DB_PATH", "metas.db")
    pg_url = (os.getenv("DATABASE_URL") or "").strip()
    if not pg_url:
        raise SystemExit("ERROR: define DATABASE_URL para migrar a Postgres.")

    try:
        import psycopg
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"ERROR: instala psycopg[binary] para migracion ({exc})")

    if not os.path.exists(sqlite_path):
        raise SystemExit(f"ERROR: no existe sqlite: {sqlite_path}")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    pg_conn = psycopg.connect(pg_url)
    pg_conn.autocommit = False

    tables = [
        "usuarios",
        "metas",
        "calendario_eventos",
        "mensajes",
        "audit_log",
        "notificaciones_descartadas",
        "rate_limits",
        "web_push_subscriptions",
        "web_push_notificaciones_log",
        "email_notificaciones_log",
        "sms_notificaciones_log",
        "whatsapp_notificaciones_log",
        "schema_migrations",
    ]

    try:
        ensure_pg_schema_from_sqlite(sqlite_conn, pg_conn, tables)
        with pg_conn.cursor() as cur:
            for table in tables:
                cols = table_columns_sqlite(sqlite_conn, table)
                if not cols:
                    continue
                rows = fetch_all_sqlite(sqlite_conn, table, cols)
                if not rows:
                    print(f"- {table}: sin datos")
                    continue

                col_list = ", ".join(cols)
                placeholders = ", ".join(["%s"] * len(cols))
                cur.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
                cur.executemany(
                    f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders})',
                    [tuple(r[c] for c in cols) for r in rows],
                )
                print(f"- {table}: {len(rows)} filas")
        pg_conn.commit()
        print("OK: migracion sqlite -> postgres completada.")
    except Exception as exc:  # noqa: BLE001
        pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
