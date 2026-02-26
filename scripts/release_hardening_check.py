import os
import re
import sys


PLACEHOLDER_HINTS = (
    "pega_aqui",
    "reemplaza",
    "xxxx",
    "example",
    "tu_",
)


def read_env_file(path):
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


def env_value(key, env_file_values):
    val = os.getenv(key)
    if val is not None and str(val).strip() != "":
        return str(val).strip()
    return env_file_values.get(key, "").strip()


def looks_placeholder(value):
    low = (value or "").strip().lower()
    if not low:
        return True
    return any(h in low for h in PLACEHOLDER_HINTS)


def is_truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def main():
    strict = "--strict" in sys.argv
    env_path = ".env"
    if "--env" in sys.argv:
        idx = sys.argv.index("--env")
        if idx + 1 < len(sys.argv):
            env_path = sys.argv[idx + 1]

    values = read_env_file(env_path)
    errors = []
    warnings = []

    # Security defaults
    flask_debug = env_value("FLASK_DEBUG", values) or "0"
    cookie_secure = env_value("COOKIE_SECURE", values) or "0"
    samesite = env_value("COOKIE_SAMESITE", values) or "Lax"
    secret_key = env_value("FLASK_SECRET_KEY", values)

    if is_truthy(flask_debug):
        errors.append("FLASK_DEBUG debe estar en 0 para release.")
    if not is_truthy(cookie_secure):
        errors.append("COOKIE_SECURE debe estar en 1 para release HTTPS.")
    if samesite not in {"Lax", "Strict"}:
        warnings.append("COOKIE_SAMESITE recomendado: Lax o Strict.")
    if len(secret_key) < 32 or looks_placeholder(secret_key):
        errors.append("FLASK_SECRET_KEY invalido o placeholder.")

    # Test flags off
    for key in ("ENABLE_TEST_NOTIFICATIONS", "FORCE_NOTIFICATIONS_TEST", "NOTIFICATIONS_FORCE_EACH_RUN"):
        if is_truthy(env_value(key, values) or "0"):
            errors.append(f"{key} debe estar en 0 para release.")

    # Provider sanity
    smtp_user = env_value("SMTP_USER", values)
    smtp_pass = env_value("SMTP_PASSWORD", values)
    resend_key = env_value("RESEND_API_KEY", values)
    twilio_sid = env_value("TWILIO_ACCOUNT_SID", values)
    twilio_token = env_value("TWILIO_AUTH_TOKEN", values)
    twilio_from = env_value("TWILIO_FROM_NUMBER", values)

    if smtp_user and looks_placeholder(smtp_user):
        errors.append("SMTP_USER parece placeholder.")
    if smtp_pass and looks_placeholder(smtp_pass):
        errors.append("SMTP_PASSWORD parece placeholder.")
    if resend_key and looks_placeholder(resend_key):
        errors.append("RESEND_API_KEY parece placeholder.")
    if twilio_sid and not re.match(r"^AC[a-fA-F0-9]{32}$", twilio_sid):
        warnings.append("TWILIO_ACCOUNT_SID no tiene formato esperado ACxxxxxxxx.")
    if twilio_token and len(twilio_token) < 16:
        warnings.append("TWILIO_AUTH_TOKEN parece demasiado corto.")
    if twilio_from and not twilio_from.startswith("+"):
        warnings.append("TWILIO_FROM_NUMBER deberia estar en formato E.164 (+1...).")

    # OAuth placeholders
    for key in ("GOOGLE_CLIENT_SECRET", "FACEBOOK_APP_SECRET", "MICROSOFT_CLIENT_SECRET"):
        val = env_value(key, values)
        if val and looks_placeholder(val):
            errors.append(f"{key} parece placeholder.")

    print("Release hardening check")
    print(f"- env file: {env_path}")
    print(f"- strict mode: {strict}")
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  - {e}")
        if strict:
            raise SystemExit(1)
    print("OK: validacion completada.")


if __name__ == "__main__":
    main()
