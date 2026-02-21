import unittest

from ewelink.main import eWeLink
from ewelink.data.errors import errors
from test._setup.python_test_utils import require_credentials, require_dependency


class TestUserInformation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require_dependency("requests")
        cls.creds = require_credentials("email", "password", "region")

    def test_region_should_be_returned(self):
        conn = eWeLink({"email": self.creds["email"], "password": self.creds["password"]})
        response = conn.getRegion()
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get("email"), self.creds["email"])
        self.assertEqual(response.get("region"), self.creds["region"])

    def test_invalid_credentials_should_fail(self):
        conn = eWeLink({"email": "invalid", "password": "credentials"})
        response = conn.getRegion()
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get("msg"), errors[406])
        self.assertEqual(response.get("error"), 406)

    def test_invalid_initialization_should_warn(self):
        conn = eWeLink({"at": "access token"})
        response = conn.getRegion()
        self.assertIsInstance(response, dict)
        self.assertEqual(response.get("msg"), errors["invalidAuth"])
        self.assertEqual(response.get("error"), 406)


if __name__ == "__main__":
    unittest.main()
