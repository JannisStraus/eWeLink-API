"""Custom exceptions for ewelink-api."""

from __future__ import annotations

from typing import Any


class EWeLinkError(Exception):
    """Base exception for the package."""


class ConfigurationError(EWeLinkError):
    """Raised when client configuration is invalid."""


class AuthenticationError(EWeLinkError):
    """Raised when authentication fails."""


class APIError(EWeLinkError):
    """Raised when eWeLink API returns a non-success response."""

    def __init__(self, message: str, *, error: int | None = None, payload: Any = None) -> None:
        super().__init__(message)
        self.error = error
        self.payload = payload


class DeviceNotFound(EWeLinkError):
    """Raised when a requested device does not exist."""


class DeviceOffline(EWeLinkError):
    """Raised when trying to control a device that is offline."""
