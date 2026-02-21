import json
import threading
import time

from ewelink.classes.change_state_zeroconf import ChangeStateZeroconf
from ewelink.classes.device_power_usage_raw import DevicePowerUsageRaw
from ewelink.data.errors import errors
from ewelink.helpers.device_control import (
    VALID_POWER_STATES,
    get_all_channels_state,
    get_new_power_state,
    get_power_state_params,
    get_specific_channel_state,
)
from ewelink.helpers.ewelink import (
    get_device_channel_count as _channel_count,
    make_authorization_sign,
)
from ewelink.helpers.utilities import _empty, _get, nonce, timestamp, to_query_string
from ewelink.parsers.parse_firmware_updates import parse_firmware_updates
from ewelink.parsers.parse_power_usage import parse_power_usage
from ewelink.payloads.credentials_payload import credentials_payload
from ewelink.payloads.device_status import device_status
from ewelink.payloads.wss_login_payload import wss_login_payload

try:
    import websocket
except Exception:  # pragma: no cover
    websocket = None


def check_device_update(self, device_id):
    device = self.get_device(device_id)
    error = _get(device, "error", False)
    if error:
        return device

    device_info_list = parse_firmware_updates([device])
    device_info_list_error = _get(device_info_list, "0.error", False)
    if device_info_list_error:
        return device_info_list[0]

    update = self.make_request(
        method="post",
        url=self.get_ota_url(),
        uri="/app",
        body={"deviceInfoList": device_info_list},
    )

    is_update = _get(update, "upgradeInfoList.0.version", False)
    if not is_update:
        return {"status": "ok", "msg": "No update available"}

    return {"status": "ok", "msg": "Update available", "version": is_update}


def check_devices_updates(self):
    devices = self.get_devices()
    error = _get(devices, "error", False)
    if error:
        return devices

    device_info_list = parse_firmware_updates(devices)
    for item in device_info_list:
        if item.get("error"):
            return item

    updates = self.make_request(
        method="post",
        url=self.get_ota_url(),
        uri="/app",
        body={"deviceInfoList": device_info_list},
    )

    upgrade_info_list = _get(updates, "upgradeInfoList", False)
    if not upgrade_info_list:
        return {"error": "Can't find firmware update information"}

    parsed = []
    for device in upgrade_info_list:
        upd = _get(device, "version", False)
        if not upd:
            parsed.append(
                {
                    "status": "ok",
                    "deviceId": device.get("deviceid"),
                    "msg": "No update available",
                }
            )
        else:
            parsed.append(
                {
                    "status": "ok",
                    "deviceId": device.get("deviceid"),
                    "msg": "Update available",
                    "version": upd,
                }
            )

    return parsed


def init_device_control(self, params=None):
    if params is None:
        params = {}

    if getattr(self, "wsp", None):
        return

    if websocket is None:
        raise RuntimeError("websocket-client is required")

    delay_time = params.get("delayTime", 1000)
    self.wsDelayTime = delay_time

    if self.at is None or self.apiKey is None:
        self.get_credentials()

    dispatch = self.make_request(
        method="post",
        url=f"https://{self.region}-api.coolkit.cc:8080",
        uri="/dispatch/app",
        body={
            "accept": "ws",
            "appid": self.APP_ID,
            "nonce": nonce,
            "ts": timestamp,
            "version": 8,
        },
    )

    wss_url = f"wss://{dispatch['domain']}:{dispatch['port']}/api/ws"
    self.wsp = websocket.create_connection(wss_url)

    self.web_socket_handshake()


def web_socket_handshake(self):
    apikey = getattr(self, "deviceApiKey", None) or self.apiKey

    payload = json.dumps(
        {
            "action": "userOnline",
            "version": 8,
            "ts": timestamp,
            "at": self.at,
            "userAgent": "app",
            "apikey": apikey,
            "appid": self.APP_ID,
            "nonce": nonce,
            "sequence": int(timestamp * 1000),
        }
    )

    self.wsp.send(payload)
    time.sleep(self.wsDelayTime / 1000)


