import importlib
from unittest import SkipTest


def load_credentials():
    try:
        mod = importlib.import_module("test._setup.config.credentials")
        credentials = getattr(mod, "CREDENTIALS")
        if isinstance(credentials, dict):
            return credentials
    except Exception:
        pass

    from test._setup.config.credentials_example import CREDENTIALS

    return CREDENTIALS


def _is_placeholder(value):
    return not value or (isinstance(value, str) and value.startswith("<") and value.endswith(">"))


def require_credentials(*keys):
    credentials = load_credentials()
    missing = [k for k in keys if _is_placeholder(credentials.get(k))]
    if missing:
        raise SkipTest(
            "Live credentials not configured for keys: " + ", ".join(missing)
        )
    return credentials


def require_dependency(module_name):
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        raise SkipTest(f"Missing dependency: {module_name}") from exc
