from ewelink.classes.websocket_base import WebSocketBase
from ewelink.helpers.utilities import _get
from ewelink.payloads.zeroconf_update_payload import zeroconf_update_payload


class ChangeStateZeroconf(WebSocketBase):
    @staticmethod
    def set(url, device, params, switches, state):
        import requests

        self_apikey = device["apikey"]
        device_id = device["deviceid"]
        device_key = device["devicekey"]

        endpoint = "switches" if switches else "switch"
        body = zeroconf_update_payload(self_apikey, device_id, device_key, params)

        request = requests.post(f"{url}/{endpoint}", json=body, timeout=10)
        response = request.json()

        error = _get(response, "error", False)
        if error == 403:
            return {"error": error, "msg": response.get("reason")}

        return {"status": "ok", "state": state}
