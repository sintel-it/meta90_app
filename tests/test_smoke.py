import sqlite3
from datetime import datetime, timedelta


def test_registro_login_restablecer_smoke(client):
    cli, temp_db = client

    username = "tester_hash"
    email = "tester_hash@example.com"
    password = "clave123"

    resp = cli.post(
        "/registro",
        data={"usuario": username, "email": email, "contrasena": password},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM usuarios WHERE username = ?", (username,))
    row = cur.fetchone()
    assert row is not None
    user_id = row["id"]
    assert row["password"] != password

    resp = cli.post(
        "/",
        data={"usuario": username, "contrasena": password},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert resp.request.path == "/inicio"

    code = "123456"
    exp = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "UPDATE usuarios SET reset_token = ?, reset_expira = ? WHERE id = ?",
        (code, exp, user_id),
    )
    conn.commit()

    new_password = "nueva1234"
    resp = cli.post(
        "/restablecer",
        data={
            "identificador": username,
            "codigo": code,
            "contrasena": new_password,
            "confirmar_contrasena": new_password,
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    cur.execute(
        "SELECT password, reset_token, reset_expira FROM usuarios WHERE id = ?",
        (user_id,),
    )
    row2 = cur.fetchone()
    assert row2 is not None
    assert row2["password"] != new_password
    assert row2["reset_token"] is None and row2["reset_expira"] is None
    conn.close()

    cli.get("/logout", follow_redirects=True)
    resp = cli.post(
        "/",
        data={"usuario": username, "contrasena": new_password},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert resp.request.path == "/inicio"


def test_health_and_admin_details(client):
    cli, _ = client

    resp = cli.get("/health")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert isinstance(payload, dict)
    assert "ok" in payload and "checks" in payload

    login = cli.post("/", data={"usuario": "admin", "contrasena": "1234"}, follow_redirects=True)
    assert login.status_code == 200

    details = cli.get("/health/details")
    assert details.status_code == 200
    details_payload = details.get_json()
    assert "env" in details_payload


def test_busqueda_global_basica(client):
    cli, _ = client
    login = cli.post("/", data={"usuario": "admin", "contrasena": "1234"}, follow_redirects=True)
    assert login.status_code == 200

    resp = cli.get("/buscar?q=admin")
    assert resp.status_code == 200
