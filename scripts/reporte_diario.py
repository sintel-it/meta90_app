import json
import os
import sqlite3
import subprocess
import sys
import unicodedata
from datetime import datetime, timedelta
from urllib import request as urlrequest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
ENV_PATH = os.path.join(BASE_DIR, ".env")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import app


TASKS = [
    r"\Meta90_Notificaciones_Manana",
    r"\Meta90_Notificaciones_Noche",
    r"\Meta90_DB_Backup",
    r"\Meta90_DB_Restore_Verify",
    r"\Meta90_Task_Monitor",
]

LOG_FILES = [
    "notificaciones_scheduler.log",
    "db_backup.log",
    "db_restore_verify.log",
    "task_monitor.log",
]


def parse_env(path):
    values = {}
    if not os.path.exists(path):
        return values
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            values[k.strip()] = v.strip().strip('"').strip("'")
    return values


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
        return {"task": task_name, "ok": False, "detail": f"No se pudo consultar: {exc}"}

    if proc.returncode != 0:
        return {"task": task_name, "ok": False, "detail": (proc.stderr or proc.stdout or "Error").strip()}

    fields = parse_schtasks_list(proc.stdout)
    last_result = (fields.get("_last_result") or fields.get("Ultimo resultado") or fields.get("Ãšltimo resultado") or "").strip()
    status = (fields.get("_status") or fields.get("Estado") or "").strip()
    next_run = (fields.get("_next_run") or fields.get("Hora proxima ejecucion") or fields.get("Hora prÃ³xima ejecuciÃ³n") or "").strip()
    status_norm = status.lower()
    ok = last_result in {"0", "267009", "267011"} and status_norm in {"listo", "en ejecucion", "en ejecucion"}
    return {"task": task_name, "ok": ok, "detail": f"Estado={status} | Ultimo={last_result} | Proxima={next_run}"}


