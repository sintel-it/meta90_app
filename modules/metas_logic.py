from datetime import datetime


def construir_metas_para_vista(datos, parsear_fecha_limite):
    metas = []
    hoy = datetime.now().date()

    for fila in datos:
        fecha_limite_raw = fila["fecha_limite"]
        fecha_obj = parsear_fecha_limite(fecha_limite_raw)
        dias_restantes = (fecha_obj - hoy).days if fecha_obj else 0
        fecha_limite_mostrar = (
            fecha_obj.strftime("%Y-%m-%d") if fecha_obj else f"{fecha_limite_raw} (formato invalido)"
        )

        monto = fila["monto"]
        ahorrado = fila["ahorrado"]

        progreso = round((ahorrado / monto) * 100, 2) if monto > 0 else 0
        progreso = min(progreso, 100)

        restante = max(monto - ahorrado, 0)
        ahorro_diario = round(restante / dias_restantes, 2) if dias_restantes > 0 else 0

        metas.append(
            {
                "id": fila["id"],
                "meta": fila["meta"],
                "monto": monto,
                "ahorrado": ahorrado,
                "fecha_limite": fecha_limite_mostrar,
                "progreso": progreso,
                "ahorro_diario": ahorro_diario,
            }
        )

    return metas
