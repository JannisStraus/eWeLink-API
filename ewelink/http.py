"""Low-level HTTP transport for eWeLink."""

from __future__ import annotations

from typing import Any

import aiohttp

from .exceptions import APIError

DEFAULT_REGION = "us"


class HttpTransport:
    """Thin async transport with eWeLink specific defaults."""

    def __init__(
        self,
        *,
        region: str = DEFAULT_REGION,
        app_id: str,
        timeout: float = 10.0,
    ) -> None:
        self.region = region
        self.app_id = app_id
        self.at: str | None = None
        self.api_key: str | None = None
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._client = aiohttp.ClientSession(timeout=self._timeout)

    def update_auth(self, *, at: str | None, api_key: str | None, region: str | None = None) -> None:
        self.at = at
        self.api_key = api_key
        if region:
            self.region = region

    async def close(self) -> None:
        await self._client.close()

    def _base_url(self) -> str:
        return f"https://{self.region}-api.coolkit.cc:8080/api"

    def _headers(self, auth: bool) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CK-Appid": self.app_id,
        }
        if auth and self.at:
            headers["Authorization"] = f"Bearer {self.at}"
        return headers

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        auth: bool = True,
        absolute_url: str | None = None,
    ) -> dict[str, Any]:
        url = absolute_url or f"{self._base_url()}{path}"
        async with self._client.request(
            method,
            url,
            json=json_body,
            headers=self._headers(auth),
            params=params,
        ) as response:
            response.raise_for_status()
            payload = await response.json()
        if isinstance(payload, dict) and payload.get("error", 0) not in (0, None):
            raise APIError(
                payload.get("msg") or "eWeLink API returned an error",
                error=payload.get("error"),
                payload=payload,
            )
        if not isinstance(payload, dict):
            raise APIError("Unexpected eWeLink API response payload", payload=payload)
        return payload
