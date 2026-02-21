import os
import unittest

import ewelink
from ewelink import Client
from ewelink.models.enumerations import Power


class TestUser(unittest.IsolatedAsyncioTestCase):
    email = os.environ["EWELINK_EMAIL"]
    phone = os.environ["EWELINK_PHONE"]
    password = os.environ["EWELINK_PASSWORD"]
    region = os.environ["EWELINK_REGION"]
    device_id_on = os.environ["EWELINK_DEVICE_ID_ON"]
    device_id_off = os.environ["EWELINK_DEVICE_ID_OFF"]

    @ewelink.login(password, email=email, region=region)
    async def test_device(self, client: Client) -> None:
        device_off = client.get_device(self.device_id_off)
        device_on = client.get_device(self.device_id_on)

        # Test id
        self.assertEqual(device_on.id, self.device_id_on)
        self.assertEqual(device_off.id, self.device_id_off)

        # Test online
        self.assertEqual(device_on.online, True)
        self.assertEqual(device_off.online, False)

        # Test state
        self.assertEqual(device_on.state, Power.off)
        self.assertEqual(device_off.state, Power.off)


if __name__ == "__main__":
    unittest.main()
