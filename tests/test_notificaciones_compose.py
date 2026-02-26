from modules import notificaciones_compose as nc


def test_total_alertas_sumatoria():
    notis = {
        "por_vencer": [1, 2],
        "vencidas": [3],
        "eventos_hoy": [4],
        "eventos_proximos": [5, 6],
        "mensajes_no_leidos_total": 2,
    }
    assert nc.total_alertas(notis) == 8


def test_push_resumen_sin_alertas_y_force():
    notis = {
        "por_vencer": [],
        "vencidas": [],
        "eventos_hoy": [],
        "eventos_proximos": [],
        "mensajes_no_leidos_total": 0,
    }
    assert nc.construir_push_resumen(notis, False) is None
    assert nc.construir_push_resumen(notis, True) is None


def test_email_contiene_secciones_nuevas():
    notis = {
        "por_vencer": [{"meta": "A", "fecha_limite": "2026-02-24", "dias": 1}],
        "vencidas": [],
        "eventos_hoy": [{"titulo": "Reunion", "fecha_evento": "2026-02-24", "hora_evento": "08:00"}],
        "eventos_proximos": [],
        "mensajes_no_leidos_total": 1,
        "mensajes_no_leidos_recientes": [{"asunto": "Hola", "remitente": "admin"}],
    }
    asunto, cuerpo = nc.construir_email("demo", notis, False)
    assert "alertas" in asunto.lower()
    assert "eventos de calendario" in cuerpo.lower()
    assert "mensajes sin leer" in cuerpo.lower()
