import unittest

from ewelink.main import eWeLink
from test._setup.expectations import (
    assert_all_device_shape,
    assert_credentials,
    assert_specific_device_shape,
)
from test._setup.python_test_utils import require_credentials, require_dependency


class TestEnvNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = require_credentials(
            "email",
            "password",
            "singleChannelDeviceId",
            "fourChannelsDevice",
        )
        cls.conn = eWeLink({"email": cls.creds["email"], "password": cls.creds["password"]})

    def test_get_credentials(self):
        credentials = self.conn.getCredentials()
        assert_credentials(self, credentials)

    def test_get_all_devices(self):
        devices = self.conn.getDevices()
        self.assertIsInstance(devices, list)
        assert_all_device_shape(self, devices[0])

    def test_get_specific_device(self):
        device_id = self.creds["singleChannelDeviceId"]
        device = self.conn.getDevice(device_id)
        self.assertIsInstance(device, dict)
        self.assertEqual(device.get("deviceid"), device_id)
        assert_specific_device_shape(self, device)

    def test_get_single_channel_power_state(self):
        device_id = self.creds["singleChannelDeviceId"]
        device = self.conn.getDevice(device_id)
        state = self.conn.getDevicePowerState(device_id)
        self.assertEqual(state.get("status"), "ok")
        self.assertEqual(state.get("state"), device.get("params", {}).get("switch"))

    def test_get_multi_channel_power_state(self):
        device_id = self.creds["fourChannelsDevice"]
        channel = 3
        device = self.conn.getDevice(device_id)
        current = device.get("params", {}).get("switches", [])[channel - 1]["switch"]
        state = self.conn.getDevicePowerState(device_id, channel)
        self.assertEqual(state.get("status"), "ok")
        self.assertEqual(state.get("state"), current)

    def test_get_channel_count_1(self):
        result = self.conn.getDeviceChannelCount(self.creds["singleChannelDeviceId"])
        self.assertEqual(result.get("status"), "ok")
        self.assertEqual(result.get("switchesAmount"), 1)

    def test_get_channel_count_4(self):
        result = self.conn.getDeviceChannelCount(self.creds["fourChannelsDevice"])
        self.assertEqual(result.get("status"), "ok")
        self.assertEqual(result.get("switchesAmount"), 4)


if __name__ == "__main__":
    unittest.main()
