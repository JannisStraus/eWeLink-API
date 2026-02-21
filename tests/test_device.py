import unittest
import os
import ewelink
from ewelink import Client
from ewelink.models.enumerations import Region, Power

class TestUser(unittest.IsolatedAsyncioTestCase):
    email = os.environ["EWELINK_EMAIL"]
    phone = os.environ["EWELINK_PHONE"]
    password = os.environ["EWELINK_PASSWORD"]
    region = os.environ["EWELINK_REGION"]
    device_id_on = os.environ["EWELINK_DEVICE_ID_ON"]
    device_id_off = os.environ["EWELINK_DEVICE_ID_OFF"]

    @ewelink.login(password, email=email, region=region)
    async def test_device(self, client: Client) -> None:
        # Test online
        device_on = client.get_device(self.device_id_on)

        self.assertEqual(device_on.id, self.device_id_on)
        self.assertEqual(device_on.online, True)

        device_off = client.get_device(self.device_id_off)

        self.assertEqual(device_off.id, self.device_id_off)
        self.assertEqual(device_off.online, False)

if __name__ == "__main__":
    unittest.main()
