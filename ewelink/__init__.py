"""Public package API."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from .client import DEFAULT_APP_ID, DEFAULT_APP_SECRET, Client
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    DeviceNotFound,
    DeviceOffline,
    EWeLinkError,
)
from dotenv import load_dotenv

load_dotenv()

__all__ = [
    "APIError",
    "AuthenticationError",
    "Client",
    "ConfigurationError",
    "DeviceNotFound",
    "DeviceOffline",
    "EWeLinkError",
    "login",
]

P = ParamSpec("P")
T = TypeVar("T")


def login(
    password: str,
    username: str,
    *,
    region: str = "us",
    app_id: str | None = None,
    app_secret: str | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator that injects an authenticated client as first arg."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
            email = username if "@" in username else None
            phone_number = username if email is None else None
            client = Client(
                email=email,
                phone_number=phone_number,
                password=password,
                region=region,
                app_id=app_id or DEFAULT_APP_ID,
                app_secret=app_secret or DEFAULT_APP_SECRET,
            )
            async with client:
                await client.get_credentials()
                return await func(client, *args, **kwargs)

        return wrapped

    return decorator