def check_health(url):
    try:
        req = urlrequest.Request(url, method="GET")
        with urlrequest.urlopen(req, timeout=8) as resp:
            body = resp.read().decode("utf-8", errors="ignore")
            ok = resp.status == 200
            return {"ok": ok, "status": resp.status, "detail": body[:220]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": 0, "detail": str(exc)}


def check_backups():
    if not os.path.isdir(BACKUPS_DIR):
        return {"ok": False, "count": 0, "latest": None, "detail": "No existe carpeta backups/."}
    files = []
    for name in os.listdir(BACKUPS_DIR):
        if not name.lower().endswith(".db"):
            continue
        path = os.path.join(BACKUPS_DIR, name)
        if os.path.isfile(path):
            files.append(path)
    if not files:
        return {"ok": False, "count": 0, "latest": None, "detail": "No hay backups .db."}

    latest_path = max(files, key=lambda p: os.path.getmtime(p))
    latest_ts = datetime.fromtimestamp(os.path.getmtime(latest_path))
    age = datetime.now() - latest_ts
    ok = age <= timedelta(hours=36)
    return {
        "ok": ok,
        "count": len(files),
        "latest": os.path.basename(latest_path),
        "hours_old": round(age.total_seconds() / 3600, 2),
        "detail": f"latest={os.path.basename(latest_path)} age_h={round(age.total_seconds() / 3600, 2)} total={len(files)}",
    }


def check_logs():
    out = []
    for name in LOG_FILES:
        path = os.path.join(LOGS_DIR, name)
        if not os.path.exists(path):
            out.append({"file": name, "ok": False, "errors": 0, "detail": "No existe."})
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                lines = fh.readlines()[-300:]
        except Exception as exc:  # noqa: BLE001
            out.append({"file": name, "ok": False, "errors": 0, "detail": f"No se pudo leer: {exc}"})
            continue
        fail_hits = 0
        for raw in lines:
            line = raw.strip().lower()
            if "traceback" in line:
                fail_hits += 1
            elif " fail " in f" {line} ":
                fail_hits += 1
            elif " exit=1" in line or "(exit=1)" in line:
                fail_hits += 1
            elif line.startswith("error:"):
                fail_hits += 1
        ok = fail_hits == 0
        out.append({"file": name, "ok": ok, "errors": fail_hits, "detail": f"ultimas_lineas=300 fallos={fail_hits}"})
    return out


def check_notification_metrics():
    latest_file = os.path.join(LOGS_DIR, "notificaciones_last.json")
    metrics_file = os.path.join(LOGS_DIR, "notificaciones_metrics.jsonl")
    today = datetime.now().strftime("%Y-%m-%d")
    result = {
        "ok": False,
        "runs_today": 0,
        "email_enviados_today": 0,
        "sms_enviados_today": 0,
        "push_enviados_today": 0,
        "detail": "",
    }

    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    ts = str(row.get("timestamp", ""))
                    if not ts.startswith(today):
                        continue
                    result["runs_today"] += 1
                    result["email_enviados_today"] += int(row.get("email", {}).get("enviados", 0) or 0)
                    result["sms_enviados_today"] += int(row.get("sms", {}).get("enviados", 0) or 0)
                    result["push_enviados_today"] += int(row.get("push", {}).get("enviados", 0) or 0)
        except Exception as exc:  # noqa: BLE001
            result["detail"] = f"No se pudo leer metrics: {exc}"
            return result

    if os.path.exists(latest_file):
        try:
            with open(latest_file, "r", encoding="utf-8", errors="ignore") as fh:
                last_payload = json.load(fh)
            last_ts = str(last_payload.get("timestamp", ""))
        except Exception:  # noqa: BLE001
            last_ts = "N/A"
    else:
        last_ts = "N/A"

    sent_total = result["email_enviados_today"] + result["sms_enviados_today"] + result["push_enviados_today"]
    result["ok"] = result["runs_today"] >= 1
    result["detail"] = (
        f"runs_today={result['runs_today']} sent_total={sent_total} "
        f"(email={result['email_enviados_today']} sms={result['sms_enviados_today']} push={result['push_enviados_today']}) "
        f"last={last_ts}"
    )
    return result


def check_activity_sqlite():
    db_path = os.getenv("DB_PATH", "").strip() or os.path.join(BASE_DIR, "metas.db")
    if not os.path.exists(db_path):
        return {"ok": False, "detail": f"No existe DB local: {db_path}"}

    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) c FROM metas")
        metas_total = int(cur.fetchone()["c"])
        cur.execute("SELECT COUNT(*) c FROM calendario_eventos WHERE fecha_evento = ?", (today,))
        eventos_hoy = int(cur.fetchone()["c"])
        cur.execute("SELECT COUNT(*) c FROM mensajes WHERE date(creado_en) = ?", (today,))
        mensajes_hoy = int(cur.fetchone()["c"])
    finally:
        conn.close()

    return {
        "ok": True,
        "detail": f"metas_total={metas_total} eventos_hoy={eventos_hoy} mensajes_hoy={mensajes_hoy}",
        "metas_total": metas_total,
        "eventos_hoy": eventos_hoy,
        "mensajes_hoy": mensajes_hoy,
    }


def build_report():
    env_values = parse_env(ENV_PATH)
    health_url = (
        os.getenv("REPORT_HEALTH_URL", "").strip()
        or env_values.get("REPORT_HEALTH_URL", "").strip()
        or "http://127.0.0.1:5000/health"
    )

    tasks = [check_task(t) for t in TASKS]
    health = check_health(health_url)
    backups = check_backups()
    logs = check_logs()
    metrics = check_notification_metrics()
    activity = check_activity_sqlite()

    critical_ok = all(t["ok"] for t in tasks) and health["ok"] and backups["ok"]
    logs_ok = all(x["ok"] for x in logs)
    overall_ok = critical_ok and logs_ok and metrics["ok"]

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_ok": overall_ok,
        "critical_ok": critical_ok,
        "health_url": health_url,
        "tasks": tasks,
        "health": health,
        "backups": backups,
        "logs": logs,
        "metrics": metrics,
        "activity": activity,
    }


