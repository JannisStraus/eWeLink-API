import unittest

from ewelink.main import eWeLink
from ewelink.data.errors import errors
from test._setup.python_test_utils import require_credentials, require_dependency


class TestTemperatureHumidity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = require_credentials(
            "email",
            "password",
            "deviceIdWithTempAndHum",
            "deviceIdWithoutTempAndHum",
        )
        cls.conn = eWeLink({"email": cls.creds["email"], "password": cls.creds["password"]})
        cls.conn.getCredentials()

    def test_get_temperature_humidity(self):
        device_id = self.creds["deviceIdWithTempAndHum"]
        device = self.conn.getDevice(device_id)
        result = self.conn.getDeviceCurrentTH(device_id)
        self.assertEqual(result.get("status"), "ok")
        self.assertEqual(result.get("temperature"), device.get("params", {}).get("currentTemperature"))
        self.assertEqual(result.get("humidity"), device.get("params", {}).get("currentHumidity"))

    def test_invalid_device(self):
        result = self.conn.getDeviceCurrentTemperature("invalid")
        self.assertEqual(result.get("error"), 404)
        self.assertEqual(result.get("msg"), errors[404])

    def test_device_without_sensor(self):
        result = self.conn.getDeviceCurrentHumidity(self.creds["deviceIdWithoutTempAndHum"])
        self.assertEqual(result.get("error"), 404)
        self.assertEqual(result.get("msg"), errors["noSensor"])


if __name__ == "__main__":
    unittest.main()
