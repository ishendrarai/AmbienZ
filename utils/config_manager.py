"""
config_manager.py — Load/save config.json with defaults.
"""

import json
import os

DEFAULTS = {
    "device_ip":        "192.168.0.100",
    "port":             38899,
    "send_fps":         40,
    "min_brightness":   10,
    "max_brightness":   255,
    "dark_threshold":   20,
    "saturation_boost": 1.4,
    "base_smooth":      0.8,
    "fast_smooth":      0.3,
    "num_clusters":     3,
    "slow_threshold":   0.03,
    "fallback_scale":   0.5,
    "color_temp":       6500,
    "algorithm_mode":   "dominant",   # dominant | average | edge_weighted
    "capture_scale":    1.0,          # 1.0 | 0.5 | 0.25
    "temporal_smooth":  False,
    "capture_region":   "full",       # full | top | bottom | custom
    "custom_region":    None,         # [x, y, w, h] or None
    "scene_mode":       "ambient",    # movie | gaming | music | ambient
}

_CFG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


def load() -> dict:
    cfg = dict(DEFAULTS)
    try:
        with open(_CFG_FILE, "r") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def save(cfg: dict) -> None:
    try:
        with open(_CFG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"[Config] Save failed: {e}")
