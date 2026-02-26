from flask import Blueprint, flash, redirect, render_template, request, url_for


perfil_bp = Blueprint("perfil_bp", __name__)


def configure_perfil_routes(deps):
    @perfil_bp.route("/perfil", methods=["GET", "POST"], endpoint="perfil")
    def perfil():
        if not deps["usuario_autenticado"]():
            return redirect(url_for("auth_bp.login"))

        usuario_id = deps["obtener_usuario_id_actual"]()
        if usuario_id is None:
            flash("Tu sesion no es valida. Vuelve a iniciar sesion.", "warning")
            return redirect(url_for("auth_bp.logout"))

        conn = deps["get_connection"]()
        cursor = conn.cursor()

        if request.method == "POST":
            accion = (request.form.get("accion") or "perfil").strip().lower()

            if accion == "perfil":
                email = request.form["email"].strip().lower()
                telefono = deps["limpiar_telefono"](request.form.get("telefono", ""))

                if not deps["email_valido"](email):
                    conn.close()
                    flash("Ingresa un email valido.", "warning")
                    return redirect(url_for("perfil_bp.perfil"))

                cursor.execute(
                    "SELECT 1 FROM usuarios WHERE email = ? AND id <> ?",
                    (email, usuario_id),
                )
                if cursor.fetchone():
                    conn.close()
                    flash("Ese email ya esta en uso por otro usuario.", "warning")
                    return redirect(url_for("perfil_bp.perfil"))

                if telefono and len(telefono) < 10:
                    conn.close()
                    flash("Ingresa un telefono valido en formato internacional.", "warning")
                    return redirect(url_for("perfil_bp.perfil"))

                if telefono:
                    cursor.execute(
                        "SELECT 1 FROM usuarios WHERE telefono = ? AND id <> ?",
                        (telefono, usuario_id),
                    )
                    if cursor.fetchone():
                        conn.close()
                        flash("Ese telefono ya esta en uso por otro usuario.", "warning")
                        return redirect(url_for("perfil_bp.perfil"))

                telefono_guardar = telefono or None
                cursor.execute(
                    "UPDATE usuarios SET email = ?, telefono = ? WHERE id = ?",
                    (email, telefono_guardar, usuario_id),
                )
                conn.commit()
                flash("Perfil actualizado correctamente.", "success")

            elif accion == "prefs_noti":
                allow_email = 1 if request.form.get("allow_email") == "1" else 0
                allow_sms = 1 if request.form.get("allow_sms") == "1" else 0
                allow_push = 1 if request.form.get("allow_push") == "1" else 0
                try:
                    morning_hour = int(request.form.get("morning_hour", "8"))
                    night_hour = int(request.form.get("night_hour", "20"))
                except ValueError:
                    morning_hour = 8
                    night_hour = 20
                morning_hour = min(12, max(5, morning_hour))
                night_hour = min(23, max(17, night_hour))
                quiet_days = ",".join(request.form.getlist("quiet_days"))
                deps["guardar_prefs_noti"](
                    usuario_id,
                    {
                        "allow_email": allow_email,
                        "allow_sms": allow_sms,
                        "allow_push": allow_push,
                        "morning_hour": morning_hour,
                        "night_hour": night_hour,
                        "quiet_days": quiet_days,
                    },
                )
                flash("Preferencias de notificaciones actualizadas.", "success")

            elif accion == "api_token_new":
                nombre = (request.form.get("token_name") or "principal").strip()
                token = deps["generar_api_token_usuario"](usuario_id, nombre)
                flash(f"Nuevo token API: {token}", "warning")

            elif accion == "api_token_revoke":
                try:
                    token_id = int(request.form.get("token_id", "0"))
                except ValueError:
                    token_id = 0
                if token_id > 0 and deps["revocar_api_token_usuario"](usuario_id, token_id):
                    flash("Token API revocado.", "info")
                else:
                    flash("No se pudo revocar el token.", "warning")

        cursor.execute("SELECT username, email, telefono FROM usuarios WHERE id = ?", (usuario_id,))
        user = cursor.fetchone()
        conn.close()
        prefs_noti = deps["obtener_prefs_noti"](usuario_id)
        api_tokens = deps["listar_api_tokens_usuario"](usuario_id)
        return render_template("perfil/perfil.html", user=user, prefs_noti=prefs_noti, api_tokens=api_tokens)

