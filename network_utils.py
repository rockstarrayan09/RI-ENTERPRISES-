import socket
import subprocess
import sys


def _ip_from_udp_probe():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return None


def _ip_from_hostname():
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip and not ip.startswith("127."):
                return ip
    except OSError:
        pass
    return None


def _ip_from_mac_interfaces():
    if sys.platform != "darwin":
        return None
    for iface in ("en0", "en1", "en2"):
        try:
            result = subprocess.run(
                ["ipconfig", "getifaddr", iface],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            ip = result.stdout.strip()
            if ip and not ip.startswith("127."):
                return ip
        except (OSError, subprocess.SubprocessError):
            continue
    return None


def get_local_ip():
    """Return this PC's LAN IP so phones on the same Wi-Fi can open the site."""
    for candidate in (_ip_from_udp_probe, _ip_from_mac_interfaces, _ip_from_hostname):
        ip = candidate()
        if ip and not ip.startswith("127.") and ip != "0.0.0.0":
            return ip
    return "127.0.0.1"
