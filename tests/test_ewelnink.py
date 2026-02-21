import unittest
import ewelink
from ewelink import Client
import os

class TesteWeLink(unittest.IsolatedAsyncioTestCase):
    async def test_device(self) -> None:
        password = os.environ["EWELINK_PASSWORD"]
        email = os.environ["EWELINK_EMAIL"]
        region = os.environ["EWELINK_REGION"]

        @ewelink.login(password, email, region=region)
        async def get_client(client: Client) -> Client:
            return client

        client = await get_client()

        # Basic sanity
        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, "devices"))

        print("Region:", client.region)
        print("User:", client.user.info)
        print("Devices:", client.devices)

        device = client.get_device("10008ecfd9")  # single channel device
        device2 = client.get_device("10007fgah9")  # four channel device (optional)

        # Depending on implementation, these may be properties that trigger network calls.
        print("Device 1 params:", device.params)
        print("Device 1 state:", device.state)
        print("Device 1 created_at:", device.created_at)
        print(
            "Brand Name:", device.brand.name,
            "Logo URL:", device.brand.logo.url,
        )
        print("Device 1 online?", device.online)

        # Optional: at least assert the objects exist
        self.assertIsNotNone(device)
        self.assertIsNotNone(device2)


if __name__ == "__main__":
    unittest.main()
