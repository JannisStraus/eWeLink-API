import unittest

from ewelink.main import eWeLink
from ewelink.data.errors import errors
from test._setup.expectations import assert_firmware_shape
from test._setup.python_test_utils import require_credentials, require_dependency


class TestFirmware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = require_credentials(
            "email",
            "password",
            "singleChannelDeviceId",
            "outdatedFirmwareDevice",
            "updatedFirmwareDevice",
        )
        cls.connection = eWeLink({"email": cls.creds["email"], "password": cls.creds["password"]})

    def test_get_firmware_version(self):
        device_id = self.creds["singleChannelDeviceId"]
        device = self.connection.getDevice(device_id)
        firmware = self.connection.getFirmwareVersion(device_id)
        self.assertEqual(firmware.get("status"), "ok")
        self.assertEqual(firmware.get("fwVersion"), device.get("params", {}).get("fwVersion"))

    def test_invalid_device(self):
        firmware = self.connection.getFirmwareVersion("invalid deviceid")
        self.assertEqual(firmware.get("error"), 404)
        self.assertEqual(firmware.get("msg"), errors[404])

    def test_check_device_update(self):
        status = self.connection.checkDeviceUpdate(self.creds["outdatedFirmwareDevice"])
        self.assertEqual(status.get("status"), "ok")
        self.assertIn(status.get("msg"), ("Update available", "No update available"))

    def test_check_devices_updates_shape(self):
        status = self.connection.checkDevicesUpdates()
        self.assertIsInstance(status, list)
        assert_firmware_shape(self, status[0])


if __name__ == "__main__":
    unittest.main()
