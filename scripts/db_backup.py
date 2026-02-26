import argparse
import os
import shutil
import sqlite3
from datetime import datetime, timedelta


def backup_sqlite(db_path, backup_dir):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No existe la base de datos: {db_path}")

    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(backup_dir, f"metas_{ts}.db")

    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(out_path)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

    return out_path


def prune_backups(backup_dir, keep_days):
    if keep_days <= 0 or not os.path.isdir(backup_dir):
        return 0

    limit = datetime.now() - timedelta(days=keep_days)
    removed = 0
    for name in os.listdir(backup_dir):
        if not name.lower().endswith(".db"):
            continue
        path = os.path.join(backup_dir, name)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
        except OSError:
            continue
        if mtime < limit:
            try:
                os.remove(path)
                removed += 1
            except OSError:
                pass
    return removed


def main():
    parser = argparse.ArgumentParser(description="Respaldo de base de datos SQLite.")
    parser.add_argument("--db", default=os.getenv("DB_PATH", "metas.db"), help="Ruta de base SQLite.")
    parser.add_argument(
        "--out-dir",
        default=os.getenv("BACKUP_DIR", "backups"),
        help="Directorio destino de respaldos.",
    )
    parser.add_argument(
        "--keep-days",
        type=int,
        default=int(os.getenv("BACKUP_KEEP_DAYS", "14")),
        help="Dias de retencion. 0 desactiva limpieza.",
    )
    parser.add_argument(
        "--latest-copy",
        default="metas_latest.db",
        help="Nombre de la copia estable mas reciente dentro de out-dir.",
    )
    parser.add_argument(
        "--offsite-dir",
        default=os.getenv("BACKUP_OFFSITE_DIR", "").strip(),
        help="Directorio offsite (carpeta sincronizada nube/red). Opcional.",
    )
    args = parser.parse_args()

    out_path = backup_sqlite(args.db, args.out_dir)
    latest_path = os.path.join(args.out_dir, args.latest_copy)
    shutil.copy2(out_path, latest_path)
    if args.offsite_dir:
        os.makedirs(args.offsite_dir, exist_ok=True)
        shutil.copy2(latest_path, os.path.join(args.offsite_dir, os.path.basename(latest_path)))
    removed = prune_backups(args.out_dir, args.keep_days)

    print(f"OK backup: {out_path}")
    print(f"OK latest: {latest_path}")
    if args.offsite_dir:
        print(f"OK offsite copy: {args.offsite_dir}")
    print(f"Backups removidos por retencion: {removed}")


if __name__ == "__main__":
    main()