def web_socket_close(self):
    self.wsp.close()
    if hasattr(self, "wsDelayTime"):
        del self.wsDelayTime
    if hasattr(self, "wsp"):
        del self.wsp
    if hasattr(self, "deviceApiKey"):
        del self.deviceApiKey


def update_device_status(self, device_id, params):
    self.init_device_control()
    apikey = getattr(self, "deviceApiKey", None) or self.apiKey

    payload = json.dumps(
        {
            "action": "update",
            "deviceid": device_id,
            "apikey": apikey,
            "userAgent": "app",
            "sequence": int(timestamp * 1000),
            "ts": timestamp,
            "params": params,
        }
    )

    return self.wsp.send(payload)


def get_ws_device_status(self, device_id, params):
    self.init_device_control()

    apikey = getattr(self, "deviceApiKey", None) or self.apiKey
    payload = json.dumps(
        {
            "action": "query",
            "deviceid": device_id,
            "apikey": apikey,
            "userAgent": "app",
            "sequence": int(timestamp * 1000),
            "ts": timestamp,
            "params": params,
        }
    )

    self.wsp.send(payload)
    time.sleep(self.wsDelayTime / 1000)

    response = json.loads(self.wsp.recv())

    if response.get("error"):
        raise RuntimeError(errors.get(response["error"], errors["unknown"]))

    return response


def get_ws_device_power_state(self, device_id, options=None):
    if options is None:
        options = {}

    channel = options.get("channel", 1)
    all_channels = options.get("allChannels", False)
    shared = options.get("shared", False)

    if shared:
        device = self.get_device(device_id)
        self.deviceApiKey = device["apikey"]

    status = self.get_ws_device_status(device_id, ["switch", "switches"])
    self.web_socket_close()

    multi_channel = bool(status["params"].get("switches"))

    if multi_channel and all_channels:
        return {"status": "ok", "state": get_all_channels_state(status["params"])}

    if multi_channel:
        return {
            "status": "ok",
            "state": get_specific_channel_state(status["params"], channel),
            "channel": channel,
        }

    return {
        "status": "ok",
        "state": status["params"]["switch"],
        "channel": channel,
    }


def set_ws_device_power_state(self, device_id, state, options=None):
    if state not in VALID_POWER_STATES:
        raise ValueError(errors["invalidPowerState"])

    if options is None:
        options = {}

    channel = options.get("channel", 1)
    shared = options.get("shared", False)

    if shared:
        device = self.get_device(device_id)
        self.deviceApiKey = device["apikey"]

    status = self.get_ws_device_status(device_id, ["switch", "switches"])
    multi_channel = bool(status["params"].get("switches"))

    current_state = (
        status["params"]["switches"][channel - 1]["switch"]
        if multi_channel
        else status["params"]["switch"]
    )

    state_to_switch = get_new_power_state(current_state, state)
    params = get_power_state_params(status["params"], state_to_switch, channel)

    try:
        self.update_device_status(device_id, params)
        time.sleep(self.wsDelayTime / 1000)
    finally:
        self.web_socket_close()

    return {
        "status": "ok",
        "state": state_to_switch,
        "channel": channel if multi_channel else 1,
    }


def get_credentials(self):
    import requests

    body = credentials_payload(
        appid=self.APP_ID,
        email=self.email,
        phone_number=self.phoneNumber,
        password=self.password,
    )

    request = requests.post(
        f"{self.get_api_url()}/user/login",
        headers={"Authorization": f"Sign {make_authorization_sign(self.APP_SECRET, body)}"},
        json=body,
        timeout=15,
    )

    response = request.json()

    error = _get(response, "error", False)
    region = _get(response, "region", False)

    if error and int(error) in [400, 401, 404]:
        return {"error": 406, "msg": errors[406]}

    if error and int(error) == 301 and region:
        if self.region != region:
            self.region = region
            return self.get_credentials()
        return {"error": error, "msg": "Region does not exist"}

    self.apiKey = _get(response, "user.apikey", "")
    self.at = _get(response, "at", "")
    return response


