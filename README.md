<div align="center">

<img src="assets/icon.png" alt="Light Wiz Logo" width="80" height="80"/>

# 💡 Light Wiz

### Screen-to-WiZ Ambient Lighting Sync

**A professional desktop ambient lighting controller that syncs your screen colors to WiZ smart bulbs in real time.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41cd52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)]()

*Inspired by Philips Hue Sync and Govee Desktop App*

[Features](#-features) · [Installation](#-installation) · [Usage](#-usage) · [Configuration](#-configuration) · [Build .exe](#-building-the-executable) · [FAQ](#-faq)

---

</div>

## ✨ Features

| Feature | Description |
|---|---|
| 🎨 **3 Color Algorithms** | Dominant KMeans, Average, and Edge-Weighted extraction |
| 🔬 **Color Accuracy** | Gamma-corrected pipeline, perceptual luminance, color temperature 2700K–9000K |
| 🌊 **Adaptive Smoothing** | Exponential + optional Kalman filter for temporal stabilization |
| 🖥️ **Modern Dark UI** | PySide6 GUI with live color preview, cluster swatches, RGB/HSV readout |
| 🎬 **Scene Presets** | Movie, Gaming, Music, Ambient — one-click tuning |
| 📡 **Device Discovery** | UDP broadcast scan to auto-find WiZ bulbs on your network |
| ⚡ **Performance Scaling** | Auto fallback to lower resolution when frame time is too high |
| 🔔 **System Tray** | Background operation; tray icon dynamically reflects current screen color |
| 💾 **Config Persistence** | All settings auto-saved/loaded from `config.json` |
| 📦 **Portable .exe** | Single-file PyInstaller build — no Python needed on target machine |

---

## 📸 Screenshots

> Add your own screenshots here once the app is running.

```
[ Screenshot of main window ]     [ Screenshot of tray icon ]
```

---

## 📋 Requirements

- **Python** 3.10 or higher
- **WiZ smart bulb** connected to your local Wi-Fi network
- Windows 10/11 (primary), macOS, or Linux

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/ishendrarai/Wizard_Light.git
cd LightWiz
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install PySide6 mss opencv-python numpy scikit-learn Pillow pystray pyinstaller
```

### 3. Run

```bash
python main.py
```

---

## 🖱️ Usage

### First-time setup

1. **Find your bulb's IP address** — see [Finding Your Bulb's IP](#-finding-your-bulbs-ip)
2. **Enter the IP** in the *Bulb IP* field at the top of the UI, or click **Discover** to auto-scan
3. **Click Start Sync** — your bulb will immediately begin mirroring your screen

### Controls overview

| Control | What it does |
|---|---|
| **Start Sync / Stop** | Toggle the sync loop on/off |
| **Test Color** | Sends a white→red→green→blue→off test sequence to verify connection |
| **Discover** | UDP broadcast scan to find WiZ bulbs on your network |
| **Save Config** | Persist all current settings to `config.json` |
| **Reset** | Restore all settings to defaults |

---

## 🎨 Algorithm Modes

### Dominant Color (KMeans)
Clusters screen pixels by color using K-Means with brightness weighting. Best for films and games with distinct color palettes.

### Average Color
Simple mean of all screen pixels. Fastest mode, lowest CPU usage. Best for 60+ FPS or weaker hardware.

### Edge-Weighted Color
Weights pixels by Sobel edge magnitude before clustering. Action areas and edges are emphasized — excellent for fast-paced movies and gaming.

---

## 🎬 Scene Presets

| Scene | FPS | Smoothness | Clusters | Saturation | Best For |
|-------|-----|------------|----------|------------|----------|
| 🎬 Movie | 20 | 0.85 | 3 | 1.3× | Films, TV shows |
| 🎮 Gaming | 60 | 0.30 | 2 | 1.6× | Fast-paced games |
| 🎵 Music | 30 | 0.50 | 2 | 2.0× | Music visualization |
| 🌿 Ambient | 40 | 0.80 | 3 | 1.4× | General use |

---

## 🔬 Color Accuracy Pipeline

```
Raw Screen Pixels
      │
      ▼
Convert to linear RGB        (gamma = 2.2)
      │
      ▼
Perceptual luminance         Y = 0.2126R + 0.7152G + 0.0722B
      │
      ▼
Color extraction             (KMeans / Average / Edge-Weighted)
      │
      ▼
Saturation boost             (HSV space — configurable multiplier)
      │
      ▼
Color temperature mapping    (white-point scaling 2700K–9000K)
      │
      ▼
Adaptive smoothing           (exponential decay or Kalman filter)
      │
      ▼
UDP → WiZ Bulb               (setPilot JSON over port 38899)
```

---

## ⚙️ Configuration

All settings live in `config.json` next to `main.py`. Edit manually or use the **Save Config** button in the UI.

| Key | Default | Description |
|-----|---------|-------------|
| `device_ip` | `192.168.0.100` | WiZ bulb IP address |
| `port` | `38899` | WiZ UDP port (do not change unless needed) |
| `send_fps` | `40` | Target frames per second to send to bulb |
| `min_brightness` | `10` | Minimum dimming value (0–255) |
| `max_brightness` | `255` | Maximum dimming value (0–255) |
| `dark_threshold` | `20` | Pixels below this luminance are treated as black |
| `saturation_boost` | `1.4` | Saturation multiplier (1.0 = no boost) |
| `base_smooth` | `0.8` | Smoothing factor for slow changes (0–1) |
| `fast_smooth` | `0.3` | Smoothing factor for fast changes (0–1) |
| `num_clusters` | `3` | KMeans cluster count for dominant color |
| `color_temp` | `6500` | White balance in Kelvin (2700–9000) |
| `algorithm_mode` | `dominant` | `dominant` / `average` / `edge_weighted` |
| `capture_scale` | `1.0` | Resolution scale factor (`1.0`, `0.5`, `0.25`) |
| `temporal_smooth` | `false` | Enable Kalman filter temporal stabilization |
| `capture_region` | `full` | `full` / `top` / `bottom` / `custom` |
| `scene_mode` | `ambient` | `movie` / `gaming` / `music` / `ambient` |

---

## 📁 Project Structure

```
LightWiz/
├── main.py                    ← Entry point + system tray launch
├── config.json                ← Persistent user settings
├── requirements.txt           ← Python dependencies
├── LightWiz.spec              ← PyInstaller build spec
│
├── core/
│   ├── capture.py             ← Screen capture (mss) with region + scale support
│   ├── color_engine.py        ← Color extraction, gamma, color temp, saturation boost
│   ├── smoothing.py           ← Adaptive exponential + Kalman smoothers
│   ├── sync_engine.py         ← Main capture → color → smooth → send loop thread
│   └── wiz_protocol.py        ← UDP WiZ bulb communication (setPilot JSON)
│
├── ui/
│   ├── main_window.py         ← PySide6 main application window
│   ├── controls.py            ← Sliders, algorithm selectors, scene preset buttons
│   ├── preview_panel.py       ← Live color display, cluster swatches, RGB/HSV values
│   └── tray.py                ← System tray icon with dynamic color reflection
│
├── utils/
│   ├── config_manager.py      ← Load / save config.json with defaults fallback
│   └── device_discovery.py    ← UDP broadcast WiZ bulb discovery
│
└── assets/
    ├── icon.png               ← App icon (64×64 PNG)
    └── icon.ico               ← Windows .exe icon (optional)
```

---

## 📦 Building the Executable

### Option A — Use the included spec (recommended)

Bundles `config.json` and `assets/` automatically:

```bash
pip install pyinstaller
pyinstaller LightWiz.spec
```

### Option B — Quick one-liner

```bash
pyinstaller --onefile --noconsole --name LightWiz main.py
```

### Option C — With assets bundled (manual)

**Windows:**
```bash
pyinstaller --onefile --noconsole --name LightWiz ^
            --add-data "config.json;." ^
            --add-data "assets;assets" ^
            main.py
```

**macOS / Linux:**
```bash
pyinstaller --onefile --noconsole --name LightWiz \
            --add-data "config.json:." \
            --add-data "assets:assets" \
            main.py
```

> **Note:** On Windows, use `;` as the separator. On macOS/Linux, use `:`.

Output: `dist/LightWiz.exe`

### If the build fails with sklearn errors

```bash
pyinstaller --onefile --noconsole --collect-all sklearn --name LightWiz main.py
```

> **Windows Defender note:** On first run, Defender may flag the `.exe`. Add an exclusion for the `dist/` folder if needed. This is a false positive common with PyInstaller builds.

---

## 📡 Finding Your Bulb's IP

### Option 1 — Use the Discover button *(easiest)*
Click **Discover** in the UI. Light Wiz broadcasts a UDP packet and auto-fills the IP of the first responding bulb.

### Option 2 — WiZ mobile app
`App → Device → Settings → Device Info → IP Address`

### Option 3 — Router admin panel
Log into your router (usually `192.168.0.1` or `192.168.1.1`) and look for a device named **WiZ** or **ESP** in the connected devices list.

### Option 4 — Network scanner
Use a tool like [Advanced IP Scanner](https://www.advanced-ip-scanner.com/) (Windows) or `nmap -sn 192.168.0.0/24` to scan for devices.

---

## 🧠 How It Works

Light Wiz runs a high-frequency capture loop in a background thread:

1. **Capture** — `mss` grabs a frame from your screen at the configured resolution and region
2. **Extract** — The chosen algorithm (KMeans/Average/Edge) finds the dominant color
3. **Correct** — Gamma correction, saturation boost, and color temperature are applied
4. **Smooth** — Adaptive exponential smoothing or Kalman filter prevents jarring flicker
5. **Send** — A `setPilot` JSON command is sent via UDP to the WiZ bulb at up to 60 FPS

The WiZ protocol is a simple JSON-over-UDP API on port `38899`. No cloud, no account, no latency.

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Bulb not responding | Check IP address is correct. Try **Test Color** button. Ensure bulb and PC are on same Wi-Fi network. |
| High CPU usage | Switch to **Average Color** mode, reduce Clusters to 2, or set Resolution to **Half (0.5×)** |
| Colors feel washed out | Increase **Saturation Boost** to 1.8–2.2 |
| Too much flickering | Increase **Smoothness** slider toward 0.9, or enable **Temporal Stabilization** |
| Slow / laggy response | Lower **Smoothness** to 0.2–0.4, or use **Gaming** preset |
| App crashes on launch | Ensure all dependencies are installed: `pip install -r requirements.txt` |
| `.exe` flagged by antivirus | False positive from PyInstaller. Add `dist/LightWiz.exe` to your AV exclusions. |
| Bulb not found by Discover | Some routers block UDP broadcast. Enter the IP manually instead. |

---

## 💡 Tips & Tricks

- **Warm movie atmosphere** → Set Color Temp to **3000K** + use **Movie** preset
- **Competitive gaming** → Use **Gaming** preset for maximum responsiveness (60 FPS, low smoothing)
- **Music sync** → Use **Music** preset with high saturation for vibrant, reactive colors
- **Multi-monitor** → The app captures monitor index 1 by default (primary display)
- **Dark content** → Increase **Dark Threshold** if the bulb goes off too often during dark scenes
- **Tray icon** → The system tray icon color dynamically reflects the current detected screen color

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and test them
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature-name`
6. Open a Pull Request

### Ideas for contributions
- [ ] Multi-monitor support with per-monitor zone mapping
- [ ] Multi-bulb sync (broadcast to multiple IPs simultaneously)
- [ ] Audio reactive mode (microphone input → color)
- [ ] Custom region selector (drag-to-select screen area)
- [ ] WLED / Govee / Tapo protocol support
- [ ] macOS `.app` build guide

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You are free to use, modify, and distribute this software for any purpose.

---

## 🙏 Acknowledgements

- [pywizlight](https://github.com/sbidy/pywizlight) — WiZ protocol reference
- [mss](https://github.com/BoboTiG/python-mss) — Fast cross-platform screen capture
- [scikit-learn](https://scikit-learn.org/) — KMeans color clustering
- [PySide6 / Qt](https://doc.qt.io/qtforpython/) — GUI framework
- [pystray](https://github.com/moses-palmer/pystray) — System tray integration

---

<div align="center">

Made with ❤️ for smart home enthusiasts

⭐ **Star this repo if you find it useful!**

</div>
