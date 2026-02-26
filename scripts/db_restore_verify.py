import os
import shutil
import sqlite3
import tempfile
from datetime import datetime


def check_db(path):
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if cur.fetchone() is None:
            raise RuntimeError("Tabla 'usuarios' no encontrada en restore.")
        cur.execute("SELECT COUNT(*) FROM usuarios")
        total = int(cur.fetchone()[0])
    finally:
        conn.close()
    return total


def main():
    backup = os.path.join("backups", "metas_latest.db")
    if not os.path.exists(backup):
        raise FileNotFoundError(f"No existe backup para verificar: {backup}")

    os.makedirs("logs", exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="meta90_restore_verify_")
    tmp_db = os.path.join(tmp_dir, "metas_verify.db")
    try:
        shutil.copy2(backup, tmp_db)
        total_users = check_db(tmp_db)
        print(
            f"OK restore verify: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"backup={backup} | usuarios={total_users}"
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
