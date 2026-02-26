import json
from urllib import error as urlerror
from urllib import request as urlrequest


def _post_whatsapp(api_version, phone_number_id, token, payload):
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=15) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"WhatsApp devolvio estado {resp.status}")
            cuerpo = resp.read().decode("utf-8", errors="ignore").strip()
            if not cuerpo:
                return {}
            try:
                return json.loads(cuerpo)
            except json.JSONDecodeError:
                return {"raw": cuerpo}
    except urlerror.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"WhatsApp HTTP {exc.code}: {detalle}") from exc


def send_text(api_version, phone_number_id, token, to, text):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text,
        },
    }
    return _post_whatsapp(api_version, phone_number_id, token, payload)


def send_template(api_version, phone_number_id, token, to, template_name, template_lang):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": template_lang},
        },
    }
    return _post_whatsapp(api_version, phone_number_id, token, payload)
