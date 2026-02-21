from ewelink.helpers.utilities import nonce, timestamp


def credentials_payload(appid, email, phone_number, password):
    return {
        "appid": appid,
        "email": email,
        "phoneNumber": phone_number,
        "password": password,
        "ts": timestamp,
        "version": 8,
        "nonce": nonce,
    }
