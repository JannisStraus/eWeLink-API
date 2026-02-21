"""Typed models for eWeLink responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


class APIResponse(TypedDict, total=False):
    error: int
    msg: str
    data: Any


class Credentials(TypedDict, total=False):
    at: str
    apiKey: str
    region: str
    user: dict[str, Any]


class Device(TypedDict, total=False):
    deviceid: str
    name: str
    online: bool
    apiKey: str
    params: dict[str, Any]
    extra: dict[str, Any]


@dataclass(slots=True)
class ChannelCommand:
    """Simple channel command helper."""

    channel: int
    state: str
