import unittest

from ewelink.main import eWeLink
from ewelink.classes.zeroconf import Zeroconf
from ewelink.data.errors import errors
from test._setup.python_test_utils import require_credentials, require_dependency


class TestZeroconf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = require_credentials("email", "password", "region", "localIp", "localIpInvalid")

    def test_save_devices_cache(self):
        file_path = "./test/_setup/cache/devices-cache.json"
        conn = eWeLink(
            {
                "region": self.creds["region"],
                "email": self.creds["email"],
                "password": self.creds["password"],
            }
        )
        result = conn.saveDevicesCache(file_path)
        self.assertEqual(result.get("status"), "ok")
        self.assertEqual(result.get("file"), file_path)

    def test_save_devices_cache_invalid_credentials(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        result = conn.saveDevicesCache("/tmp/non-existent-folder/devices-cache.json")
        self.assertEqual(result.get("error"), 406)
        self.assertEqual(result.get("msg"), errors[406])

    def test_load_cached_devices_missing(self):
        devices = Zeroconf.load_cached_devices("file-not-found")
        self.assertIsInstance(devices, dict)
        self.assertIn("No such file", devices.get("error", "").title())

    def test_load_arp_table_missing(self):
        arp_table = Zeroconf.load_arp_table("/tmp/non-existent-folder/arp-table.json")
        self.assertIsInstance(arp_table, dict)
        self.assertIn("No such file", arp_table.get("error", "").title())


if __name__ == "__main__":
    unittest.main()
