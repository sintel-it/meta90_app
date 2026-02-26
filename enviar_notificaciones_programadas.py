from datetime import datetime
import json
import os

import app


def guardar_metricas(resumen, forzar_envio):
    base = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "force_each_run": bool(forzar_envio),
        "sms": {
            "usuarios_total": resumen.get("sms_usuarios_total", 0),
            "enviados": resumen.get("sms_enviados", 0),
            "omitidos": resumen.get("sms_omitidos", 0),
            "errores": resumen.get("sms_errores", 0),
            "detalle": resumen.get("sms_detalle"),
        },
        "push": {
            "usuarios_total": resumen.get("push_usuarios_total", 0),
            "enviados": resumen.get("push_enviados", 0),
            "omitidos": resumen.get("push_omitidos", 0),
            "errores": resumen.get("push_errores", 0),
            "detalle": resumen.get("push_detalle"),
        },
        "email": {
            "usuarios_total": resumen.get("email_usuarios_total", 0),
            "enviados": resumen.get("email_enviados", 0),
            "omitidos": resumen.get("email_omitidos", 0),
            "errores": resumen.get("email_errores", 0),
            "detalle": resumen.get("email_detalle"),
        },
    }

    metrics_file = os.path.join(logs_dir, "notificaciones_metrics.jsonl")
    with open(metrics_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")

    latest_file = os.path.join(logs_dir, "notificaciones_last.json")
    with open(latest_file, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=True, indent=2)


def main():
    app.crear_base_datos()
    forzar_envio = os.getenv("NOTIFICATIONS_FORCE_EACH_RUN", "0").strip() in ("1", "true", "True")
    resumen = app.enviar_recordatorios_sms_todos(forzar_envio=forzar_envio)
    guardar_metricas(resumen, forzar_envio)
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[{ahora}] SMS usuarios: {resumen.get('sms_usuarios_total', 0)} | "
        f"SMS enviados: {resumen.get('sms_enviados', 0)} | "
        f"SMS omitidos: {resumen.get('sms_omitidos', 0)} | "
        f"SMS errores: {resumen.get('sms_errores', 0)} | "
        f"SMS detalle: {resumen.get('sms_detalle') or '-'} | "
        f"Push usuarios: {resumen.get('push_usuarios_total', 0)} | "
        f"Push enviados: {resumen.get('push_enviados', 0)} | "
        f"Push omitidos: {resumen.get('push_omitidos', 0)} | "
        f"Push errores: {resumen.get('push_errores', 0)} | "
        f"Email usuarios: {resumen.get('email_usuarios_total', 0)} | "
        f"Email enviados: {resumen.get('email_enviados', 0)} | "
        f"Email omitidos: {resumen.get('email_omitidos', 0)} | "
        f"Email errores: {resumen.get('email_errores', 0)} | "
        f"Force each run: {forzar_envio}"
    )


if __name__ == "__main__":
    main()
