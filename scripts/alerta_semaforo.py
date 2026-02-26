import json
import os
import sys
from datetime import datetime, timedelta
from urllib import request as urlrequest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORT_PATH = os.path.join(LOGS_DIR, "reporte_diario_last.json")
STATE_PATH = os.path.join(LOGS_DIR, "semaforo_alert_state.json")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import app


def read_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return {}


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=True, indent=2)


def send_webhook(payload):
    webhook = (os.getenv("ALERT_WEBHOOK_URL") or "").strip()
    if not webhook:
        return "sin_webhook"
    req = urlrequest.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=10) as _:
        return "ok"


def main():
    now = datetime.now()
    report = read_json(REPORT_PATH)
    if not report:
        print("No hay reporte diario para evaluar.")
        return

    overall_ok = bool(report.get("overall_ok"))
    critical_ok = bool(report.get("critical_ok"))
    status = "green" if overall_ok else ("yellow" if critical_ok else "red")
    print(f"Semaforo actual: {status}")
    if status != "red":
        return

    state = read_json(STATE_PATH)
    last_sent_raw = str(state.get("last_red_alert_sent") or "")
    if last_sent_raw:
        try:
            last_sent = datetime.strptime(last_sent_raw, "%Y-%m-%d %H:%M:%S")
            if now - last_sent < timedelta(hours=2):
                print("Alerta roja ya enviada hace menos de 2 horas.")
                return
        except ValueError:
            pass

    ts = now.strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[ALERTA ROJA] Semaforo Meta90 {ts}"
    detail = {
        "timestamp": ts,
        "overall_ok": overall_ok,
        "critical_ok": critical_ok,
        "reporte_timestamp": report.get("timestamp"),
    }
    body = (
        "Semaforo rojo detectado en Meta90.\n\n"
        f"- Fecha alerta: {ts}\n"
        f"- Reporte evaluado: {report.get('timestamp')}\n"
        f"- overall_ok: {overall_ok}\n"
        f"- critical_ok: {critical_ok}\n\n"
        "Revisa /admin/dashboard y logs operativos."
    )
    to_addr = (os.getenv("ALERT_EMAIL_TO") or os.getenv("SMTP_USER") or "").strip()
    if to_addr:
        app.enviar_email_generico(to_addr, subject, body)
        print(f"Alerta enviada a correo: {to_addr}")
    else:
        print("Sin ALERT_EMAIL_TO/SMTP_USER configurado.")

    try:
        send_webhook({"title": subject, "detail": detail})
        print("Alerta enviada por webhook.")
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo enviar webhook: {exc}")

    state["last_red_alert_sent"] = ts
    write_json(STATE_PATH, state)


if __name__ == "__main__":
    main()
