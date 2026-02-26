import subprocess
import sys


def run(cmd):
    print(f"> {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr.strip())
        raise SystemExit(proc.returncode)


def main():
    py = sys.executable
    run([py, "-m", "py_compile", "app.py", "enviar_notificaciones_programadas.py", "migrations.py"])
    run([py, "-m", "py_compile", "scripts/db_backup.py", "scripts/db_restore.py", "scripts/db_restore_verify.py"])
    run([py, "-m", "py_compile", "scripts/monitor_tareas_programadas.py"])
    run([py, "-m", "py_compile", "scripts/reporte_diario.py"])
    run([py, "-m", "py_compile", "scripts/rotate_logs.py", "scripts/alerta_semaforo.py"])
    run([py, "-m", "py_compile", "scripts/postdeploy_check.py"])
    run([py, "-m", "py_compile", "scripts/release_hardening_check.py"])
    run([py, "-m", "py_compile", "scripts/check_google_oauth.py", "scripts/sqlite_to_postgres.py"])
    run([py, "-m", "py_compile", "scripts/check_committed_secrets.py"])
    run([py, "-m", "py_compile", "routes/auth.py", "routes/calendario.py", "routes/mensajes.py"])
    run([py, "-m", "py_compile", "routes/metas.py", "routes/notificaciones.py", "routes/perfil.py"])
    run([py, "-m", "py_compile", "modules/notificaciones_compose.py", "modules/metas_logic.py"])
    run([py, "-m", "py_compile", "modules/calendario_logic.py", "modules/calendario_queries.py", "modules/mensajes_logic.py"])
    run([py, "scripts/check_committed_secrets.py"])
    run([py, "-m", "pytest", "-q"])
    print("OK: predeploy check completo.")


if __name__ == "__main__":
    main()
