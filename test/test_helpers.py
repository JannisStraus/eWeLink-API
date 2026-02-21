import unittest

from ewelink.data.constants import APP_SECRET
from ewelink.helpers import ewelink as ewelink_helpers


class TestHelpers(unittest.TestCase):
    def test_make_authorization_sign(self):
        auth = ewelink_helpers.make_authorization_sign(APP_SECRET, {"data": "string"})
        self.assertEqual(len(auth), 44)
        self.assertEqual(auth, "7Aaa/8EuRScACNrZTATW2WKIY7lcRnjgWHTiBl8G0TQ=")

    def test_get_device_channel_count(self):
        self.assertEqual(ewelink_helpers.get_device_channel_count(8), 3)
        self.assertEqual(ewelink_helpers.get_device_channel_count(31), 4)
        self.assertEqual(ewelink_helpers.get_device_channel_count(29), 2)
        self.assertEqual(ewelink_helpers.get_device_channel_count(27), 1)
        self.assertEqual(ewelink_helpers.get_device_channel_count(5000), 0)


if __name__ == "__main__":
    unittest.main()