def get_device(self, device_id):
    if self.devicesCache:
        for dev in self.devicesCache:
            if dev.get("deviceid") == device_id:
                return dev
        return None

    device = self.make_request(
        uri=f"/user/device/{device_id}",
        qs={
            "deviceid": device_id,
            "appid": self.APP_ID,
            "nonce": nonce,
            "ts": timestamp,
            "version": 8,
        },
    )

    error = _get(device, "error", False)
    if error:
        return {"error": error, "msg": errors.get(error)}

    return device


def get_device_channel_count(self, device_id):
    device = self.get_device(device_id)
    error = _get(device, "error", False)
    uiid = _get(device, "extra.extra.uiid", False)
    switches_amount = _channel_count(uiid)

    if error:
        return {"error": error, "msg": errors.get(error)}

    return {"status": "ok", "switchesAmount": switches_amount}


def get_device_current_th(self, device_id, kind=""):
    device = self.get_device(device_id)
    error = _get(device, "error", False)
    temperature = _get(device, "params.currentTemperature", False)
    humidity = _get(device, "params.currentHumidity", False)

    if error:
        return device

    if not temperature or not humidity:
        return {"error": 404, "msg": errors["noSensor"]}

    data = {"status": "ok", "temperature": temperature, "humidity": humidity}

    if kind == "temp":
        data.pop("humidity", None)

    if kind == "humd":
        data.pop("temperature", None)

    return data


def get_device_current_temperature(self, device_id):
    return self.get_device_current_th(device_id, "temp")


def get_device_current_humidity(self, device_id):
    return self.get_device_current_th(device_id, "humd")


def get_device_ip(self, device):
    mac = device["extra"]["extra"]["staMac"]
    arp_item = next(item for item in self.arpTable if item["mac"].lower() == mac.lower())
    return arp_item["ip"]


def get_device_power_state(self, device_id, channel=1):
    status = self.make_request(
        uri="/user/device/status",
        qs=device_status(
            appid=self.APP_ID,
            device_id=device_id,
            params="switch|switches",
        ),
    )

    error = _get(status, "error", False)
    if error:
        err = 404 if error == 400 else error
        return {"error": err, "msg": errors.get(err)}

    state = _get(status, "params.switch", False)
    switches = _get(status, "params.switches", False)
    switches_amount = len(switches) if switches else 1

    if switches_amount > 0 and switches_amount < channel:
        return {"error": 404, "msg": errors["ch404"]}

    if switches:
        state = switches[channel - 1]["switch"]

    return {"status": "ok", "state": state, "channel": channel}


def get_device_power_usage(self, device_id):
    response = self.get_device_power_usage_raw(device_id)

    error = _get(response, "error", False)
    hundred_days = _get(response, "data.hundredDaysKwhData", False)

    if error:
        return response

    parsed = parse_power_usage(hundred_days)
    return {"status": "ok", **parsed}


def get_device_power_usage_raw(self, device_id):
    device = self.get_device(device_id)
    device_api_key = _get(device, "apikey", False)

    action_params = {
        "api_url": self.get_api_websocket(),
        "at": self.at,
        "api_key": self.apiKey,
        "device_id": device_id,
    }

    if self.apiKey != device_api_key:
        action_params["api_key"] = device_api_key

    DevicePowerUsageRaw.APP_ID = self.APP_ID
    return DevicePowerUsageRaw.get(**action_params)


def get_devices(self):
    response = self.make_request(
        uri="/user/device",
        qs={
            "lang": "en",
            "appid": self.APP_ID,
            "ts": timestamp,
            "version": 8,
            "getTags": 1,
        },
    )

    error = _get(response, "error", False)
    devicelist = _get(response, "devicelist", False)

    if error:
        return {"error": error, "msg": errors.get(error)}

    if not devicelist:
        return {"error": 404, "msg": errors["noDevices"]}

    return devicelist


