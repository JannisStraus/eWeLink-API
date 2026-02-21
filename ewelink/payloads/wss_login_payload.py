import json

from ewelink.helpers.utilities import nonce, timestamp


def wss_login_payload(at, api_key, appid):
    payload = {
        "action": "userOnline",
        "at": at,
        "apikey": api_key,
        "appid": appid,
        "nonce": nonce,
        "ts": timestamp,
        "userAgent": "app",
        "sequence": int(timestamp * 1000),
        "version": 8,
    }
    return json.dumps(payload)
