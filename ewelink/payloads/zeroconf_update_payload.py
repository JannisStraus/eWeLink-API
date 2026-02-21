from ewelink.helpers.ewelink import encryptation_data
from ewelink.helpers.utilities import timestamp


def zeroconf_update_payload(self_apikey, device_id, device_key, params):
    encrypted_data = encryptation_data(json_dump(params), device_key)
    return {
        "sequence": str(int(timestamp * 1000)),
        "deviceid": device_id,
        "selfApikey": self_apikey,
        "iv": encrypted_data["iv"],
        "encrypt": True,
        "data": encrypted_data["data"],
    }


def json_dump(value):
    import json

    return json.dumps(value)
