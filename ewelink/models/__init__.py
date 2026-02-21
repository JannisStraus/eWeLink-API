from typing import Iterable

from .device import Device
from .enumerations import Power

PowerState = Power


class Devices(list[Device]):
    def __init__(self, devices: Iterable[Device]):
        super().__init__(devices)

    def get(self, id: str) -> Device | None:
        for device in self:
            if device.id == id:
                return device


del Iterable
