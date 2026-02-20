from collections.abc import Iterable

from .asset import Asset
from .device import Device, Network, Pulse
from .enumerations import CountryCodes, DeviceChannelLengh, DeviceType, Power, Region
from .object import Object
from .user import AppInfo, ClientInfo, ClientUser

PowerState = Power


class Devices(list[Device]):
    def __init__(self, devices: Iterable[Device]):
        super().__init__(devices)

    def get(self, id: str) -> Device | None:
        for device in self:
            if device.id == id:
                return device


del Iterable
