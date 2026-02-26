import argparse
import os
import shutil
import sqlite3
from datetime import datetime


def validar_sqlite(path):
    conn = sqlite3.connect(path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        ok = cursor.fetchone() is not None
    finally:
        conn.close()
    return ok


def main():
    parser = argparse.ArgumentParser(description="Restaura base SQLite desde backup.")
    parser.add_argument("--from", dest="src", required=True, help="Backup origen (.db).")
    parser.add_argument("--to", dest="dst", default=os.getenv("DB_PATH", "metas.db"), help="Base destino.")
    parser.add_argument(
        "--make-safety-copy",
        action="store_true",
        help="Crea copia de seguridad del destino antes de restaurar.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.src):
        raise FileNotFoundError(f"No existe backup origen: {args.src}")
    if not validar_sqlite(args.src):
        raise RuntimeError("El backup origen no parece una base valida de Meta90.")

    dst_dir = os.path.dirname(os.path.abspath(args.dst)) or "."
    os.makedirs(dst_dir, exist_ok=True)

    if args.make_safety_copy and os.path.exists(args.dst):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safety = os.path.join(dst_dir, f"metas_pre_restore_{ts}.db")
        shutil.copy2(args.dst, safety)
        print(f"Copia de seguridad creada: {safety}")

    shutil.copy2(args.src, args.dst)
    print(f"OK restore: {args.src} -> {args.dst}")


if __name__ == "__main__":
    main()
