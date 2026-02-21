from ewelink.classes.websocket_base import WebSocketBase
from ewelink.data.errors import errors
from ewelink.helpers.utilities import _get
from ewelink.payloads.wss_login_payload import wss_login_payload
from ewelink.payloads.wss_update_payload import wss_update_payload


class DevicePowerUsageRaw(WebSocketBase):
    APP_ID = None

    @classmethod
    def get(cls, api_url, at, api_key, device_id):
        payload_login = wss_login_payload(at=at, api_key=api_key, appid=cls.APP_ID)
        payload_update = wss_update_payload(
            api_key=api_key,
            device_id=device_id,
            params={"hundredDaysKwh": "get"},
        )

        response = cls.websocket_request(api_url, [payload_login, payload_update])

        if isinstance(response, dict) and response.get("error"):
            return response

        if len(response) == 1:
            return {"error": errors["noPower"]}

        error = _get(response[1], "error", False)
        if error == 403:
            return {"error": error, "msg": response[1].get("reason")}

        hundred_days = _get(response[1], "config.hundredDaysKwhData", False)
        if not hundred_days:
            return {"error": errors["noPower"]}

        return {
            "status": "ok",
            "data": {"hundredDaysKwhData": hundred_days},
        }
