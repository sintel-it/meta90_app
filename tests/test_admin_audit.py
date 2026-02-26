import sqlite3


def test_audit_log_on_meta_create_and_admin_dashboard(client):
    cli, temp_db = client

    reg = cli.post(
        "/registro",
        data={"usuario": "audit_user", "email": "audit_user@example.com", "contrasena": "1234"},
        follow_redirects=True,
    )
    assert reg.status_code == 200

    login = cli.post("/", data={"usuario": "audit_user", "contrasena": "1234"}, follow_redirects=True)
    assert login.status_code == 200

    create_meta = cli.post(
        "/crear_meta",
        data={"meta": "Meta audit", "monto": "200", "ahorrado": "20", "fecha_limite": "2026-12-31"},
        follow_redirects=True,
    )
    assert create_meta.status_code == 200

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT modulo, accion, entidad FROM audit_log WHERE modulo = 'metas' ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone()
    conn.close()
    assert row is not None
    assert row["accion"] == "crear"
    assert row["entidad"] == "meta"

    cli.get("/logout", follow_redirects=True)
    admin_login = cli.post("/", data={"usuario": "admin", "contrasena": "1234"}, follow_redirects=True)
    assert admin_login.status_code == 200

    dash = cli.get("/admin/dashboard")
    assert dash.status_code == 200
    assert b"Pagina " in dash.data

    export_resp = cli.get("/admin/audit/export.csv")
    assert export_resp.status_code == 200
    assert "text/csv" in (export_resp.content_type or "")
    body = export_resp.data.decode("utf-8", errors="ignore")
    assert "id,creado_en,actor,modulo,accion,entidad,entidad_id,detalle" in body

    users = cli.get("/admin/usuarios")
    assert users.status_code == 200

    excel = cli.get("/admin/reportes/excel")
    assert excel.status_code == 200
    assert "text/csv" in (excel.content_type or "")

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE username = 'audit_user'")
    target = cur.fetchone()
    conn.close()
    assert target is not None

    role_resp = cli.post(
        f"/admin/usuarios/{int(target['id'])}/rol",
        data={"rol": "admin"},
        follow_redirects=True,
    )
    assert role_resp.status_code == 200
