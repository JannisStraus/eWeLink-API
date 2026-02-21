import json


class Zeroconf:
    @staticmethod
    def get_arp_table(ip=None):
        try:
            import arpping
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("python arpping dependency is required") from exc

        hosts = arpping.discover(ip)
        return Zeroconf.fix_mac_addresses(hosts)

    @staticmethod
    def fix_mac_addresses(hosts):
        fixed_hosts = []
        for host in hosts:
            octets = host["mac"].split(":")
            fixed_mac = [f"0{o}" if len(o) == 1 else o for o in octets]
            fixed_hosts.append({"ip": host["ip"], "mac": ":".join(fixed_mac)})
        return fixed_hosts

    @staticmethod
    def save_arp_table(config=None):
        if config is None:
            config = {}

        ip = config.get("ip")
        file_name = config.get("file", "./arp-table.json")
        try:
            arp_table = Zeroconf.get_arp_table(ip)
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(arp_table, f, indent=2)
            return {"status": "ok", "file": file_name}
        except Exception as exc:
            return {"error": str(exc)}

    @staticmethod
    def load_arp_table(file_name="./arp-table.json"):
        try:
            with open(file_name, encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            return {"error": str(exc)}

    @staticmethod
    def load_cached_devices(file_name="./devices-cache.json"):
        try:
            with open(file_name, encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            return {"error": str(exc)}
