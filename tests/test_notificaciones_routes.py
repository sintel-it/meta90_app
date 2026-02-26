from datetime import datetime, timedelta


def test_descartar_y_restaurar_notificaciones_hoy(client):
    cli, _ = client

    username = "tester_noti"
    password = "clave123"
    email = "tester_noti@example.com"

    r = cli.post(
        "/registro",
        data={"usuario": username, "email": email, "contrasena": password},
        follow_redirects=True,
    )
    assert r.status_code == 200

    r = cli.post("/", data={"usuario": username, "contrasena": password}, follow_redirects=True)
    assert r.status_code == 200

    fecha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    r = cli.post(
        "/crear_meta",
        data={"meta": "Meta noti", "monto": "100", "ahorrado": "10", "fecha_limite": fecha},
        follow_redirects=True,
    )
    assert r.status_code == 200

    r = cli.post("/notificaciones/descartar_todas", follow_redirects=True)
    assert r.status_code == 200

    r = cli.post("/notificaciones/restaurar_hoy", follow_redirects=True)
    assert r.status_code == 200
