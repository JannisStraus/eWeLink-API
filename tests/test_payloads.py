from __future__ import annotations

import json
import unittest
from unittest.mock import AsyncMock

from ewelink import Client


class TestPayloads(unittest.IsolatedAsyncioTestCase):
    async def test_get_credentials_payload_matches_js_shape(self) -> None:
        client = Client(email="user@example.com", password="secret")
        client._timestamp = lambda: 1234567890  # type: ignore[method-assign]
        client._nonce = lambda: "nonce123"  # type: ignore[method-assign]
        client._transport.request = AsyncMock(  # type: ignore[method-assign]
            return_value={"at": "token", "user": {"apikey": "api"}, "region": "us"}
        )

        await client.get_credentials()

        client._transport.request.assert_awaited_once_with(
            "POST",
            "/user/login",
            json_body={
                "appid": client.app_id,
                "email": "user@example.com",
                "password": "5ebe2294ecd0e0f08eab7690d2a6ee69",
                "ts": 1234567890,
                "version": 8,
                "nonce": "nonce123",
            },
            auth=False,
        )
        await client.close()

    async def test_build_power_payload_matches_js_shape(self) -> None:
        client = Client(at="token", api_key="api")
        client._timestamp = lambda: 1234567890  # type: ignore[method-assign]
        client._nonce = lambda: "nonce123"  # type: ignore[method-assign]

        payload = client._build_power_payload("device-1", "on", None)
        self.assertEqual(
            payload,
            {
                "deviceid": "device-1",
                "appid": client.app_id,
                "nonce": "nonce123",
                "ts": 1234567890,
                "version": 8,
                "params": {"switch": "on"},
            },
        )
        await client.close()

    async def test_set_device_power_state_uses_enriched_payload(self) -> None:
        client = Client(at="token", api_key="api")
        client._timestamp = lambda: 1234567890  # type: ignore[method-assign]
        client._nonce = lambda: "nonce123"  # type: ignore[method-assign]
        client.get_device = AsyncMock(return_value={"deviceid": "abc", "online": True, "params": {"switch": "off"}})  # type: ignore[method-assign]
        client._transport.request = AsyncMock(return_value={"error": 0})  # type: ignore[method-assign]

        payload = await client.set_device_power_state("abc", "on")

        self.assertEqual(payload["appid"], client.app_id)
        self.assertEqual(payload["nonce"], "nonce123")
        self.assertEqual(payload["ts"], 1234567890)
        self.assertEqual(payload["version"], 8)
        client._transport.request.assert_awaited_once_with("POST", "/user/device/status", json_body=payload)
        await client.close()

    async def test_build_wss_login_payload_matches_js_shape(self) -> None:
        client = Client(at="token", api_key="api", app_id="appid123")
        client._timestamp = lambda: 1234567890  # type: ignore[method-assign]
        client._nonce = lambda: "nonce123"  # type: ignore[method-assign]

        payload = json.loads(client._build_wss_login_payload())

        self.assertEqual(
            payload,
            {
                "action": "userOnline",
                "at": "token",
                "apikey": "api",
                "appid": "appid123",
                "nonce": "nonce123",
                "ts": 1234567890,
                "userAgent": "app",
                "sequence": 1234567890000,
                "version": 8,
            },
        )
        await client.close()


if __name__ == "__main__":
    unittest.main()
