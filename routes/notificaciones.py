from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from modules import notificaciones_compose


notificaciones_bp = Blueprint("notificaciones_bp", __name__)


def configure_notificaciones_routes(deps):
    @notificaciones_bp.route("/notificaciones", endpoint="notificaciones")
    def notificaciones():
        if not deps["usuario_autenticado"]():
            return redirect(url_for("auth_bp.login"))

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            flash("Tu sesion no es valida. Vuelve a iniciar sesion.", "warning")
            return redirect(url_for("auth_bp.logout"))

        notis = deps["obtener_notificaciones_usuario"](usuario_id)
        sms_status = deps["obtener_estado_sms_operativo"]()
        return render_template("notificaciones/notificaciones.html", notis=notis, sms_status=sms_status)

    @notificaciones_bp.route("/notificaciones/enviar_movil", methods=["POST"], endpoint="enviar_notificaciones_movil")
    def enviar_notificaciones_movil():
        if not deps["usuario_autenticado"]():
            return redirect(url_for("auth_bp.login"))
        rate = deps["aplicar_rate_limit_api"]("api_push")
        if rate:
            return rate

        if not deps["sms_configurado"]():
            flash("SMS no esta configurado en el servidor.", "warning")
            return redirect(url_for("notificaciones_bp.notificaciones"))

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            flash("Tu sesion no es valida. Vuelve a iniciar sesion.", "warning")
            return redirect(url_for("auth_bp.logout"))

        resultado = deps["enviar_recordatorios_sms_usuario"](usuario_id, True)
        if resultado["enviados"] > 0:
            flash(f"Se enviaron {resultado['enviados']} notificaciones SMS a tu celular.", "success")
        elif resultado["errores"] > 0:
            detalle = resultado.get("detalle") or "Error desconocido."
            if deps["obtener_rol_usuario_actual"]() != "admin":
                detalle_lower = detalle.lower()
                if "twilio http" in detalle_lower or "code\":" in detalle_lower or "code" in detalle_lower:
                    detalle = "No se pudo enviar SMS. Revisa la verificacion del numero en Twilio o la configuracion del canal."
            flash(f"No se pudo enviar SMS al celular: {detalle}", "danger")
        else:
            flash("No habia notificaciones nuevas para enviar en esta franja.", "info")

        if resultado["omitidos"] > 0:
            flash(f"Se omitieron {resultado['omitidos']} alertas ya enviadas en esta franja.", "info")

        return redirect(url_for("notificaciones_bp.notificaciones"))

    @notificaciones_bp.route("/notificaciones/descartar", methods=["POST"], endpoint="descartar_notificacion")
    def descartar_notificacion():
        if not deps["usuario_autenticado"]():
            return redirect(url_for("auth_bp.login"))

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            flash("Tu sesion no es valida. Vuelve a iniciar sesion.", "warning")
            return redirect(url_for("auth_bp.logout"))

        tipo = request.form.get("tipo", "")
        referencia = request.form.get("referencia", "")
        ok = deps["descartar_notificacion_usuario"](usuario_id, tipo, referencia)
        if ok:
            flash("Notificacion eliminada de la vista.", "success")
        else:
            flash("No se pudo eliminar la notificacion.", "warning")
        return redirect(url_for("notificaciones_bp.notificaciones"))

    @notificaciones_bp.route("/notificaciones/descartar_todas", methods=["POST"], endpoint="descartar_todas")
    def descartar_todas():
        if not deps["usuario_autenticado"]():
            return redirect(url_for("auth_bp.login"))

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            flash("Tu sesion no es valida. Vuelve a iniciar sesion.", "warning")
            return redirect(url_for("auth_bp.logout"))

        total = deps["descartar_todas_notificaciones_usuario"](usuario_id)
        if total > 0:
            flash(f"Se ocultaron {total} notificaciones de hoy.", "success")
        else:
            flash("No habia notificaciones para ocultar.", "info")
        return redirect(url_for("notificaciones_bp.notificaciones"))

    @notificaciones_bp.route("/notificaciones/restaurar_hoy", methods=["POST"], endpoint="restaurar_hoy")
    def restaurar_hoy():
        if not deps["usuario_autenticado"]():
            return redirect(url_for("auth_bp.login"))

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            flash("Tu sesion no es valida. Vuelve a iniciar sesion.", "warning")
            return redirect(url_for("auth_bp.logout"))

        total = deps["restaurar_notificaciones_descartadas_hoy"](usuario_id)
        if total > 0:
            flash(f"Se restauraron {total} notificaciones descartadas hoy.", "success")
        else:
            flash("No habia notificaciones descartadas hoy para restaurar.", "info")
        return redirect(url_for("notificaciones_bp.notificaciones"))

    @notificaciones_bp.route("/notificaciones/push/public_key", endpoint="push_public_key")
    def push_public_key():
        if not deps["usuario_autenticado"]():
            return jsonify({"ok": False, "error": "auth_required"}), 401

        if not deps["push_web_configurado"]():
            return jsonify(
                {
                    "ok": False,
                    "error": "push_not_configured",
                    "detail": deps["push_web_estado"](),
                }
            ), 503

        return jsonify({"ok": True, "public_key": deps["push_public_key"]()})

    @notificaciones_bp.route("/notificaciones/push/subscribe", methods=["POST"], endpoint="push_subscribe")
    def push_subscribe():
        if not deps["usuario_autenticado"]():
            return jsonify({"ok": False, "error": "auth_required"}), 401
        rate = deps["aplicar_rate_limit_api"]("api_push")
        if rate:
            return rate

        if not deps["push_web_configurado"]():
            return jsonify({"ok": False, "error": "push_not_configured"}), 503

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            return jsonify({"ok": False, "error": "invalid_session"}), 401

        payload = request.get_json(silent=True) or {}
        subscription = payload.get("subscription")
        if not isinstance(subscription, dict):
            return jsonify({"ok": False, "error": "invalid_payload"}), 400

        try:
            deps["guardar_suscripcion_push"](usuario_id, subscription)
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400

        return jsonify({"ok": True})

    @notificaciones_bp.route("/notificaciones/push/test", methods=["POST"], endpoint="push_test")
    def push_test():
        if not deps["usuario_autenticado"]():
            return jsonify({"ok": False, "error": "auth_required"}), 401
        rate = deps["aplicar_rate_limit_api"]("api_push")
        if rate:
            return rate

        if not deps["push_web_configurado"]():
            return jsonify({"ok": False, "error": "push_not_configured"}), 503

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            return jsonify({"ok": False, "error": "invalid_session"}), 401

        notis = deps["obtener_notificaciones_usuario"](usuario_id)
        total = notificaciones_compose.total_alertas(notis)
        if total > 0:
            body = f"Tienes {total} alertas pendientes en Meta Inteligente."
        else:
            body = "No hay alertas pendientes por ahora."

        resultado = deps["enviar_push_usuario"](usuario_id, "Meta Inteligente", body, "/notificaciones")
        return jsonify({"ok": True, "resultado": resultado})

