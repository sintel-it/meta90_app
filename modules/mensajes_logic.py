def carpeta_mensajes_solicitada(request):
    carpeta = request.args.get("carpeta", "entrada").strip().lower()
    if carpeta not in ("entrada", "enviados", "papelera"):
        carpeta = "entrada"
    return carpeta


def buscar_mensajes_usuario(get_connection, usuario_id, carpeta, q, limit=10, offset=0):
    q = (q or "").strip().lower()
    query = (
        "SELECT id, remitente, destinatario, asunto, cuerpo, leido, creado_en "
        "FROM mensajes WHERE user_id = ? AND carpeta = ?"
    )
    params = [usuario_id, carpeta]
    if q:
        query += (
            " AND (lower(coalesce(remitente,'')) LIKE ? OR lower(coalesce(destinatario,'')) LIKE ? "
            "OR lower(asunto) LIKE ? OR lower(cuerpo) LIKE ?)"
        )
        like = f"%{q}%"
        params.extend([like, like, like, like])
    query += " ORDER BY datetime(creado_en) DESC, id DESC LIMIT ? OFFSET ?"
    params.extend([int(limit), int(offset)])

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    filas = cursor.fetchall()
    conn.close()
    return filas


def contar_mensajes_filtrados(get_connection, usuario_id, carpeta, q):
    q = (q or "").strip().lower()
    query = "SELECT count(*) AS c FROM mensajes WHERE user_id = ? AND carpeta = ?"
    params = [usuario_id, carpeta]
    if q:
        query += (
            " AND (lower(coalesce(remitente,'')) LIKE ? OR lower(coalesce(destinatario,'')) LIKE ? "
            "OR lower(asunto) LIKE ? OR lower(cuerpo) LIKE ?)"
        )
        like = f"%{q}%"
        params.extend([like, like, like, like])
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    total = int(cursor.fetchone()["c"])
    conn.close()
    return total


def conteo_mensajes(get_connection, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    conteo = {}
    for carpeta in ("entrada", "enviados", "papelera"):
        cursor.execute(
            "SELECT count(*) AS c FROM mensajes WHERE user_id = ? AND carpeta = ?",
            (usuario_id, carpeta),
        )
        conteo[carpeta] = int(cursor.fetchone()["c"])
    conn.close()
    return conteo
