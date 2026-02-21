import unittest

from ewelink.main import eWeLink
from ewelink.data.errors import errors
from ewelink.helpers.device_control import get_all_channels_state
from test._setup.python_test_utils import require_credentials, require_dependency


class TestDeviceControlWebSocket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        require_dependency("websocket")
        cls.creds = require_credentials(
            "email",
            "password",
            "singleChannelDeviceId",
            "fourChannelsDevice",
        )
        cls.conn = eWeLink({"email": cls.creds["email"], "password": cls.creds["password"]})
        cls.shared = bool(cls.creds.get("sharedAccount", False))

    def test_get_single_channel_power_state(self):
        device = self.conn.getDevice(self.creds["singleChannelDeviceId"])
        original = device.get("params", {}).get("switch")
        power = self.conn.getWSDevicePowerState(
            self.creds["singleChannelDeviceId"], {"shared": self.shared}
        )
        self.assertEqual(power.get("status"), "ok")
        self.assertEqual(power.get("state"), original)
        self.assertEqual(power.get("channel"), 1)

    def test_get_all_channels_power_state(self):
        device = self.conn.getDevice(self.creds["fourChannelsDevice"])
        original = get_all_channels_state(device.get("params", {}))
        power = self.conn.getWSDevicePowerState(
            self.creds["fourChannelsDevice"], {"allChannels": True, "shared": self.shared}
        )
        self.assertEqual(power.get("status"), "ok")
        self.assertEqual(power.get("state"), original)

    def test_invalid_power_state_error(self):
        with self.assertRaisesRegex(ValueError, errors["invalidPowerState"]):
            self.conn.setWSDevicePowerState(self.creds["singleChannelDeviceId"], "INVALID STATE")


if __name__ == "__main__":
    unittest.main()