def report_text(payload):
    lines = []
    lines.append(f"Reporte diario Meta90 [{payload['timestamp']}]")
    lines.append(f"Estado general: {'OK' if payload['overall_ok'] else 'ALERTA'}")
    lines.append("")
    lines.append("1) Tareas programadas")
    for t in payload["tasks"]:
        lines.append(f"- {'OK' if t['ok'] else 'FAIL'} {t['task']} | {t['detail']}")
    lines.append("")
    lines.append("2) Salud aplicacion")
    h = payload["health"]
    lines.append(f"- {'OK' if h['ok'] else 'FAIL'} {payload['health_url']} | status={h['status']} | {h['detail']}")
    lines.append("")
    lines.append("3) Backups")
    b = payload["backups"]
    lines.append(f"- {'OK' if b['ok'] else 'FAIL'} {b['detail']}")
    lines.append("")
    lines.append("4) Logs operativos")
    for item in payload["logs"]:
        lines.append(f"- {'OK' if item['ok'] else 'WARN'} {item['file']} | {item['detail']}")
    lines.append("")
    lines.append("5) Notificaciones del dia")
    lines.append(f"- {'OK' if payload['metrics']['ok'] else 'WARN'} {payload['metrics']['detail']}")
    lines.append("")
    lines.append("6) Actividad de modulos")
    lines.append(f"- {'OK' if payload['activity']['ok'] else 'WARN'} {payload['activity']['detail']}")
    lines.append("")
    lines.append("7) Recomendacion")
    if payload["overall_ok"]:
        lines.append("- Operacion estable. Mantener monitoreo diario.")
    else:
        lines.append("- Revisar fallos marcados como FAIL y pausar cambios visuales hasta estabilizar.")
    return "\n".join(lines)


def send_report_email(text):
    to_addr = (os.getenv("ALERT_EMAIL_TO") or os.getenv("SMTP_USER") or "").strip()
    if not to_addr:
        return "sin_destino"
    subject = f"[Meta90] Reporte diario {'OK' if 'Estado general: OK' in text else 'ALERTA'}"
    app.enviar_email_generico(to_addr, subject, text)
    return to_addr


def save_report(payload, text):
    os.makedirs(LOGS_DIR, exist_ok=True)
    json_path = os.path.join(LOGS_DIR, "reporte_diario_last.json")
    txt_path = os.path.join(LOGS_DIR, "reporte_diario_last.txt")
    hist_path = os.path.join(LOGS_DIR, "reporte_diario_historial.log")
    history_jsonl = os.path.join(LOGS_DIR, "reporte_diario_history.jsonl")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=True, indent=2)
    with open(txt_path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    with open(hist_path, "a", encoding="utf-8") as fh:
        fh.write(text + "\n" + ("=" * 70) + "\n")
    status = "green" if payload.get("overall_ok") else ("yellow" if payload.get("critical_ok") else "red")
    fail_tasks = sum(1 for t in (payload.get("tasks") or []) if not bool(t.get("ok")))
    warn_logs = sum(1 for t in (payload.get("logs") or []) if not bool(t.get("ok")))
    row = {
        "timestamp": payload.get("timestamp"),
        "status": status,
        "overall_ok": bool(payload.get("overall_ok")),
        "critical_ok": bool(payload.get("critical_ok")),
        "fail_tasks": fail_tasks,
        "warn_logs": warn_logs,
    }
    with open(history_jsonl, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def main():
    app.crear_base_datos()
    payload = build_report()
    text = report_text(payload)
    save_report(payload, text)

    try:
        sent_to = send_report_email(text)
        print(f"Reporte enviado a: {sent_to}")
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo enviar reporte por correo: {exc}")

    print(text)
    if payload["overall_ok"]:
        return
    raise SystemExit(1)


if __name__ == "__main__":
    main()
