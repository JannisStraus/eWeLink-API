"""Helpers for local cache and LAN metadata."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def load_json_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {}
    return json.loads(file_path.read_text(encoding="utf-8"))


def save_json_file(path: str | Path, payload: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_devices_cache(path: str | Path = "devices-cache.json") -> list[dict[str, Any]]:
    payload = load_json_file(path)
    devices = payload.get("devices")
    if isinstance(devices, list):
        return [device for device in devices if isinstance(device, dict)]
    return []


def save_devices_cache(devices: list[dict[str, Any]], path: str | Path = "devices-cache.json") -> None:
    save_json_file(path, {"devices": devices})


def save_arp_table(path: str | Path = "arp-table.json") -> dict[str, str]:
    result = subprocess.run(["arp", "-a"], check=False, capture_output=True, text=True)
    table: dict[str, str] = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[1].startswith("(") and parts[1].endswith(")"):
            ip = parts[1].strip("()")
            mac = parts[3]
            table[mac.lower()] = ip
    save_json_file(path, {"arp": table})
    return table


def load_arp_table(path: str | Path = "arp-table.json") -> dict[str, str]:
    payload = load_json_file(path)
    arp = payload.get("arp")
    if isinstance(arp, dict):
        return {str(key).lower(): str(value) for key, value in arp.items()}
    return {}
