from flask import Blueprint


auth_bp = Blueprint("auth_bp", __name__)


def configure_auth_routes(deps):
    auth_bp.add_url_rule("/", endpoint="login", view_func=deps["login"], methods=["GET", "POST"])
    auth_bp.add_url_rule("/auth/admin-2fa", endpoint="admin_2fa", view_func=deps["admin_2fa"], methods=["GET", "POST"])
    auth_bp.add_url_rule("/auth/facebook/start", endpoint="facebook_start", view_func=deps["facebook_start"])
    auth_bp.add_url_rule(
        "/auth/facebook/callback",
        endpoint="facebook_callback",
        view_func=deps["facebook_callback"],
    )
    auth_bp.add_url_rule("/auth/google/start", endpoint="google_start", view_func=deps["google_start"])
    auth_bp.add_url_rule(
        "/auth/google/callback",
        endpoint="google_callback",
        view_func=deps["google_callback"],
    )
    auth_bp.add_url_rule("/auth/microsoft/start", endpoint="microsoft_start", view_func=deps["microsoft_start"])
    auth_bp.add_url_rule(
        "/auth/microsoft/callback",
        endpoint="microsoft_callback",
        view_func=deps["microsoft_callback"],
    )
    auth_bp.add_url_rule(
        "/registro",
        endpoint="registro",
        view_func=deps["registro"],
        methods=["GET", "POST"],
    )
    auth_bp.add_url_rule(
        "/registro/whatsapp",
        endpoint="registro_whatsapp",
        view_func=deps["registro_whatsapp"],
        methods=["GET", "POST"],
    )
    auth_bp.add_url_rule(
        "/recuperar",
        endpoint="recuperar_cuenta",
        view_func=deps["recuperar_cuenta"],
        methods=["GET", "POST"],
    )
    auth_bp.add_url_rule(
        "/restablecer",
        endpoint="restablecer_contrasena",
        view_func=deps["restablecer_contrasena"],
        methods=["GET", "POST"],
    )
    auth_bp.add_url_rule("/logout", endpoint="logout", view_func=deps["logout"])
