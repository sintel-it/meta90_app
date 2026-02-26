import os
import sys


def main():
    client_id = (os.getenv("GOOGLE_CLIENT_ID") or "").strip()
    client_secret = (os.getenv("GOOGLE_CLIENT_SECRET") or "").strip()
    redirect_uri = (os.getenv("GOOGLE_REDIRECT_URI") or "").strip()

    missing = []
    if not client_id:
        missing.append("GOOGLE_CLIENT_ID")
    if not client_secret:
        missing.append("GOOGLE_CLIENT_SECRET")
    if not redirect_uri:
        missing.append("GOOGLE_REDIRECT_URI")

    if missing:
        print("ERROR: faltan variables de Google OAuth:")
        for m in missing:
            print(f"- {m}")
        raise SystemExit(1)

    if "localhost" in redirect_uri or "127.0.0.1" in redirect_uri:
        print("WARN: GOOGLE_REDIRECT_URI apunta a local; en produccion debe ser URL publica HTTPS.")

    print("OK: configuracion base Google OAuth presente.")


if __name__ == "__main__":
    main()
