from ewelink.data.errors import errors
from ewelink.helpers.utilities import _get


def parse_firmware_updates(devices_list):
    parsed = []
    for device in devices_list:
        model = _get(device, "extra.extra.model", False)
        fw_version = _get(device, "params.fwVersion", False)

        if not model or not fw_version:
            parsed.append({"error": 500, "msg": errors["noFirmware"]})
        else:
            parsed.append(
                {
                    "model": model,
                    "version": fw_version,
                    "deviceid": device.get("deviceid"),
                }
            )

    return parsed
