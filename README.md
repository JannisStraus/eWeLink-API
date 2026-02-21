# ewelink-api (Python)

Python async wrapper for eWeLink based on the API surface of `skydiver/ewelink-api`.

## Requirements

- Python 3.12+

## Install

```bash
pip install -e .
```

## Quick Start

```python
import asyncio
import ewelink
from ewelink import Client, DeviceOffline


@ewelink.login("your-password", "user@example.com")
async def main(client: Client) -> None:
    devices = await client.get_devices()
    print(devices)

    if not devices:
        return

    device_id = devices[0]["deviceid"]
    try:
        await client.set_device_power_state(device_id, "on")
    except DeviceOffline:
        print("Device is offline")


asyncio.run(main())
```

## Implemented API Surface

- `Client.get_region()`
- `Client.get_credentials()`
- `Client.get_devices()`
- `Client.get_device(device_id)`
- `Client.get_device_channel_count(device)`
- `Client.get_device_power_state(device, channel=0)`
- `Client.set_device_power_state(device_id, state, channel=None)`
- `Client.toggle_device(device_id, channel=None)`
- `Client.get_device_current_temperature(device)`
- `Client.get_device_current_humidity(device)`
- `Client.get_device_power_usage(device)`
- `Client.get_device_firmware_version(device)`
- `Client.open_websocket(on_message)`
- `Client.get_ws_device_power_state(device_id, channel=0)`
- `Client.set_ws_device_power_state(device_id, state, channel=None)`
- `Client.save_devices_cache(path)` / `Client.load_devices_cache(path)`
- `Client.save_arp_table(path)` / `Client.load_arp_table(path)`

## Notes

- This package uses the eWeLink cloud endpoints and requires valid account credentials.
- API behavior can vary by region/account and eWeLink backend updates.
