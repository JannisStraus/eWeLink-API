import unittest

from ewelink.main import eWeLink
from ewelink.data.errors import errors
from test._setup.python_test_utils import require_credentials, require_dependency


class TestValidCredentials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = require_credentials(
            "email",
            "password",
            "deviceIdWithoutPower",
            "fourChannelsDevice",
        )

    def test_invalid_device_power_state(self):
        conn = eWeLink({"email": self.creds["email"], "password": self.creds["password"]})
        power = conn.getDevicePowerState("invalid deviceid")
        self.assertEqual(power.get("error"), 404)
        self.assertEqual(power.get("msg"), errors[404])

    def test_wrong_device_channel(self):
        conn = eWeLink({"email": self.creds["email"], "password": self.creds["password"]})
        power = conn.getDevicePowerState(self.creds["fourChannelsDevice"], 8)
        self.assertEqual(power.get("error"), 404)
        self.assertEqual(power.get("msg"), errors["ch404"])

    def test_invalid_device_power_usage(self):
        conn = eWeLink({"email": self.creds["email"], "password": self.creds["password"]})
        usage = conn.getDevicePowerUsage("invalid deviceid")
        self.assertEqual(usage.get("error"), errors["noPower"])

    def test_device_without_monitor_power_usage(self):
        conn = eWeLink({"email": self.creds["email"], "password": self.creds["password"]})
        usage = conn.getDevicePowerUsageRaw(self.creds["deviceIdWithoutPower"])
        self.assertEqual(usage.get("error"), errors["noPower"])


if __name__ == "__main__":
    unittest.main()
