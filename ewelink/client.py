"""High-level eWeLink client."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from hashlib import md5
from typing import Any
from uuid import uuid4

from .exceptions import AuthenticationError, ConfigurationError, DeviceNotFound, DeviceOffline
from .http import DEFAULT_REGION, HttpTransport
from .models import Credentials, Device
from .zeroconf import load_arp_table, load_devices_cache, save_arp_table, save_devices_cache

DEFAULT_APP_ID = "oeVkj2lYFGnJu5XUtWisfW4utiN4u9Mq"
DEFAULT_APP_SECRET = ""  # optional, endpoint behavior may vary by account region


class Client:
    """Async eWeLink client inspired by skydiver/ewelink-api."""

    def __init__(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        phone_number: str | None = None,
        region: str = DEFAULT_REGION,
        at: str | None = None,
        api_key: str | None = None,
        app_id: str = DEFAULT_APP_ID,
        app_secret: str = DEFAULT_APP_SECRET,
        timeout: float = 10.0,
        devices_cache: list[dict[str, Any]] | None = None,
        arp_table: dict[str, str] | None = None,
    ) -> None:
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.region = region
        self.at = at
        self.api_key = api_key
        self.app_id = app_id
        self.app_secret = app_secret
        self._transport = HttpTransport(region=region, app_id=app_id, timeout=timeout)
        self._transport.update_auth(at=at, api_key=api_key, region=region)
        self._devices_cache = devices_cache
        self._arp_table = arp_table

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._transport.close()

    async def get_region(self) -> str:
        if self.region:
            return self.region
        if not self.email and not self.phone_number:
            raise ConfigurationError("email or phone_number is required to determine region")

        payload: dict[str, Any] = {}
        if self.email:
            payload["email"] = self.email
        if self.phone_number:
            payload["phoneNumber"] = self.phone_number

        response = await self._transport.request(
            "POST",
            "/user/region",
            json_body=payload,
            auth=False,
            absolute_url="https://app-api.coolkit.cc:8080/api/user/region",
        )
        data = response.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("region"), str):
            raise AuthenticationError("failed to detect account region")
        self.region = data["region"]
        self._transport.update_auth(at=self.at, api_key=self.api_key, region=self.region)
        return self.region

    async def get_credentials(self) -> Credentials:
        if self.at and self.api_key:
            return {"at": self.at, "apiKey": self.api_key, "region": self.region}

        if not self.password or (not self.email and not self.phone_number):
            raise ConfigurationError("password and email/phone_number are required for login")

        payload: dict[str, Any] = {
            "password": md5(self.password.encode("utf-8")).hexdigest(),
            "version": 8,
            "ts": int(datetime.now(UTC).timestamp()),
            "nonce": uuid4().hex,
        }
        if self.email:
            payload["email"] = self.email
        if self.phone_number:
            payload["phoneNumber"] = self.phone_number

        response = await self._transport.request("POST", "/user/login", json_body=payload, auth=False)
        at = response.get("at")
        user = response.get("user")
        if not isinstance(at, str) or not isinstance(user, dict):
            raise AuthenticationError("login response missing token or user")

        api_key = user.get("apikey") or user.get("apiKey")
        if not isinstance(api_key, str):
            raise AuthenticationError("login response missing apiKey")

        self.at = at
        self.api_key = api_key
        self.region = str(response.get("region") or self.region)
        self._transport.update_auth(at=self.at, api_key=self.api_key, region=self.region)
        return {"at": self.at, "apiKey": self.api_key, "region": self.region, "user": user}

    async def get_devices(self, *, refresh: bool = False) -> list[Device]:
        if self._devices_cache is not None and not refresh:
            return [device for device in self._devices_cache if isinstance(device, dict)]

        await self.get_credentials()
        response = await self._transport.request("GET", "/user/device")
        devices = response.get("devicelist") or response.get("data") or []
        if not isinstance(devices, list):
            return []
        parsed: list[Device] = [device for device in devices if isinstance(device, dict)]
        self._devices_cache = parsed
        return parsed

    async def get_device(self, device_id: str) -> Device:
        for device in await self.get_devices():
            if device.get("deviceid") == device_id:
                return device
        raise DeviceNotFound(f"device not found: {device_id}")

    def get_device_channel_count(self, device: Device) -> int:
        params = device.get("params") or {}
        switches = params.get("switches")
        if isinstance(switches, list):
            return len(switches)
        if isinstance(params.get("switch"), str):
            return 1
        return 0

    def get_device_power_state(self, device: Device, *, channel: int = 0) -> str | None:
        params = device.get("params") or {}
        switches = params.get("switches")
        if isinstance(switches, list):
            if channel < 0 or channel >= len(switches):
                raise IndexError(f"channel index out of range: {channel}")
            target = switches[channel]
            if isinstance(target, dict):
                value = target.get("switch")
                return value if isinstance(value, str) else None
            return None

        switch = params.get("switch")
        return switch if isinstance(switch, str) else None

    def _build_power_payload(self, device_id: str, state: str, channel: int | None) -> dict[str, Any]:
        if channel is None:
            return {"deviceid": device_id, "params": {"switch": state}}
        return {
            "deviceid": device_id,
            "params": {
                "switches": [{"outlet": channel, "switch": state}],
            },
        }

    async def set_device_power_state(self, device_id: str, state: str, *, channel: int | None = None) -> dict[str, Any]:
        if state not in {"on", "off"}:
            raise ValueError("state must be 'on' or 'off'")

        device = await self.get_device(device_id)
        if not device.get("online", True):
            raise DeviceOffline(f"device is offline: {device_id}")

        payload = self._build_power_payload(device_id, state, channel)
        await self._transport.request("POST", "/user/device/status", json_body=payload)
        return payload

    async def toggle_device(self, device_id: str, *, channel: int | None = None) -> dict[str, Any]:
        device = await self.get_device(device_id)
        current = self.get_device_power_state(device, channel=channel or 0)
        next_state = "off" if current == "on" else "on"
        return await self.set_device_power_state(device_id, next_state, channel=channel)

    def get_device_current_temperature(self, device: Device) -> float | None:
        params = device.get("params") or {}
        for key in ("currentTemperature", "temperature", "temp"):
            value = params.get(key)
            if isinstance(value, (int, float, str)):
                try:
                    return float(value)
                except ValueError:
                    return None
        return None

    def get_device_current_humidity(self, device: Device) -> float | None:
        params = device.get("params") or {}
        for key in ("currentHumidity", "humidity"):
            value = params.get(key)
            if isinstance(value, (int, float, str)):
                try:
                    return float(value)
                except ValueError:
                    return None
        return None

    def get_device_power_usage(self, device: Device) -> float | None:
        params = device.get("params") or {}
        for key in ("power", "currentPower", "fwPower"):
            value = params.get(key)
            if isinstance(value, (int, float, str)):
                try:
                    return float(value)
                except ValueError:
                    return None
        return None

    def get_device_firmware_version(self, device: Device) -> str | None:
        extra = device.get("extra") or {}
        value = extra.get("fwVersion")
        return value if isinstance(value, str) else None

    async def save_devices_cache(self, path: str = "devices-cache.json") -> list[Device]:
        devices = await self.get_devices(refresh=True)
        save_devices_cache(list(devices), path=path)
        return devices

    def load_devices_cache(self, path: str = "devices-cache.json") -> list[dict[str, Any]]:
        devices = load_devices_cache(path=path)
        self._devices_cache = devices
        return devices

    def save_arp_table(self, path: str = "arp-table.json") -> dict[str, str]:
        table = save_arp_table(path=path)
        self._arp_table = table
        return table

    def load_arp_table(self, path: str = "arp-table.json") -> dict[str, str]:
        table = load_arp_table(path=path)
        self._arp_table = table
        return table

    async def open_websocket(
        self,
        on_message: Callable[[dict[str, Any]], Awaitable[None] | None],
    ) -> Any:
        try:
            import websockets
        except ImportError as exc:
            raise ConfigurationError(
                "websocket support requires the 'websockets' package"
            ) from exc

        await self.get_credentials()
        websocket_url = f"wss://{self.region}-pconnect3.coolkit.cc:8080/api/ws"
        socket = await websockets.connect(websocket_url)
        await socket.send(
            json.dumps(
                {
                    "action": "userOnline",
                    "at": self.at,
                    "apikey": self.api_key,
                    "userAgent": "ewelink-api-python",
                    "sequence": str(int(datetime.now(UTC).timestamp() * 1000)),
                }
            )
        )

        async def _reader() -> None:
            async for raw_message in socket:
                if not isinstance(raw_message, str):
                    continue
                payload = json.loads(raw_message)
                maybe_awaitable = on_message(payload)
                if asyncio.iscoroutine(maybe_awaitable):
                    await maybe_awaitable

        asyncio.create_task(_reader())
        return socket

    async def get_ws_device_power_state(self, device_id: str, *, channel: int = 0) -> str | None:
        device = await self.get_device(device_id)
        return self.get_device_power_state(device, channel=channel)

    async def set_ws_device_power_state(self, device_id: str, state: str, *, channel: int | None = None) -> dict[str, Any]:
        return await self.set_device_power_state(device_id, state, channel=channel)
