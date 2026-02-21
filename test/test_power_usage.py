from datetime import datetime
import unittest

from ewelink.main import eWeLink
from test._setup.python_test_utils import require_credentials, require_dependency


class TestPowerUsageNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        require_dependency("websocket")
        cls.creds = require_credentials("email", "password", "deviceIdWithPower")
        cls.conn = eWeLink({"email": cls.creds["email"], "password": cls.creds["password"]})
        cls.conn.getCredentials()

    def test_raw_power_usage(self):
        usage = self.conn.getDevicePowerUsageRaw(self.creds["deviceIdWithPower"])
        self.assertIsInstance(usage, dict)
        self.assertEqual(usage.get("status"), "ok")
        self.assertEqual(len(usage.get("data", {}).get("hundredDaysKwhData", "")), 600)

    def test_current_month_power_usage(self):
        days = datetime.now().day
        usage = self.conn.getDevicePowerUsage(self.creds["deviceIdWithPower"])
        self.assertIsInstance(usage, dict)
        self.assertEqual(usage.get("status"), "ok")
        self.assertEqual(len(usage.get("daily", [])), days)


class TestPowerUsageServerless(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        require_dependency("websocket")
        cls.creds = require_credentials("email", "password", "deviceIdWithPower")
        conn = eWeLink({"email": cls.creds["email"], "password": cls.creds["password"]})
        credentials = conn.getCredentials()
        cls.access_token = credentials.get("at")
        cls.api_key = credentials.get("user", {}).get("apikey")

    def test_raw_power_usage(self):
        conn = eWeLink({"at": self.access_token, "apiKey": self.api_key})
        usage = conn.getDevicePowerUsageRaw(self.creds["deviceIdWithPower"])
        self.assertEqual(usage.get("status"), "ok")
        self.assertEqual(len(usage.get("data", {}).get("hundredDaysKwhData", "")), 600)


if __name__ == "__main__":
    unittest.main()
