import os
import subprocess
import sys
import unicodedata
import json
from datetime import datetime
from urllib import request as urlrequest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import app


TASKS = [
    r"\Meta90_Notificaciones_Manana",
    r"\Meta90_Notificaciones_Noche",
    r"\Meta90_DB_Backup",
    r"\Meta90_DB_Restore_Verify",
]


def parse_schtasks_list(text):
    data = {}
    for raw in (text or "").splitlines():
        if ":" not in raw:
            continue
        k, v = raw.split(":", 1)
        key = k.strip()
        value = v.strip()
        data[key] = value

        norm = unicodedata.normalize("NFKD", key).encode("ascii", "ignore").decode("ascii").lower()
        if "resultado" in norm and "tiempo" not in norm:
            data["_last_result"] = value
        elif "hora" in norm and "ejecucion" in norm and "ultimo" not in norm and "tiempo" not in norm:
            data["_next_run"] = value
        elif norm == "estado":
            data["_status"] = value
    return data


def check_task(task_name):
    try:
        proc = subprocess.run(
            ["schtasks", "/Query", "/TN", task_name, "/V", "/FO", "LIST"],
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return {"task": task_name, "ok": False, "detail": f"No se pudo consultar tarea: {exc}"}

    if proc.returncode != 0:
        return {"task": task_name, "ok": False, "detail": (proc.stderr or proc.stdout or "Error").strip()}

    fields = parse_schtasks_list(proc.stdout)
    last_result = (fields.get("_last_result") or fields.get("Último resultado") or "").strip()
    status = (fields.get("_status") or fields.get("Estado") or "").strip()
    next_run = (fields.get("_next_run") or fields.get("Hora próxima ejecución") or "").strip()

    # 0: OK, 267009: en ejecucion/siendo ejecutada
    ok = last_result in {"0", "267009", "267011"} and status.lower() in {"listo", "en ejecución", "en ejecucion"}
    detail = f"Estado={status} | Ultimo={last_result} | Proxima={next_run}"
    return {"task": task_name, "ok": ok, "detail": detail}


def main():
    checks = [check_task(t) for t in TASKS]
    failed = [c for c in checks if not c["ok"]]
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{ts}] MONITOR INICIO")
    for c in checks:
        state = "OK" if c["ok"] else "FAIL"
        print(f"[{ts}] {state} {c['task']} | {c['detail']}")
    print(f"[{ts}] MONITOR FIN")

    if not failed:
        print("OK monitor: todas las tareas en estado correcto.")
        return

    webhook = (os.getenv("ALERT_WEBHOOK_URL") or "").strip()
    if webhook:
        payload = {
            "timestamp": ts,
            "title": "Alerta de tareas programadas",
            "failed": failed,
        }
        try:
            req = urlrequest.Request(
                webhook,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlrequest.urlopen(req, timeout=10) as _:
                pass
            print("ALERTA enviada por webhook.")
        except Exception as exc:  # noqa: BLE001
            print(f"No se pudo enviar alerta webhook: {exc}")

    destinatario = (os.getenv("ALERT_EMAIL_TO") or os.getenv("SMTP_USER") or "").strip()
    if not destinatario:
        print("FALLA monitor detectada, pero no hay ALERT_EMAIL_TO/SMTP_USER configurado.")
        return

    asunto = f"[ALERTA] Fallo en tareas programadas ({len(failed)})"
    cuerpo = ["Se detectaron fallos en tareas programadas:\n"]
    for c in failed:
        cuerpo.append(f"- {c['task']}: {c['detail']}")
    cuerpo.append("\nRevisa Programador de tareas y logs locales.")
    try:
        app.enviar_email_generico(destinatario, asunto, "\n".join(cuerpo))
        print(f"ALERTA enviada a {destinatario}.")
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo enviar alerta por correo: {exc}")


if __name__ == "__main__":
    main()
