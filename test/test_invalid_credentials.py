import unittest

from ewelink.main import eWeLink
from ewelink.data.errors import errors
from test._setup.python_test_utils import load_credentials, require_dependency


class TestInvalidCredentials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = load_credentials()

    def test_no_credentials_given(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink({})

    def test_get_error_on_credentials(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        credentials = conn.getCredentials()
        self.assertIsInstance(credentials, dict)
        self.assertEqual(credentials.get("msg"), errors[406])
        self.assertEqual(credentials.get("error"), 406)

    def test_get_error_on_all_devices(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        devices = conn.getDevices()
        self.assertIsInstance(devices, dict)
        self.assertEqual(devices.get("msg"), errors[406])
        self.assertEqual(devices.get("error"), 406)

    def test_get_error_on_specific_device(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        device = conn.getDevice(self.creds.get("singleChannelDeviceId", "invalid"))
        self.assertIsInstance(device, dict)
        self.assertEqual(device.get("msg"), errors[406])
        self.assertEqual(device.get("error"), 406)

    def test_get_device_power_state_should_fail(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        state = conn.getDevicePowerState(self.creds.get("singleChannelDeviceId", "invalid"))
        self.assertIsInstance(state, dict)
        self.assertIn(state.get("error"), (401, 406))

    def test_set_device_power_state_should_fail(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        state = conn.setDevicePowerState(self.creds.get("singleChannelDeviceId", "invalid"), "on")
        self.assertIsInstance(state, dict)
        self.assertEqual(state.get("error"), 406)

    def test_power_usage_should_fail(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        usage = conn.getDevicePowerUsage(self.creds.get("deviceIdWithPower", "invalid"))
        self.assertIsInstance(usage, dict)
        self.assertEqual(usage.get("error"), errors["noPower"])


if __name__ == "__main__":
    unittest.main()
