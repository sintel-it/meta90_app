def total_alertas(notis):
    return (
        len(notis.get("por_vencer", []))
        + len(notis.get("vencidas", []))
        + len(notis.get("metas_rezagadas", []))
        + len(notis.get("eventos_hoy", []))
        + len(notis.get("eventos_proximos", []))
        + int(notis.get("mensajes_no_leidos_total", 0))
    )


def construir_push_resumen(notis, force_test=False):
    metas_total = len(notis.get("por_vencer", [])) + len(notis.get("vencidas", [])) + len(notis.get("metas_rezagadas", []))
    eventos_total = len(notis.get("eventos_hoy", [])) + len(notis.get("eventos_proximos", []))
    mensajes_total = int(notis.get("mensajes_no_leidos_total", 0))
    total = metas_total + eventos_total + mensajes_total
    if total <= 0:
        return None

    partes = []
    if metas_total:
        partes.append(f"metas {metas_total}")
    if eventos_total:
        partes.append(f"calendario {eventos_total}")
    if mensajes_total:
        partes.append(f"mensajes {mensajes_total}")
    return f"Tienes {total} alertas: {', '.join(partes)}."


def construir_sms_items(notis):
    mensajes = []

    for item in notis.get("vencidas", []):
        mensajes.append(
            {
                "meta_id": item["id"],
                "tipo": "meta_vencida",
                "texto": (
                    f"meta_90.app: Tu meta '{item['meta']}' vencio hace {item['dias']} dias "
                    f"(fecha limite {item['fecha_limite']})."
                ),
            }
        )

    for item in notis.get("por_vencer", []):
        mensajes.append(
            {
                "meta_id": item["id"],
                "tipo": "meta_por_vencer",
                "texto": (
                    f"meta_90.app: Tu meta '{item['meta']}' vence en {item['dias']} dias "
                    f"(fecha limite {item['fecha_limite']})."
                ),
            }
        )

    for item in notis.get("metas_rezagadas", []):
        mensajes.append(
            {
                "meta_id": item["id"],
                "tipo": "meta_rezago",
                "texto": (
                    f"meta_90.app: Tu meta '{item['meta']}' tiene avance bajo ({item['porcentaje']}%). "
                    f"Faltan {item['dias']} dias y te faltan {item['faltante']}."
                ),
            }
        )

    for item in notis.get("eventos_hoy", []):
        hora = f" {item['hora_evento']}" if item.get("hora_evento") else ""
        mensajes.append(
            {
                "meta_id": -int(item["id"]),
                "tipo": "calendario_hoy",
                "texto": f"meta_90.app: Hoy tienes el evento '{item['titulo']}' ({item['fecha_evento']}{hora}).",
            }
        )

    for item in notis.get("eventos_proximos", []):
        hora = f" {item['hora_evento']}" if item.get("hora_evento") else ""
        mensajes.append(
            {
                "meta_id": -int(item["id"]),
                "tipo": "calendario_proximo",
                "texto": (
                    f"meta_90.app: Evento proximo '{item['titulo']}' en {item['dias']} dias "
                    f"({item['fecha_evento']}{hora})."
                ),
            }
        )

    mensajes_no_leidos = int(notis.get("mensajes_no_leidos_total", 0))
    if mensajes_no_leidos > 0:
        mensajes.append(
            {
                "meta_id": -900000,
                "tipo": "mensajes_no_leidos",
                "texto": f"meta_90.app: Tienes {mensajes_no_leidos} mensaje(s) sin leer en tu bandeja de entrada.",
            }
        )

    return mensajes


def construir_email(username, notis, force_test=False):
    por_vencer = notis.get("por_vencer", [])
    vencidas = notis.get("vencidas", [])
    metas_rezagadas = notis.get("metas_rezagadas", [])
    eventos_hoy = notis.get("eventos_hoy", [])
    eventos_proximos = notis.get("eventos_proximos", [])
    mensajes_no_leidos = int(notis.get("mensajes_no_leidos_total", 0))
    mensajes_recientes = notis.get("mensajes_no_leidos_recientes", [])
    total = len(por_vencer) + len(vencidas) + len(metas_rezagadas) + len(eventos_hoy) + len(eventos_proximos) + mensajes_no_leidos
    if total <= 0:
        return None, None

    asunto = f"Recordatorio de alertas ({total}) - Meta Inteligente"
    lineas = [
        f"Hola {username},",
        "",
        f"Tienes {total} notificaciones activas.",
        "",
    ]
    if por_vencer:
        lineas.append(f"Metas por vencer ({len(por_vencer)}):")
        for item in por_vencer:
            lineas.append(f"- {item['meta']} | vence {item['fecha_limite']} | faltan {item['dias']} dias")
        lineas.append("")
    if vencidas:
        lineas.append(f"Metas vencidas ({len(vencidas)}):")
        for item in vencidas:
            lineas.append(f"- {item['meta']} | vencio {item['fecha_limite']} | hace {item['dias']} dias")
        lineas.append("")
    if metas_rezagadas:
        lineas.append(f"Metas con avance bajo ({len(metas_rezagadas)}):")
        for item in metas_rezagadas:
            lineas.append(
                f"- {item['meta']} | avance {item['porcentaje']}% | faltante {item['faltante']} | faltan {item['dias']} dias"
            )
        lineas.append("")
    if eventos_hoy:
        lineas.append(f"Eventos de calendario para hoy ({len(eventos_hoy)}):")
        for item in eventos_hoy:
            hora = f" {item['hora_evento']}" if item.get("hora_evento") else ""
            lineas.append(f"- {item['titulo']} | {item['fecha_evento']}{hora}")
        lineas.append("")
    if eventos_proximos:
        lineas.append(f"Eventos proximos (1-3 dias) ({len(eventos_proximos)}):")
        for item in eventos_proximos:
            hora = f" {item['hora_evento']}" if item.get("hora_evento") else ""
            lineas.append(f"- {item['titulo']} | {item['fecha_evento']}{hora} | faltan {item['dias']} dias")
        lineas.append("")
    if mensajes_no_leidos:
        lineas.append(f"Mensajes sin leer: {mensajes_no_leidos}")
        for item in mensajes_recientes:
            lineas.append(f"- {item['asunto']} | de {item['remitente']}")
        lineas.append("")
    lineas.append("Ingresa a Meta Inteligente para revisar tus pendientes.")
    return asunto, "\n".join(lineas)
