from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest


def send_twilio_sms(account_sid, auth_token, from_number, to_number, body):
    endpoint = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    payload = urlparse.urlencode(
        {
            "From": from_number,
            "To": to_number,
            "Body": body,
        }
    ).encode("utf-8")
    req = urlrequest.Request(endpoint, data=payload, method="POST")
    password_mgr = urlrequest.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, endpoint, account_sid, auth_token)
    auth_handler = urlrequest.HTTPBasicAuthHandler(password_mgr)
    opener = urlrequest.build_opener(auth_handler)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with opener.open(req, timeout=20) as resp:
            return {"status": resp.status}
    except urlerror.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Twilio HTTP {exc.code}: {detalle}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"No se pudo conectar con Twilio: {exc.reason}") from exc

