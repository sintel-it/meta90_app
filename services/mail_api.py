import json
import smtplib
import ssl
from email.message import EmailMessage
from urllib import error as urlerror
from urllib import request as urlrequest


def send_resend(api_key, sender, to, subject, body):
    payload = {
        "from": sender,
        "to": [to],
        "subject": subject,
        "text": body,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        "https://api.resend.com/emails",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=15) as resp:
            if resp.status not in (200, 202):
                raise RuntimeError(f"Resend devolvio estado {resp.status}")
    except urlerror.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Resend HTTP {exc.code}: {detalle}") from exc


def send_smtp(host, port, user, password, sender, to, subject, body, use_tls):
    mensaje = EmailMessage()
    mensaje["Subject"] = subject
    mensaje["From"] = sender
    mensaje["To"] = to
    mensaje.set_content(body)

    if use_tls:
        contexto = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=15) as servidor:
            servidor.starttls(context=contexto)
            servidor.login(user, password)
            servidor.send_message(mensaje)
        return

    with smtplib.SMTP_SSL(host, port, timeout=15) as servidor:
        servidor.login(user, password)
        servidor.send_message(mensaje)
