"""
smoothing.py — Adaptive exponential smoothing + optional Kalman filter.
"""

import numpy as np
from typing import Tuple

RGB = Tuple[int, int, int]


class AdaptiveSmoother:
    """Smooth color transitions with adaptive blending speed."""

    def __init__(self, base_smooth: float = 0.8, fast_smooth: float = 0.3):
        self.base_smooth = base_smooth
        self.fast_smooth = fast_smooth
        self.prev_rgb = (0, 0, 0)
        self.prev_brightness = 0

    def update(self, r: int, g: int, b: int, brightness: int) -> Tuple[RGB, int]:
        diff = (abs(r - self.prev_rgb[0]) +
                abs(g - self.prev_rgb[1]) +
                abs(b - self.prev_rgb[2]) +
                abs(brightness - self.prev_brightness))

        if diff > 150:
            smooth = self.fast_smooth
        elif diff < 40:
            smooth = self.base_smooth
        else:
            t = (diff - 40) / 110.0
            smooth = self.base_smooth - t * (self.base_smooth - self.fast_smooth)

        blend = 1.0 - smooth
        nr = int(self.prev_rgb[0] + (r - self.prev_rgb[0]) * blend)
        ng = int(self.prev_rgb[1] + (g - self.prev_rgb[1]) * blend)
        nb = int(self.prev_rgb[2] + (b - self.prev_rgb[2]) * blend)
        nb_ = int(self.prev_brightness + (brightness - self.prev_brightness) * blend)

        self.prev_rgb = (nr, ng, nb)
        self.prev_brightness = nb_
        return (nr, ng, nb), nb_

    def reset(self):
        self.prev_rgb = (0, 0, 0)
        self.prev_brightness = 0


class KalmanSmoother:
    """1D Kalman filter per channel for temporal color stabilization."""

    def __init__(self, process_noise: float = 1e-3, measure_noise: float = 0.1):
        n = 4  # r, g, b, brightness
        self._x = np.zeros(n, dtype=np.float64)
        self._P = np.ones(n, dtype=np.float64)
        self._Q = np.full(n, process_noise)
        self._R = np.full(n, measure_noise)

    def update(self, r: int, g: int, b: int, brightness: int) -> Tuple[RGB, int]:
        z = np.array([r, g, b, brightness], dtype=np.float64)
        # Predict
        self._P += self._Q
        # Update
        K = self._P / (self._P + self._R)
        self._x = self._x + K * (z - self._x)
        self._P = (1 - K) * self._P
        out = np.clip(self._x, 0, 255).astype(int)
        return (int(out[0]), int(out[1]), int(out[2])), int(out[3])

    def reset(self):
        self._x[:] = 0
        self._P[:] = 1
