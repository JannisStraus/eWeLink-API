from __future__ import annotations

import json
from pathlib import Path

import ewelink
import os
from ewelink import Client
from ewelink.exceptions import ConfigurationError, DeviceOffline, DeviceNotFound
import unittest

class TesteWeLink(unittest.IsolatedAsyncioTestCase):
    async def test_get_region(self) -> None:
        async with Client(email=os.environ["EWELINK_EMAIL"]) as client:
            region = await client.get_region()
        self.assertEqual(region, os.environ["EWELINK_REGION"])

    async def test_get_credentials_uses_existing_tokens(self) -> None:
        async with Client(email=os.environ["EWELINK_EMAIL"], password=os.environ["EWELINK_PASSWORD"]) as client:
            creds = await client.get_credentials()
            print(creds)

    # async def test_get_credentials_requires_password(self) -> None:
    #     client = Client(email="user@example.com")
    #     with pytest.raises(ConfigurationError):
    #         await client.get_credentials()
    #     await client.close()

    # async def test_get_device_raises_if_missing(self) -> None:
    #     client = Client(at="token", api_key="api", devices_cache=[])
    #     with pytest.raises(DeviceNotFound):
    #         await client.get_device("missing")
    #     await client.close()

    # async def test_set_device_power_state_checks_offline(self) -> None:
    #     client = Client(
    #         at="token",
    #         api_key="api",
    #         devices_cache=[
    #             {"deviceid": "abc", "online": False, "params": {"switch": "off"}},
    #         ],
    #     )
    #     with pytest.raises(DeviceOffline):
    #         await client.set_device_power_state("abc", "on")
    #     await client.close()

    # async def test_channel_count_and_state(self) -> None:
    #     client = Client(at="token", api_key="api")
    #     device = {
    #         "deviceid": "multi",
    #         "params": {
    #             "switches": [
    #                 {"outlet": 0, "switch": "off"},
    #                 {"outlet": 1, "switch": "on"},
    #             ]
    #         },
    #     }
    #     assert client.get_device_channel_count(device) == 2
    #     assert client.get_device_power_state(device, channel=1) == "on"
    #     await client.close()

    # async def test_login_decorator_injects_client(self, monkeypatch: pytest.MonkeyPatch) -> None:
    #     called = False

    #     async def fake_get_credentials(self: Client) -> dict[str, str]:
    #         return {"at": "token", "apiKey": "api"}

    #     monkeypatch.setattr(Client, "get_credentials", fake_get_credentials)

    #     @ewelink.login("pass", "user@example.com")
    #     async def run(client: Client) -> str:
    #         nonlocal called
    #         called = True
    #         assert isinstance(client, Client)
    #         return "ok"

    #     assert await run() == "ok"
    #     assert called

    # async def test_devices_cache_roundtrip(self, tmp_path: Path) -> None:
    #     file_path = tmp_path / "devices-cache.json"
    #     client = Client(at="token", api_key="api", devices_cache=[{"deviceid": "one"}])
    #     await client.save_devices_cache(path=str(file_path))

    #     loaded = json.loads(file_path.read_text(encoding="utf-8"))
    #     assert loaded["devices"][0]["deviceid"] == "one"

    #     client2 = Client(at="token", api_key="api")
    #     devices = client2.load_devices_cache(path=str(file_path))
    #     assert devices[0]["deviceid"] == "one"
    #     await client.close()
    #     await client2.close()


if __name__ == "__main__":
    unittest.main()
