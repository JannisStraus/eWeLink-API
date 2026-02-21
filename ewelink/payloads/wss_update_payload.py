import json

from ewelink.helpers.utilities import timestamp


def wss_update_payload(api_key, device_id, params):
    payload = {
        "action": "update",
        "apikey": api_key,
        "deviceid": device_id,
        "selfApikey": api_key,
        "params": params,
        "ts": timestamp,
        "userAgent": "app",
        "sequence": int(timestamp * 1000),
    }
    return json.dumps(payload)
