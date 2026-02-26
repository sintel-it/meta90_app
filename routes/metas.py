from flask import Blueprint


metas_bp = Blueprint("metas_bp", __name__)


def configure_metas_routes(deps):
    metas_bp.add_url_rule("/inicio", endpoint="inicio_metas", view_func=deps["inicio_metas"])
    metas_bp.add_url_rule(
        "/crear_meta",
        endpoint="crear_meta",
        view_func=deps["crear_meta"],
        methods=["POST"],
    )
    metas_bp.add_url_rule("/ver_metas", endpoint="ver_metas", view_func=deps["ver_metas"])
    metas_bp.add_url_rule("/editar/<int:meta_id>", endpoint="editar", view_func=deps["editar"])
    metas_bp.add_url_rule(
        "/actualizar/<int:meta_id>",
        endpoint="actualizar",
        view_func=deps["actualizar"],
        methods=["POST"],
    )
    metas_bp.add_url_rule(
        "/eliminar/<int:meta_id>",
        endpoint="eliminar",
        view_func=deps["eliminar"],
        methods=["POST"],
    )
