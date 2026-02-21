import os
import unittest

import ewelink
from ewelink import Client
from ewelink.models.enumerations import Region


class TestUser(unittest.IsolatedAsyncioTestCase):
    email = os.environ["EWELINK_EMAIL"]
    phone = os.environ["EWELINK_PHONE"]
    password = os.environ["EWELINK_PASSWORD"]
    region = os.environ["EWELINK_REGION"]
    region_enum = Region[region.upper()]

    @ewelink.login(password, email=email)
    async def test_login_with_email_without_region(self, client: Client) -> None:
        self.assertEqual(client.region, self.region_enum)

    @ewelink.login(password, email=email, region=region)
    async def test_login_with_email_with_region(self, client: Client) -> None:
        self.assertEqual(client.region, self.region_enum)

    # @ewelink.login(password, phone=phone)
    # async def test_login_with_phone_without_region(self, client: Client) -> None:
    #     self.assertEqual(client.region, self.region_enum)

    # @ewelink.login(password, phone=phone, region=region)
    # async def test_login_with_phone_with_region(self, client: Client) -> None:
    #     self.assertEqual(client.region, self.region_enum)


if __name__ == "__main__":
    unittest.main()
