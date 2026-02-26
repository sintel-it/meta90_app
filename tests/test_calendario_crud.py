import sqlite3


def _login_basico(client):
    client.post(
        "/registro",
        data={"usuario": "cal_user", "email": "cal_user@example.com", "contrasena": "1234"},
        follow_redirects=True,
    )
    resp = client.post("/", data={"usuario": "cal_user", "contrasena": "1234"}, follow_redirects=True)
    assert resp.status_code == 200


def test_calendario_editar_y_eliminar_evento(client):
    cli, db_path = client
    _login_basico(cli)

    cli.post(
        "/calendario/crear",
        data={
            "titulo": "Evento Uno",
            "fecha_evento": "2026-02-24",
            "hora_evento": "09:00",
            "grupo": "Trabajo",
            "lugar": "Oficina",
            "tipo": "Reunion",
            "descripcion": "Inicial",
        },
        follow_redirects=True,
    )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id FROM calendario_eventos ORDER BY id DESC LIMIT 1")
    ev = cur.fetchone()
    assert ev is not None
    evento_id = ev["id"]

    resp = cli.post(
        f"/calendario/editar/{evento_id}",
        data={
            "titulo": "Evento Editado",
            "fecha_evento": "2026-02-25",
            "hora_evento": "10:30",
            "grupo": "Equipo",
            "lugar": "Sala 2",
            "tipo": "Sync",
            "descripcion": "Actualizado",
            "ctx_anio": "2026",
            "ctx_mes": "2",
            "ctx_page_eventos": "1",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    cur.execute("SELECT titulo, fecha_evento, hora_evento FROM calendario_eventos WHERE id = ?", (evento_id,))
    actualizado = cur.fetchone()
    assert actualizado["titulo"] == "Evento Editado"
    assert actualizado["fecha_evento"] == "2026-02-25"
    assert actualizado["hora_evento"] == "10:30"

    resp = cli.post(
        f"/calendario/eliminar/{evento_id}",
        data={"ctx_anio": "2026", "ctx_mes": "2", "ctx_page_eventos": "1"},
        follow_redirects=True,
    )
    assert resp.status_code == 200

    cur.execute("SELECT id FROM calendario_eventos WHERE id = ?", (evento_id,))
    assert cur.fetchone() is None
    conn.close()
