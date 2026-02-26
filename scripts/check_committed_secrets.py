import os
import re
import subprocess
import sys


PATTERNS = [
    re.compile(r"AC[a-fA-F0-9]{32}"),  # Twilio SID
    re.compile(r"SK[a-zA-Z0-9]{20,}"),  # Generic API key prefix
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),  # Google API key style
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
]

IGNORED = {".env", ".env.example", "metas.db"}


def tracked_files():
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("WARN: git no esta disponible; omitiendo chequeo de secretos versionados.")
        return []
    if proc.returncode != 0:
        print("WARN: no se pudo listar archivos git; omitiendo chequeo de secretos.")
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def main():
    bad = []
    for rel in tracked_files():
        base = os.path.basename(rel)
        if base in IGNORED:
            continue
        if rel.startswith("venv/") or rel.startswith("logs/"):
            continue
        if not os.path.exists(rel) or os.path.isdir(rel):
            continue

        try:
            with open(rel, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue

        for pattern in PATTERNS:
            if pattern.search(content):
                bad.append((rel, pattern.pattern))
                break

    if bad:
        print("ERROR: posibles secretos encontrados en archivos versionados:")
        for rel, patt in bad:
            print(f"- {rel} (pattern: {patt})")
        raise SystemExit(1)

    print("OK: no se detectaron secretos evidentes en archivos versionados.")


if __name__ == "__main__":
    main()
