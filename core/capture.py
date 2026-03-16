"""
capture.py — Screen capture with resolution scaling and region selection.
"""

import numpy as np
import cv2
import mss
from typing import Optional, Tuple


class ScreenCapture:
    def __init__(self):
        self._sct = mss.mss()
        self._monitor_idx = 1

    def _get_monitor(self, region: str, custom: Optional[list]) -> dict:
        base = self._sct.monitors[self._monitor_idx]
        if region == "full" or not region:
            return base
        w, h = base["width"], base["height"]
        band = max(h // 6, 100)
        if region == "top":
            return {"top": base["top"], "left": base["left"], "width": w, "height": band}
        if region == "bottom":
            return {"top": base["top"] + h - band, "left": base["left"], "width": w, "height": band}
        if region == "custom" and custom and len(custom) == 4:
            x, y, cw, ch = custom
            return {"top": base["top"] + y, "left": base["left"] + x, "width": cw, "height": ch}
        return base

    def grab(self, scale: float = 1.0, region: str = "full",
             custom_region: Optional[list] = None) -> np.ndarray:
        """
        Grab a frame from the screen.
        Returns an RGB numpy array.
        """
        monitor = self._get_monitor(region, custom_region)
        raw = np.array(self._sct.grab(monitor))
        frame = cv2.cvtColor(raw, cv2.COLOR_BGRA2RGB)
        if scale < 1.0:
            frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return frame

    def close(self):
        self._sct.close()
