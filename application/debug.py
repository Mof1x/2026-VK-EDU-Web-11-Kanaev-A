from ipaddress import IPv4Address
from pathlib import Path


def docker_gateway():
    routes = Path('/proc/net/route').read_text(encoding='ascii').splitlines()
    for route in routes[1:]:
        _, destination, gateway, *_ = route.split()
        if destination == '00000000':
            # Linux exposes IPv4 routes as little-endian hexadecimal values.
            return str(IPv4Address(bytes.fromhex(gateway)[::-1]))
    return None
