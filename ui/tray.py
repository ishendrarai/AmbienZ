"""
tray.py — System tray icon with dynamic color reflection and menu.
"""

import threading
from typing import Callable, Optional


def start_tray(on_start: Callable, on_stop: Callable,
               on_open: Callable, on_quit: Callable,
               icon_path: Optional[str] = None):
    """
    Launch a system-tray icon in a background daemon thread.
    Requires pystray + Pillow; silently no-ops if unavailable.
    """
    try:
        import pystray
        from PIL import Image as PilImage

        if icon_path and __import__("os").path.exists(icon_path):
            img = PilImage.open(icon_path).resize((64, 64))
        else:
            img = _make_default_icon()

        state = {"icon": None}

        def _start(icon, _):     on_start()
        def _stop(icon, _):      on_stop()
        def _open(icon, _):      on_open()
        def _quit(icon, _):
            on_quit()
            icon.stop()

        menu = pystray.Menu(
            pystray.MenuItem("Start Sync", _start),
            pystray.MenuItem("Stop Sync",  _stop),
            pystray.MenuItem("Open UI",    _open),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit",       _quit),
        )
        tray = pystray.Icon("LightWiz", img, "Light Wiz", menu)
        state["icon"] = tray

        def _run():
            tray.run()

        t = threading.Thread(target=_run, daemon=True, name="TrayThread")
        t.start()
        return state
    except ImportError:
        return {}


def update_tray_color(state: dict, r: int, g: int, b: int):
    """Dynamically recolor the tray icon to reflect the current screen color."""
    try:
        from PIL import Image as PilImage, ImageDraw
        icon = state.get("icon")
        if icon is None:
            return
        img = PilImage.new("RGB", (64, 64), color=(r, g, b))
        draw = ImageDraw.Draw(img)
        draw.ellipse([8, 8, 56, 56], fill=(r, g, b), outline=(255, 255, 255))
        icon.icon = img
    except Exception:
        pass


def _make_default_icon():
    try:
        from PIL import Image as PilImage, ImageDraw
        img = PilImage.new("RGB", (64, 64), color=(15, 17, 23))
        draw = ImageDraw.Draw(img)
        draw.ellipse([8, 8, 56, 56], fill=(60, 100, 220), outline=(100, 140, 255))
        return img
    except ImportError:
        return None
