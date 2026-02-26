import os
import sqlite3
import tempfile
from datetime import datetime, timedelta

import app as m


def run_smoke_test():
    fd, temp_db = tempfile.mkstemp(prefix="meta90_test_", suffix=".db")
    os.close(fd)

    try:
        m.DB_PATH = temp_db
        m.app.config["TESTING"] = True
        m.crear_base_datos()

        client = m.app.test_client()

        username = "tester_hash"
        email = "tester_hash@example.com"
        password = "clave123"

        resp = client.post(
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
        assert row is not None, "Usuario no creado"
        user_id = row["id"]
        assert row["password"] != password, "La contrasena no se hasheo en registro"

        resp = client.post(
            "/",
            data={"usuario": username, "contrasena": password},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert resp.request.path == "/inicio", "Login inicial no redirigio a /inicio"

        code = "123456"
        exp = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "UPDATE usuarios SET reset_token = ?, reset_expira = ? WHERE id = ?",
            (code, exp, user_id),
        )
        conn.commit()

        new_password = "nueva1234"
        resp = client.post(
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
        assert row2["password"] != new_password, "La nueva contrasena quedo en texto plano"
        assert row2["reset_token"] is None and row2["reset_expira"] is None, (
            "No se limpiaron datos de recuperacion"
        )
        conn.close()

        client.get("/logout", follow_redirects=True)
        resp = client.post(
            "/",
            data={"usuario": username, "contrasena": new_password},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert resp.request.path == "/inicio", "Login con nueva clave no redirigio a /inicio"

        client.get("/logout", follow_redirects=True)
        for _ in range(5):
            client.post(
                "/",
                data={"usuario": username, "contrasena": "incorrecta"},
                follow_redirects=True,
            )
        resp = client.post(
            "/",
            data={"usuario": username, "contrasena": "incorrecta"},
            follow_redirects=True,
        )
        assert b"Demasiados intentos de inicio de sesion" in resp.data, (
            "Rate limit de login no se activo"
        )

        print("OK: smoke test completo (registro/login/restablecer con hash).")
    finally:
        try:
            os.remove(temp_db)
        except OSError:
            pass


if __name__ == "__main__":
    run_smoke_test()
