import json
import os
import sys
from datetime import datetime
from urllib import request as urlrequest


def fetch(url, headers=None, timeout=10):
    req = urlrequest.Request(url, headers=headers or {}, method="GET")
    with urlrequest.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="ignore")
        return resp.status, body


def main():
    base = (os.getenv("POSTDEPLOY_BASE_URL") or "http://127.0.0.1:5000").rstrip("/")
    token = (os.getenv("POSTDEPLOY_API_TOKEN") or "").strip()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] postdeploy check")
    print(f"base={base}")

    errors = []
    try:
        status, body = fetch(f"{base}/health")
        print(f"/health status={status}")
        payload = json.loads(body)
        print(f"/health ok={payload.get('ok')}")
        if status != 200 or not payload.get("ok"):
            errors.append("/health no OK")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"/health error: {exc}")

    if token:
        try:
            status, body = fetch(f"{base}/api/private/resumen", headers={"Authorization": f"Bearer {token}"})
            print(f"/api/private/resumen status={status}")
            payload = json.loads(body)
            print(f"/api/private/resumen ok={payload.get('ok')}")
            if status != 200 or not payload.get("ok"):
                errors.append("/api/private/resumen no OK")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"/api/private/resumen error: {exc}")
    else:
        print("POSTDEPLOY_API_TOKEN no configurado, se omite check API privada.")

    if errors:
        print("Errores:")
        for e in errors:
            print(f"- {e}")
        raise SystemExit(1)
    print("OK postdeploy.")


if __name__ == "__main__":
    main()
