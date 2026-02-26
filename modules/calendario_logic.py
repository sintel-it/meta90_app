from datetime import datetime


def construir_contexto_redireccion_calendario(request, anio_default=None, mes_default=None):
    hoy = datetime.now()
    anio_base = anio_default if anio_default is not None else hoy.year
    mes_base = mes_default if mes_default is not None else hoy.month

    def _leer_int(nombre, default):
        valor = request.form.get(f"ctx_{nombre}", request.form.get(nombre, request.args.get(nombre, default)))
        try:
            return int(valor)
        except (TypeError, ValueError):
            return default

    anio = _leer_int("anio", anio_base)
    mes = _leer_int("mes", mes_base)
    page_eventos = max(1, _leer_int("page_eventos", 1))
    grupo = (
        request.form.get("ctx_grupo", request.form.get("grupo", request.args.get("grupo", ""))) or ""
    ).strip()
    lugar = (
        request.form.get("ctx_lugar", request.form.get("lugar", request.args.get("lugar", ""))) or ""
    ).strip()
    tipo = (
        request.form.get("ctx_tipo", request.form.get("tipo", request.args.get("tipo", ""))) or ""
    ).strip()

    return {
        "anio": anio,
        "mes": mes,
        "grupo": grupo,
        "lugar": lugar,
        "tipo": tipo,
        "page_eventos": page_eventos,
    }
