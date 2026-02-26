from flask import Blueprint


mensajes_bp = Blueprint("mensajes_bp", __name__)


def configure_mensajes_routes(deps):
    mensajes_bp.add_url_rule("/mensajes", endpoint="mensajes", view_func=deps["mensajes"])
    mensajes_bp.add_url_rule(
        "/mensajes/nuevo",
        endpoint="nuevo_mensaje",
        view_func=deps["nuevo_mensaje"],
        methods=["POST"],
    )
    mensajes_bp.add_url_rule(
        "/mensajes/mover/<int:mensaje_id>",
        endpoint="mover_mensaje",
        view_func=deps["mover_mensaje"],
        methods=["POST"],
    )
    mensajes_bp.add_url_rule(
        "/mensajes/editar/<int:mensaje_id>",
        endpoint="editar_mensaje",
        view_func=deps["editar_mensaje"],
        methods=["POST"],
    )
    mensajes_bp.add_url_rule(
        "/mensajes/eliminar/<int:mensaje_id>",
        endpoint="eliminar_mensaje",
        view_func=deps["eliminar_mensaje"],
        methods=["POST"],
    )
