"""
sync_engine.py — Orchestrates capture → color → smooth → send loop.
Runs in a background thread; exposes cfg dict for live parameter updates.
"""

import threading
import time
import numpy as np
from typing import Callable, Optional

from core.capture import ScreenCapture
from core.color_engine import extract_color, process_color
from core.smoothing import AdaptiveSmoother, KalmanSmoother
from core.wiz_protocol import WizSender


class SyncEngine:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._capture = ScreenCapture()
        self._sender  = WizSender(cfg["device_ip"], cfg["port"])
        self._adaptive = AdaptiveSmoother(cfg["base_smooth"], cfg["fast_smooth"])
        self._kalman   = KalmanSmoother()

        # Callbacks for UI updates
        self.on_color_update: Optional[Callable] = None  # (r, g, b, brightness, clusters, fps, frame_ms)
        self.on_status_change: Optional[Callable] = None  # (status_str)

        self._use_fallback = False
        self._last_fps = 0.0
        self._last_frame_ms = 0.0

    def start(self):
        if self._running:
            return
        self._running = True
        self._adaptive.reset()
        self._kalman.reset()
        self._sender.update_target(self.cfg["device_ip"], self.cfg["port"])
        self._sender.send_on()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="SyncEngine")
        self._thread.start()
        if self.on_status_change:
            self.on_status_change("Running")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self._sender.send_off()
        if self.on_status_change:
            self.on_status_change("Stopped")

    def is_running(self) -> bool:
        return self._running

    def update_device(self, ip: str, port: int = 38899):
        self.cfg["device_ip"] = ip
        self.cfg["port"] = port
        self._sender.update_target(ip, port)

    def _loop(self):
        cfg = self.cfg
        while self._running:
            t0 = time.perf_counter()

            scale = cfg.get("capture_scale", 1.0)
            if self._use_fallback:
                scale = min(scale, cfg.get("fallback_scale", 0.5))

            try:
                frame = self._capture.grab(
                    scale=scale,
                    region=cfg.get("capture_region", "full"),
                    custom_region=cfg.get("custom_region", None),
                )
            except Exception as e:
                time.sleep(0.1)
                continue

            try:
                (r, g, b), clusters = extract_color(
                    frame,
                    mode=cfg.get("algorithm_mode", "dominant"),
                    num_clusters=cfg.get("num_clusters", 3),
                    brightness_cutoff=cfg.get("dark_threshold", 20),
                )
            except Exception:
                r, g, b = (int(x) for x in frame.mean(axis=(0, 1)))
                clusters = [(r, g, b)]
                self._use_fallback = True

            (r, g, b), brightness = process_color(
                r, g, b,
                dark_threshold=cfg.get("dark_threshold", 20),
                saturation_boost=cfg.get("saturation_boost", 1.4),
                color_temp=cfg.get("color_temp", 6500),
                min_brightness=cfg.get("min_brightness", 10),
                max_brightness=cfg.get("max_brightness", 255),
            )

            # Smoothing
            if cfg.get("temporal_smooth", False):
                (r, g, b), brightness = self._kalman.update(r, g, b, brightness)
            else:
                self._adaptive.base_smooth = cfg.get("base_smooth", 0.8)
                self._adaptive.fast_smooth = cfg.get("fast_smooth", 0.3)
                (r, g, b), brightness = self._adaptive.update(r, g, b, brightness)

            self._sender.send_color(r, g, b, brightness,
                                    min_brightness=cfg.get("min_brightness", 10),
                                    max_brightness=cfg.get("max_brightness", 255))

            elapsed = time.perf_counter() - t0
            self._last_frame_ms = elapsed * 1000
            self._use_fallback = elapsed > cfg.get("slow_threshold", 0.03)

            fps = cfg.get("send_fps", 40)
            self._last_fps = 1.0 / max(elapsed, 1e-6)

            if self.on_color_update:
                self.on_color_update(r, g, b, brightness, clusters,
                                     self._last_fps, self._last_frame_ms)

            sleep_time = max(0, 1.0 / fps - (time.perf_counter() - t0))
            time.sleep(sleep_time)

    def close(self):
        self.stop()
        self._capture.close()
        self._sender.close()
