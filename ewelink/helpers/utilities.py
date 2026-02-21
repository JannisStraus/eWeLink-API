import time
from urllib.parse import urlencode

nonce = format(int(time.time_ns()), "x")[-8:]
timestamp = int(time.time())


def _get(obj, path, default_value=None):
    if obj is None:
        return default_value

    parts = []
    token = ""
    for ch in path:
        if ch in ".[] ,":
            if token:
                parts.append(token)
                token = ""
        else:
            token += ch
    if token:
        parts.append(token)

    cur = obj
    for part in parts:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
            continue

        if isinstance(cur, list) and part.isdigit():
            idx = int(part)
            if idx < len(cur):
                cur = cur[idx]
                continue

        return default_value

    return cur


def _empty(obj):
    return not bool(obj)


def to_query_string(obj):
    return f"?{urlencode(obj)}"
