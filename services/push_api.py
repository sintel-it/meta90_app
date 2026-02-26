import json


try:
    from pywebpush import WebPushException, webpush
except Exception:  # noqa: BLE001
    WebPushException = Exception
    webpush = None


def push_disponible():
    return webpush is not None


def enviar_web_push(subscription_info, vapid_private_key, vapid_claims, payload):
    if webpush is None:
        raise RuntimeError("pywebpush no esta instalado. Instala: pip install pywebpush")

    webpush(
        subscription_info=subscription_info,
        data=json.dumps(payload),
        vapid_private_key=vapid_private_key,
        vapid_claims=vapid_claims,
        ttl=60,
    )