def get_firmware_version(self, device_id):
    device = self.get_device(device_id)
    error = _get(device, "error", False)
    fw_version = _get(device, "params.fwVersion", False)

    if error or not fw_version:
        return {"error": error, "msg": errors.get(error)}

    return {"status": "ok", "fwVersion": fw_version}


def get_region(self):
    if not self.email or not self.password:
        return {"error": 406, "msg": errors["invalidAuth"]}

    credentials = self.get_credentials()
    error = _get(credentials, "error", False)

    if error:
        return credentials

    return {
        "email": credentials["user"]["email"],
        "region": credentials["region"],
    }


def make_request(self, method="get", url=None, uri="", body=None, qs=None):
    import requests

    if body is None:
        body = {}
    if qs is None:
        qs = {}

    if not self.at:
        self.get_credentials()

    api_url = url or self.get_api_url()

    headers = {
        "Authorization": f"Bearer {self.at}",
        "Content-Type": "application/json",
    }

    query_string = to_query_string(qs) if not _empty(qs) else ""
    request_url = f"{api_url}{uri}{query_string}"

    request = requests.request(
        method.upper(),
        request_url,
        headers=headers,
        json=None if _empty(body) else body,
        timeout=15,
    )

    if not request.ok:
        return {"error": request.status_code, "msg": errors.get(request.status_code)}

    return request.json()


def open_websocket(self, callback, heartbeat=120000):
    if websocket is None:
        raise RuntimeError("websocket-client is required")

    payload_login = wss_login_payload(at=self.at, api_key=self.apiKey, appid=self.APP_ID)
    ws = websocket.create_connection(self.get_api_websocket())
    ws.send(payload_login)

    def receiver():
        while True:
            try:
                message = ws.recv()
            except Exception:
                break
            try:
                callback(json.loads(message))
            except Exception:
                callback(message)

    def heartbeater():
        while True:
            try:
                ws.send("ping")
                time.sleep(heartbeat / 1000)
            except Exception:
                break

    threading.Thread(target=receiver, daemon=True).start()
    threading.Thread(target=heartbeater, daemon=True).start()

    return ws


def save_devices_cache(self, file_name="./devices-cache.json"):
    devices = self.get_devices()
    error = _get(devices, "error", False)

    if error or not devices:
        return devices

    try:
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(devices, f, indent=2)
        return {"status": "ok", "file": file_name}
    except Exception as exc:
        return {"error": str(exc)}


def set_device_power_state(self, device_id, state, channel=1):
    device = self.get_device(device_id)
    error = _get(device, "error", False)
    uiid = _get(device, "extra.extra.uiid", False)

    status = _get(device, "params.switch", False)
    switches = _get(device, "params.switches", False)

    switches_amount = _channel_count(uiid)

    if switches_amount > 0 and switches_amount < channel:
        return {"error": 404, "msg": errors["ch404"]}

    if error or (not status and not switches):
        return {"error": error, "msg": errors.get(error)}

    state_to_switch = state
    params = {}

    if switches:
        status = switches[channel - 1]["switch"]

    if state == "toggle":
        state_to_switch = "off" if status == "on" else "on"

    if switches:
        params["switches"] = switches
        params["switches"][channel - 1]["switch"] = state_to_switch
    else:
        params["switch"] = state_to_switch

    if self.devicesCache:
        return ChangeStateZeroconf.set(
            url=self.get_zeroconf_url(device),
            device=device,
            params=params,
            switches=switches,
            state=state_to_switch,
        )

    response = self.make_request(
        method="post",
        uri="/user/device/status",
        body={
            "deviceid": device_id,
            "params": params,
            "appid": self.APP_ID,
            "nonce": nonce,
            "ts": timestamp,
            "version": 8,
        },
    )

    response_error = _get(response, "error", False)
    if response_error:
        return {"error": response_error, "msg": errors.get(response_error)}

    return {"status": "ok", "state": state, "channel": channel}


def toggle_device(self, device_id, channel=1):
    return self.set_device_power_state(device_id, "toggle", channel)
