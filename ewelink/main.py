from ewelink.data.constants import APP_ID as DEFAULT_APP_ID, APP_SECRET as DEFAULT_APP_SECRET
from ewelink.data.errors import errors
from ewelink.mixins import apply_mixins
from ewelink.mixins.methods import get_region as _get_region


class EWeLink:
    def __init__(self, parameters=None):
        if parameters is None:
            parameters = {}

        region = parameters.get("region", "us")
        email = parameters.get("email")
        phone_number = parameters.get("phoneNumber")
        password = parameters.get("password")
        at = parameters.get("at")
        api_key = parameters.get("apiKey")
        devices_cache = parameters.get("devicesCache")
        arp_table = parameters.get("arpTable")
        app_id = parameters.get("APP_ID", DEFAULT_APP_ID)
        app_secret = parameters.get("APP_SECRET", DEFAULT_APP_SECRET)

        check = self.check_login_parameters(
            {
                "region": region,
                "email": email,
                "phoneNumber": phone_number,
                "password": password,
                "at": at,
                "apiKey": api_key,
                "devicesCache": devices_cache,
                "arpTable": arp_table,
            }
        )

        if check is False:
            raise ValueError(errors["invalidCredentials"])

        self.region = region
        self.phoneNumber = phone_number
        self.email = email
        self.password = password
        self.at = at
        self.apiKey = api_key
        self.devicesCache = devices_cache
        self.arpTable = arp_table

        self.APP_ID = app_id
        self.APP_SECRET = app_secret

    @staticmethod
    def check_login_parameters(params):
        email = params.get("email")
        phone_number = params.get("phoneNumber")
        password = params.get("password")
        devices_cache = params.get("devicesCache")
        arp_table = params.get("arpTable")
        at = params.get("at")

        if email is not None and phone_number is not None:
            return False

        if (
            (email is not None and password is not None)
            or (phone_number is not None and password is not None)
            or (devices_cache is not None and arp_table is not None)
            or at is not None
        ):
            return True

        return False

    def get_api_url(self):
        return f"https://{self.region}-api.coolkit.cc:8080/api"

    def get_ota_url(self):
        return f"https://{self.region}-ota.coolkit.cc:8080/otaother"

    def get_api_websocket(self):
        return f"wss://{self.region}-pconnect3.coolkit.cc:8080/api/ws"

    def get_zeroconf_url(self, device):
        ip = self.get_device_ip(device)
        return f"http://{ip}:8081/zeroconf"

    def get_region(self):
        return _get_region(self)

    def getRegion(self):
        return self.get_region()


apply_mixins(EWeLink)

# Backward-compatible alias with the JavaScript class name
eWeLink = EWeLink
