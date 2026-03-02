import os
import sys


def main():
    client_id = (os.getenv("GOOGLE_CLIENT_ID") or "").strip()
    client_secret = (os.getenv("GOOGLE_CLIENT_SECRET") or "").strip()
    redirect_uri = (os.getenv("GOOGLE_REDIRECT_URI") or "").strip()
    app_env = (os.getenv("APP_ENV") or "").strip().lower()
    in_render = bool(os.getenv("RENDER"))
    is_prod = app_env in ("prod", "production") or in_render

    missing = []
    if not client_id:
        missing.append("GOOGLE_CLIENT_ID")
    if not client_secret:
        missing.append("GOOGLE_CLIENT_SECRET")

    if missing:
        print("ERROR: faltan variables de Google OAuth:")
        for m in missing:
            print(f"- {m}")
        raise SystemExit(1)

    if is_prod and redirect_uri:
        print("ERROR: en produccion GOOGLE_REDIRECT_URI debe estar vacio (callback dinamico por host).")
        raise SystemExit(1)

    if not is_prod and redirect_uri and ("localhost" in redirect_uri or "127.0.0.1" in redirect_uri):
        print("INFO: GOOGLE_REDIRECT_URI local detectado para pruebas.")

    print("OK: configuracion base Google OAuth presente.")


if __name__ == "__main__":
    main()
