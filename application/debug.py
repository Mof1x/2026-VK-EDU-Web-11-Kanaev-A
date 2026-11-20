from ipaddress import IPv4Address
from pathlib import Path
from socket import gaierror, gethostbyname

from django.conf import settings


def docker_gateway():
    routes = Path('/proc/net/route').read_text(encoding='ascii').splitlines()
    for route in routes[1:]:
        _, destination, gateway, *_ = route.split()
        if destination == '00000000':
            # Linux exposes IPv4 routes as little-endian hexadecimal values.
            return str(IPv4Address(bytes.fromhex(gateway)[::-1]))
    return None


def show_toolbar_in_docker(request):
    if not settings.DEBUG:
        return False

    peer = request.META.get('REMOTE_ADDR')
    if peer in settings.INTERNAL_IPS:
        return True
    try:
        # Only trust the client address set by our nginx service.
        return (
            peer == gethostbyname('nginx')
            and request.META.get('HTTP_X_FORWARDED_FOR') in settings.INTERNAL_IPS
        )
    except gaierror:
        return False
