"""
wiz_protocol.py — Send color commands to a WiZ bulb via UDP.
"""

import json
import socket
import numpy as np


class WizSender:
    def __init__(self, ip: str, port: int = 38899):
        self.ip = ip
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def update_target(self, ip: str, port: int = 38899):
        self.ip = ip
        self.port = port

    def send_color(self, r: int, g: int, b: int, brightness: int,
                   min_brightness: int = 10, max_brightness: int = 255) -> bool:
        payload = {
            "method": "setPilot",
            "params": {
                "r": int(np.clip(r, 0, 255)),
                "g": int(np.clip(g, 0, 255)),
                "b": int(np.clip(b, 0, 255)),
                "dimming": int(np.clip(brightness, min_brightness, max_brightness)),
                "cct": 0,
            },
        }
        try:
            self._sock.sendto(json.dumps(payload).encode(), (self.ip, self.port))
            return True
        except OSError:
            return False

    def send_off(self):
        payload = {"method": "setPilot", "params": {"state": False}}
        try:
            self._sock.sendto(json.dumps(payload).encode(), (self.ip, self.port))
        except OSError:
            pass

    def send_on(self):
        payload = {"method": "setPilot", "params": {"state": True}}
        try:
            self._sock.sendto(json.dumps(payload).encode(), (self.ip, self.port))
        except OSError:
            pass

    def close(self):
        self._sock.close()
