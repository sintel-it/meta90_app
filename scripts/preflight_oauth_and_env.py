import os
import sys


def is_truthy(value):
    return str(value or "").strip().lower() in ("1", "true", "yes", "on")


def main():
    app_env = (os.getenv("APP_ENV") or "").strip().lower()
    in_render = bool(os.getenv("RENDER"))
    is_prod = app_env in ("prod", "production") or in_render

    errors = []
    warns = []

    secret_key = (os.getenv("SECRET_KEY") or os.getenv("FLASK_SECRET_KEY") or "").strip()
    if is_prod and not secret_key:
        errors.append("Falta SECRET_KEY/FLASK_SECRET_KEY.")
    elif not secret_key:
        warns.append("SECRET_KEY/FLASK_SECRET_KEY no definido en desarrollo.")
    elif len(secret_key) < 32:
        warns.append("SECRET_KEY es corta (recomendado >= 32 caracteres).")

    database_url = (os.getenv("DATABASE_URL") or "").strip()
    if is_prod and not database_url:
        warns.append("DATABASE_URL vacia en produccion; se usara SQLite local.")

    # Google OAuth
    g_id = (os.getenv("GOOGLE_CLIENT_ID") or "").strip()
    g_secret = (os.getenv("GOOGLE_CLIENT_SECRET") or "").strip()
    g_redirect = (os.getenv("GOOGLE_REDIRECT_URI") or "").strip()
    if bool(g_id) ^ bool(g_secret):
        errors.append("Google OAuth inconsistente: define ambos GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET.")
    if g_id and ".apps.googleusercontent.com" not in g_id:
        warns.append("GOOGLE_CLIENT_ID no parece valido (falta .apps.googleusercontent.com).")
    if is_prod and g_redirect:
        errors.append("GOOGLE_REDIRECT_URI debe ir vacio en produccion (callback dinamico).")

    # Facebook OAuth
    fb_id = (os.getenv("FACEBOOK_APP_ID") or "").strip()
    fb_secret = (os.getenv("FACEBOOK_APP_SECRET") or "").strip()
    if bool(fb_id) ^ bool(fb_secret):
        errors.append("Facebook OAuth inconsistente: define ambos FACEBOOK_APP_ID y FACEBOOK_APP_SECRET.")
    if fb_id and not fb_id.isdigit():
        warns.append("FACEBOOK_APP_ID normalmente es numerico.")

    # Microsoft OAuth
    ms_id = (os.getenv("MICROSOFT_CLIENT_ID") or "").strip()
    ms_secret = (os.getenv("MICROSOFT_CLIENT_SECRET") or "").strip()
    if bool(ms_id) ^ bool(ms_secret):
        errors.append("Microsoft OAuth inconsistente: define ambos MICROSOFT_CLIENT_ID y MICROSOFT_CLIENT_SECRET.")

    cookie_secure = is_truthy(os.getenv("COOKIE_SECURE", "0"))
    if is_prod and not cookie_secure:
        errors.append("COOKIE_SECURE debe ser 1 en produccion.")

    print("Preflight entorno/OAuth")
    print(f"- entorno: {'produccion' if is_prod else 'desarrollo'}")
    print(f"- database_url: {'presente' if database_url else 'vacia'}")
    print(f"- google: {'configurado' if (g_id and g_secret) else 'desactivado/incompleto'}")
    print(f"- facebook: {'configurado' if (fb_id and fb_secret) else 'desactivado/incompleto'}")
    print(f"- microsoft: {'configurado' if (ms_id and ms_secret) else 'desactivado/incompleto'}")

    if warns:
        print("\nWARN:")
        for w in warns:
            print(f"- {w}")

    if errors:
        print("\nERROR:")
        for e in errors:
            print(f"- {e}")
        raise SystemExit(1)

    print("\nOK: preflight de entorno/OAuth correcto.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
