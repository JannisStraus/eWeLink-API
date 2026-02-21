import base64
import hashlib
import hmac
import json
import random
from pathlib import Path

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except Exception:  # pragma: no cover
    AES = None
    pad = None
    unpad = None

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEVICE_TYPE_UUID = json.loads((_DATA_DIR / "devices-type-uuid.json").read_text())
DEVICE_CHANNEL_LENGTH = json.loads((_DATA_DIR / "devices-channel-length.json").read_text())


def make_authorization_sign(app_secret, body):
    body_json = json.dumps(body, separators=(",", ":"))
    digest = hmac.new(app_secret.encode(), body_json.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def get_device_type_by_uiid(uiid):
    return DEVICE_TYPE_UUID.get(str(uiid), "")


def get_device_channel_count_by_type(device_type):
    return DEVICE_CHANNEL_LENGTH.get(device_type, 0)


def get_device_channel_count(device_uuid):
    device_type = get_device_type_by_uiid(device_uuid)
    return get_device_channel_count_by_type(device_type)


def create_16_uiid():
    return "".join(str(random.randint(0, 9)) for _ in range(16))


def encryption_base64(text):
    return base64.b64encode(text.encode()).decode()


def decryption_base64(text):
    return base64.b64decode(text.encode()).decode()


def encryptation_data(data, key):
    if AES is None:
        raise RuntimeError("pycryptodome is required for zeroconf encryption")

    uid = create_16_uiid()
    iv_b64 = encryption_base64(uid)
    aes_key = hashlib.md5(key.encode()).digest()
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=uid.encode())
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))

    return {
        "uid": uid,
        "iv": iv_b64,
        "data": base64.b64encode(encrypted).decode(),
    }


def decryption_data(data, key, iv):
    if AES is None:
        raise RuntimeError("pycryptodome is required for zeroconf decryption")

    iv_raw = decryption_base64(iv)
    aes_key = hashlib.md5(key.encode()).digest()
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv_raw.encode())
    raw = cipher.decrypt(base64.b64decode(data))
    return unpad(raw, AES.block_size).decode()
