import asyncio
import time
from typing import Any, AnyStr, TypedDict

import aiohttp

from .constants import Constants as constants
from .exceptions import DeviceOffline
from .http import HttpClient
from .models import ClientUser
from .utils import nonce


class DeviceInterface:
    id: str
    online: bool


Response = TypedDict(
    "Response",
    {
        "error": int,
        "deviceid": str,
        "apikey": str,
        "sequence": str | None,
        "params": dict[str, list[dict[str, AnyStr]] | AnyStr],
    },
)


class WebSocketClient:
    http: HttpClient
    heartbeat: int
    ws: aiohttp.ClientWebSocketResponse | None
    session: aiohttp.ClientSession
    user: ClientUser
    devices: dict[str, DeviceInterface]
    _ping_task: asyncio.Task[None] | None = None
    _poll_task: asyncio.Task[None] | None = None

    def __init__(self, http: HttpClient, user: ClientUser) -> None:
        self.http = http
        self.user = user
        self.devices = []
        self.heartbeat = 90
        self.session = http.session
        self.ws = None
        self._futures: dict[str, list[asyncio.Future[Response]]] = {"update": []}

    def set_devices(self, devices: dict[str, DeviceInterface]):
        self.devices = devices

    async def create_websocket(self, domain: str, port: int | str):
        self.ws = await self.session.ws_connect(f"wss://{domain}:{port}/api/ws")
        await self.ws.send_json(
            {
                "action": "userOnline",
                "version": 8,
                "ts": int(time.time()),
                "at": self.http.token,
                "userAgent": "app",
                "apikey": self.user.api_key,
                "appid": constants.APP_ID,
                "nonce": nonce(),
                "sequence": str(time.time() * 1000),
            }
        )
        response: dict[str, str | int | dict[str, int]] = await self.ws.receive_json()
        if not response.get("error"):
            if config := response.get("config", {}):
                if isinstance(config, dict):
                    if hb_interval := response["config"].get("hbInterval", ""):
                        if isinstance(hb_interval, int):
                            self.heartbeat = hb_interval + 7
        self._ping_task = self.http.loop.create_task(self.ping_hb())
        self._poll_task = self.http.loop.create_task(self.poll_event())

    async def update_device_status(
        self, deviceid: str, **kwargs: list[dict[str, AnyStr]] | AnyStr
    ) -> Response:
        fut: asyncio.Future[Response] = self.http.loop.create_future()
        self._futures["update"].append(fut)
        await self.ws.send_json(
            {
                "action": "update",
                "deviceid": deviceid,
                "apikey": self.user.api_key,
                "userAgent": "app",
                "sequence": str(time.time() * 1000),
                "params": kwargs,
            }
        )
        try:
            result = await asyncio.wait_for(fut, timeout=10)
        except asyncio.TimeoutError:
            print("Response timed out")
            result = None
        return result

    async def poll_event(self):
        try:
            while self.ws and not self.ws.closed:
                raw_msg = await self.ws.receive()
                if raw_msg.type is aiohttp.WSMsgType.TEXT:
                    msg: dict[str, Any] = raw_msg.json()
                elif raw_msg.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.CLOSED,
                ):
                    break
                elif raw_msg.type is aiohttp.WSMsgType.ERROR:
                    break
                else:
                    continue
                if action := msg.get("action", None):
                    match action:
                        case "sysmsg":
                            if self.devices:
                                if device := self.devices.get(msg["deviceid"], None):
                                    device.online = msg["params"]["online"]
                if "error" in msg and "params" not in msg:
                    if self._futures["update"]:
                        match msg["error"]:
                            case 0:
                                self._futures["update"][0].set_result(msg)
                            case 503:
                                self._futures["update"][0].set_exception(
                                    DeviceOffline("Device is offline.")
                                )
                        self._futures["update"].pop(0)
                elif "error" in msg and "params" in msg:
                    if (
                        not msg["error"]
                        and "query" in self._futures
                        and self._futures["query"]
                    ):
                        self._futures["query"][0].set_result(msg)
                        self._futures["query"].pop(0)
        except asyncio.CancelledError:
            raise
        finally:
            for fut in self._futures.get("update", []):
                if not fut.done():
                    fut.cancel()
            self._futures["update"].clear()

    async def ping_hb(self):
        try:
            while self.ws and not self.ws.closed:
                await asyncio.sleep(self.heartbeat)
                if self.ws and not self.ws.closed:
                    await self.ws.send_str("ping")
        except asyncio.CancelledError:
            raise

    async def close(self):
        tasks = [task for task in (self._ping_task, self._poll_task) if task]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if self.ws and not self.ws.closed:
            await self.ws.close()

    @property
    def closed(self) -> bool:
        return self.ws.closed
