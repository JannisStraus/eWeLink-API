import unittest

from ewelink.main import eWeLink
from ewelink.data.constants import APP_ID, APP_SECRET
from ewelink.data.errors import errors


class TestClassInstantiationValid(unittest.TestCase):
    def test_email_and_password(self):
        credentials = {"email": "user@email.com", "password": "pass"}
        connection = eWeLink(credentials)
        self.assertEqual(
            connection.__dict__,
            {
                "region": "us",
                "phoneNumber": None,
                "email": credentials["email"],
                "password": credentials["password"],
                "at": None,
                "apiKey": None,
                "devicesCache": None,
                "arpTable": None,
                "APP_ID": APP_ID,
                "APP_SECRET": APP_SECRET,
            },
        )

    def test_email_password_with_region(self):
        credentials = {"region": "cn", "email": "user@email.com", "password": "pass"}
        connection = eWeLink(credentials)
        self.assertEqual(connection.region, "cn")
        self.assertEqual(connection.email, credentials["email"])
        self.assertEqual(connection.password, credentials["password"])

    def test_phone_password(self):
        credentials = {"phoneNumber": "555123789", "password": "pass"}
        connection = eWeLink(credentials)
        self.assertEqual(connection.phoneNumber, credentials["phoneNumber"])
        self.assertEqual(connection.password, credentials["password"])

    def test_access_token(self):
        credentials = {"at": "xxxyyyzzz"}
        connection = eWeLink(credentials)
        self.assertEqual(connection.at, credentials["at"])

    def test_devices_cache_and_arp_table(self):
        credentials = {"devicesCache": "devices", "arpTable": "arptable"}
        connection = eWeLink(credentials)
        self.assertEqual(connection.devicesCache, credentials["devicesCache"])
        self.assertEqual(connection.arpTable, credentials["arpTable"])

    def test_email_and_access_token(self):
        credentials = {"email": "user@email.com", "at": "xxxyyyzzz"}
        connection = eWeLink(credentials)
        self.assertEqual(connection.email, credentials["email"])
        self.assertEqual(connection.at, credentials["at"])

    def test_custom_app_credentials(self):
        credentials = {
            "email": "user@email.com",
            "at": "xxxyyyzzz",
            "APP_ID": "CUSTOM_APP_ID",
            "APP_SECRET": "CUSTOM_APP_SECRET",
        }
        connection = eWeLink(credentials)
        self.assertEqual(connection.APP_ID, "CUSTOM_APP_ID")
        self.assertEqual(connection.APP_SECRET, "CUSTOM_APP_SECRET")


class TestClassInstantiationInvalid(unittest.TestCase):
    def test_user_without_password(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink({"email": "user@email.com"})

    def test_only_password(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink({"password": "pass"})

    def test_phone_without_password(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink({"phoneNumber": "555123789"})

    def test_email_and_phone(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink({"email": "user@email.com", "phoneNumber": "555123789"})

    def test_email_phone_password(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink(
                {
                    "email": "user@email.com",
                    "phoneNumber": "555123789",
                    "password": "pass",
                }
            )

    def test_devices_cache_without_arp(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink({"devicesCache": "devices"})

    def test_arp_without_devices_cache(self):
        with self.assertRaisesRegex(ValueError, errors["invalidCredentials"]):
            eWeLink({"arpTable": "arptable"})


if __name__ == "__main__":
    unittest.main()
