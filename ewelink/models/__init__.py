from typing import Iterable

from .device import Device
from .enumerations import DeviceChannelLengh, DeviceType, Power, Region
from .object import Object
from .user import ClientUser

PowerState = Power


class Devices(list[Device]):
    def __init__(self, devices: Iterable[Device]):
        super().__init__(devices)

    def get(self, id: str) -> Device | None:
        for device in self:
            if device.id == id:
                return device
        return None


__all__ = (
    "ClientUser",
    "Device",
    "DeviceChannelLengh",
    "DeviceType",
    "Devices",
    "Object",
    "Power",
    "PowerState",
    "Region",
)

del Iterable
