import unittest

from ewelink.main import eWeLink
from test._setup.expectations import (
    assert_all_device_shape,
    assert_credentials,
    assert_specific_device_shape,
)
from test._setup.python_test_utils import require_credentials, require_dependency


class TestEnvServerless(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = require_credentials(
            "email",
            "password",
            "singleChannelDeviceId",
            "fourChannelsDevice",
        )
        conn = eWeLink({"email": cls.creds["email"], "password": cls.creds["password"]})
        credentials = conn.getCredentials()
        cls.access_token = credentials.get("at")
        cls.api_key = credentials.get("user", {}).get("apikey")

    def test_get_credentials(self):
        conn = eWeLink({"email": self.creds["email"], "password": self.creds["password"]})
        credentials = conn.getCredentials()
        assert_credentials(self, credentials)

    def test_get_all_devices(self):
        conn = eWeLink({"at": self.access_token})
        devices = conn.getDevices()
        self.assertIsInstance(devices, list)
        assert_all_device_shape(self, devices[0])

    def test_get_specific_device(self):
        conn = eWeLink({"at": self.access_token})
        device = conn.getDevice(self.creds["singleChannelDeviceId"])
        self.assertEqual(device.get("deviceid"), self.creds["singleChannelDeviceId"])
        assert_specific_device_shape(self, device)


if __name__ == "__main__":
    unittest.main()
