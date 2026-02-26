import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MAX_SIZE_BYTES = 2 * 1024 * 1024
KEEP_PER_PREFIX = 14


def rotate_one(path):
    if not os.path.exists(path):
        return f"SKIP {os.path.basename(path)} no existe"
    size = os.path.getsize(path)
    if size < MAX_SIZE_BYTES:
        return f"OK {os.path.basename(path)} size={size} sin rotacion"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(path)
    rotated = f"{base}.{ts}.bak"
    dst = os.path.join(LOGS_DIR, rotated)
    os.replace(path, dst)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] log rotado: {rotated}\n")
    return f"ROTATED {base} -> {rotated}"


def prune_old(prefix):
    names = []
    for name in os.listdir(LOGS_DIR):
        if name.startswith(prefix + ".") and name.endswith(".bak"):
            names.append(name)
    names.sort(reverse=True)
    removed = 0
    for old in names[KEEP_PER_PREFIX:]:
        try:
            os.remove(os.path.join(LOGS_DIR, old))
            removed += 1
        except OSError:
            continue
    return removed


def main():
    os.makedirs(LOGS_DIR, exist_ok=True)
    targets = [
        "notificaciones_scheduler.log",
        "task_monitor.log",
        "db_backup.log",
        "db_restore_verify.log",
        "reporte_diario.log",
        "reporte_diario_historial.log",
        "semaforo_alerta.log",
    ]
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ROTATE START")
    for name in targets:
        print(rotate_one(os.path.join(LOGS_DIR, name)))
        removed = prune_old(name)
        print(f"PRUNE {name} removed={removed}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ROTATE END")


if __name__ == "__main__":
    main()
