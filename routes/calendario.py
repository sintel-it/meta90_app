from flask import Blueprint


calendario_bp = Blueprint("calendario_bp", __name__)


def configure_calendario_routes(deps):
    calendario_bp.add_url_rule("/calendario", endpoint="calendario", view_func=deps["calendario"])
    calendario_bp.add_url_rule(
        "/calendario/crear",
        endpoint="crear_evento",
        view_func=deps["crear_evento"],
        methods=["POST"],
    )
    calendario_bp.add_url_rule(
        "/calendario/exportar",
        endpoint="exportar_eventos_csv",
        view_func=deps["exportar_eventos_csv"],
    )
    calendario_bp.add_url_rule(
        "/calendario/exportar-pdf",
        endpoint="exportar_eventos_pdf",
        view_func=deps["exportar_eventos_pdf"],
    )
    calendario_bp.add_url_rule(
        "/calendario/importar",
        endpoint="importar_eventos",
        view_func=deps["importar_eventos"],
        methods=["GET", "POST"],
    )
    calendario_bp.add_url_rule(
        "/calendario/importar/confirmar",
        endpoint="confirmar_importacion_eventos",
        view_func=deps["confirmar_importacion_eventos"],
        methods=["POST"],
    )
    calendario_bp.add_url_rule(
        "/calendario/editar/<int:evento_id>",
        endpoint="editar_evento",
        view_func=deps["editar_evento"],
        methods=["POST"],
    )
    calendario_bp.add_url_rule(
        "/calendario/eliminar/<int:evento_id>",
        endpoint="eliminar_evento",
        view_func=deps["eliminar_evento"],
        methods=["POST"],
    )
