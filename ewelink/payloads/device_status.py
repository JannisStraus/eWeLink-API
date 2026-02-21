from ewelink.helpers.utilities import nonce, timestamp


def device_status(appid, device_id, params):
    return {
        "deviceid": device_id,
        "appid": appid,
        "nonce": nonce,
        "ts": timestamp,
        "version": 8,
        "params": params,
    }
