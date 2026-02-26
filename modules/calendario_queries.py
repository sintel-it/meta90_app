def obtener_opciones_filtros_calendario(get_connection, usuario_id):
    conn = get_connection()
    cursor = conn.cursor()
    opciones = {}
    for campo in ("grupo", "lugar", "tipo"):
        cursor.execute(
            f"SELECT DISTINCT {campo} AS valor FROM calendario_eventos "
            "WHERE user_id = ? AND trim(coalesce(" + campo + ", '')) <> '' ORDER BY " + campo,
            (usuario_id,),
        )
        opciones[campo] = [fila["valor"] for fila in cursor.fetchall()]
    conn.close()
    return opciones


def obtener_eventos_calendario(get_connection, usuario_id, anio, mes, filtros):
    import calendar as pycalendar

    inicio = f"{anio:04d}-{mes:02d}-01"
    _, dias_mes = pycalendar.monthrange(anio, mes)
    fin = f"{anio:04d}-{mes:02d}-{dias_mes:02d}"

    query = (
        "SELECT id, titulo, fecha_evento, hora_evento, grupo, lugar, tipo, descripcion "
        "FROM calendario_eventos WHERE user_id = ? AND fecha_evento BETWEEN ? AND ?"
    )
    params = [usuario_id, inicio, fin]
    for campo in ("grupo", "lugar", "tipo"):
        valor = (filtros.get(campo) or "").strip()
        if valor:
            query += f" AND lower(coalesce({campo}, '')) = ?"
            params.append(valor.lower())
    query += " ORDER BY fecha_evento ASC, coalesce(hora_evento, '99:99') ASC, id ASC"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    filas = cursor.fetchall()
    conn.close()
    return filas


def matriz_calendario(anio, mes, eventos):
    import calendar as pycalendar

    por_dia = {}
    for fila in eventos:
        try:
            dia = int(str(fila["fecha_evento"]).split("-")[2])
        except Exception:  # noqa: BLE001
            continue
        por_dia.setdefault(dia, []).append(
            {
                "id": fila["id"],
                "titulo": fila["titulo"],
                "hora": (fila["hora_evento"] or "").strip(),
                "grupo": (fila["grupo"] or "").strip(),
                "lugar": (fila["lugar"] or "").strip(),
                "tipo": (fila["tipo"] or "").strip(),
                "descripcion": (fila["descripcion"] or "").strip(),
            }
        )

    semanas = []
    for semana in pycalendar.Calendar(firstweekday=0).monthdayscalendar(anio, mes):
        fila = []
        for dia in semana:
            fila.append(
                {
                    "dia": dia,
                    "en_mes": dia != 0,
                    "eventos": por_dia.get(dia, []) if dia != 0 else [],
                }
            )
        semanas.append(fila)
    return semanas
