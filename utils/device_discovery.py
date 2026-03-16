"""
device_discovery.py — Discover WiZ bulbs on the local network via UDP broadcast.
"""

import json
import socket
import threading
import time
from typing import Callable, List


BROADCAST_ADDR = "255.255.255.255"
PORT = 38899
TIMEOUT = 2.0
REGISTRATION_MSG = json.dumps({"method": "registration", "params": {"phoneMac": "aabbccddeeff", "register": True}})


def discover(timeout: float = TIMEOUT) -> List[dict]:
    """
    Broadcast a WiZ registration packet and collect responses.
    Returns a list of dicts: [{"ip": "...", "mac": "...", "name": "WiZ Bulb"}]
    """
    found = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    sock.bind(("", 0))

    try:
        sock.sendto(REGISTRATION_MSG.encode(), (BROADCAST_ADDR, PORT))
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                data, addr = sock.recvfrom(1024)
                ip = addr[0]
                if ip not in found:
                    try:
                        payload = json.loads(data)
                        mac = payload.get("result", {}).get("mac", "unknown")
                        name = payload.get("result", {}).get("moduleName", "WiZ Bulb")
                    except Exception:
                        mac, name = "unknown", "WiZ Bulb"
                    found[ip] = {"ip": ip, "mac": mac, "name": name}
            except socket.timeout:
                break
    finally:
        sock.close()

    return list(found.values())


def discover_async(callback: Callable[[List[dict]], None], timeout: float = TIMEOUT) -> threading.Thread:
    """Run discovery in a background thread and call callback with results."""
    def _run():
        results = discover(timeout)
        callback(results)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t
