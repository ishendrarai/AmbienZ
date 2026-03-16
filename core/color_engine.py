"""
color_engine.py — Color extraction, correction, and processing algorithms.
"""

import numpy as np
import cv2
from sklearn.cluster import KMeans
from typing import Tuple

RGB = Tuple[int, int, int]


# ── Gamma / linear conversion ─────────────────────────────────────────────────

def to_linear(rgb_uint8: np.ndarray) -> np.ndarray:
    """Convert sRGB [0,255] uint8 → linear float [0,1]."""
    return (rgb_uint8.astype(np.float32) / 255.0) ** 2.2


def from_linear(linear: np.ndarray) -> np.ndarray:
    """Convert linear float [0,1] → sRGB [0,255] uint8."""
    return np.clip(linear ** (1.0 / 2.2) * 255.0, 0, 255).astype(np.uint8)


def luminance_linear(r_lin: float, g_lin: float, b_lin: float) -> float:
    """Perceptual luminance from linear-space RGB."""
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


# ── Color temperature white point scaling ─────────────────────────────────────

_CCT_TABLE = {
    # kelvin: (R_scale, G_scale, B_scale)   (all ≤ 1.0 — attenuate channels)
    2700: (1.000, 0.760, 0.430),
    3000: (1.000, 0.800, 0.530),
    4000: (1.000, 0.870, 0.720),
    5000: (1.000, 0.940, 0.870),
    6500: (1.000, 1.000, 1.000),
    9000: (0.860, 0.950, 1.000),
}


def _lerp_cct(k: int) -> Tuple[float, float, float]:
    keys = sorted(_CCT_TABLE.keys())
    if k <= keys[0]:
        return _CCT_TABLE[keys[0]]
    if k >= keys[-1]:
        return _CCT_TABLE[keys[-1]]
    for lo, hi in zip(keys, keys[1:]):
        if lo <= k <= hi:
            t = (k - lo) / (hi - lo)
            r0, g0, b0 = _CCT_TABLE[lo]
            r1, g1, b1 = _CCT_TABLE[hi]
            return (r0 + t * (r1 - r0), g0 + t * (g1 - g0), b0 + t * (b1 - b0))
    return (1.0, 1.0, 1.0)


def apply_color_temp(r: int, g: int, b: int, kelvin: int = 6500) -> RGB:
    rs, gs, bs = _lerp_cct(kelvin)
    return (int(np.clip(r * rs, 0, 255)),
            int(np.clip(g * gs, 0, 255)),
            int(np.clip(b * bs, 0, 255)))


# ── Saturation boost ──────────────────────────────────────────────────────────

def boost_saturation(r: int, g: int, b: int, factor: float) -> RGB:
    arr = np.uint8([[[r, g, b]]])
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[0, 0]
    s = np.clip(s * factor, 0, 255)
    out = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2RGB)[0, 0]
    return int(out[0]), int(out[1]), int(out[2])


# ── Algorithm 1: Dominant KMeans ─────────────────────────────────────────────

def dominant_color(frame: np.ndarray, num_clusters: int = 3,
                   brightness_cutoff: int = 20) -> Tuple[RGB, list]:
    """
    Returns (dominant_rgb, [cluster_rgb, ...]) in sRGB space.
    Processing is done in linear space for perceptual accuracy.
    """
    pixels = frame.reshape(-1, 3).astype(np.float32) / 255.0  # linear approx
    lum = 0.2126 * pixels[:, 0] + 0.7152 * pixels[:, 1] + 0.0722 * pixels[:, 2]
    mask = lum > (brightness_cutoff / 255.0)
    if mask.sum() < 50:
        return (0, 0, 0), []

    salient = pixels[mask]
    weights = lum[mask] / lum[mask].max()
    n = min(num_clusters, len(salient))
    km = KMeans(n_clusters=n, n_init=2, random_state=0)
    km.fit(salient, sample_weight=weights)
    counts = np.bincount(km.labels_)
    centers_srgb = np.clip(km.cluster_centers_ * 255, 0, 255).astype(int)
    dom_idx = np.argmax(counts)
    dom = tuple(int(x) for x in centers_srgb[dom_idx])
    clusters = [tuple(int(x) for x in c) for c in centers_srgb]
    return dom, clusters


# ── Algorithm 2: Average Color ────────────────────────────────────────────────

def average_color(frame: np.ndarray) -> Tuple[RGB, list]:
    avg = frame.mean(axis=(0, 1))
    rgb = tuple(int(x) for x in avg)
    return rgb, [rgb]


# ── Algorithm 3: Edge-weighted Color ─────────────────────────────────────────

def edge_weighted_color(frame: np.ndarray, num_clusters: int = 3) -> Tuple[RGB, list]:
    """
    Weight pixels by edge strength (Sobel). Edges dominate → better for movies.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0)
    sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    mag = np.sqrt(sx ** 2 + sy ** 2)

    # Flatten
    pixels = frame.reshape(-1, 3).astype(np.float32) / 255.0
    edge_w = mag.reshape(-1).astype(np.float32)
    edge_w = edge_w + edge_w.mean() * 0.5   # non-edge pixels still count
    edge_w /= edge_w.max()

    # Threshold: only reasonably bright pixels
    lum = 0.2126 * pixels[:, 0] + 0.7152 * pixels[:, 1] + 0.0722 * pixels[:, 2]
    mask = lum > 0.05
    if mask.sum() < 50:
        return (0, 0, 0), []

    salient = pixels[mask]
    weights = edge_w[mask]
    n = min(num_clusters, len(salient))
    km = KMeans(n_clusters=n, n_init=2, random_state=0)
    km.fit(salient, sample_weight=weights)
    counts = np.bincount(km.labels_)
    centers_srgb = np.clip(km.cluster_centers_ * 255, 0, 255).astype(int)
    dom = tuple(int(x) for x in centers_srgb[np.argmax(counts)])
    clusters = [tuple(int(x) for x in c) for c in centers_srgb]
    return dom, clusters


# ── Dispatch ──────────────────────────────────────────────────────────────────

def extract_color(frame: np.ndarray, mode: str = "dominant",
                  num_clusters: int = 3, brightness_cutoff: int = 20) -> Tuple[RGB, list]:
    if mode == "average":
        return average_color(frame)
    if mode == "edge_weighted":
        return edge_weighted_color(frame, num_clusters)
    return dominant_color(frame, num_clusters, brightness_cutoff)


# ── Post-processing pipeline ──────────────────────────────────────────────────

def process_color(r: int, g: int, b: int,
                  dark_threshold: int,
                  saturation_boost: float,
                  color_temp: int,
                  min_brightness: int,
                  max_brightness: int) -> Tuple[RGB, int]:
    """
    Apply saturation boost, dark suppression, color temp, and return (rgb, brightness).
    """
    lin = to_linear(np.array([r, g, b], dtype=np.uint8))
    brightness_lin = luminance_linear(*lin)
    brightness = int(brightness_lin * 255)

    if brightness < dark_threshold:
        return (0, 0, 0), min_brightness

    r, g, b = boost_saturation(r, g, b, saturation_boost)
    r, g, b = apply_color_temp(r, g, b, color_temp)
    brightness = int(np.clip(brightness, min_brightness, max_brightness))
    return (r, g, b), brightness
