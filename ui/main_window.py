"""
main_window.py — Main PySide6 application window for Light Wiz.
"""

import os
import threading
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QScrollArea, QFrame, QMessageBox,
    QSizePolicy, QStatusBar
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush

from ui.preview_panel import PreviewPanel
from ui.controls import ControlsPanel
from core.sync_engine import SyncEngine
from utils import config_manager, device_discovery


# ── Dark stylesheet ───────────────────────────────────────────────────────────
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0f1117;
    color: #d0d4e0;
    font-family: "Segoe UI", "SF Pro Text", system-ui, sans-serif;
    font-size: 13px;
}

QScrollArea { border: none; }

#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #e8eaf6;
    letter-spacing: 2px;
}

#subtitleLabel {
    font-size: 11px;
    color: #5c6080;
    letter-spacing: 3px;
}

#sectionHeader {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #6a7090;
    text-transform: uppercase;
    margin-bottom: 4px;
}

#controlGroup {
    border: 1px solid #1e2030;
    border-radius: 8px;
    padding: 10px;
    margin-top: 4px;
    background-color: #13161f;
}

#controlGroup::title {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #5a6080;
    subcontrol-origin: margin;
    padding: 0 6px;
}

#sliderLabel {
    color: #8890a8;
    font-size: 12px;
}

#sliderValue {
    color: #c5cadc;
    font-size: 12px;
    font-variant-numeric: tabular-nums;
}

#paramSlider::groove:horizontal {
    height: 4px;
    background: #1e2235;
    border-radius: 2px;
}

#paramSlider::handle:horizontal {
    background: #5870f0;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

#paramSlider::sub-page:horizontal {
    background: #3d50c0;
    border-radius: 2px;
}

#algoRadio {
    color: #9098b8;
    font-size: 12px;
    spacing: 6px;
}

#algoRadio::indicator {
    width: 14px; height: 14px;
    border-radius: 7px;
    border: 2px solid #3a3f58;
    background: #13161f;
}

#algoRadio::indicator:checked {
    background: #5870f0;
    border-color: #5870f0;
}

#checkBox {
    color: #9098b8;
    font-size: 12px;
}

#checkBox::indicator {
    width: 14px; height: 14px;
    border-radius: 3px;
    border: 2px solid #3a3f58;
    background: #13161f;
}

#checkBox::indicator:checked {
    background: #5870f0;
    border-color: #5870f0;
}

#spinBox {
    background: #1a1d2a;
    border: 1px solid #2a2e42;
    border-radius: 5px;
    color: #c8cce0;
    padding: 2px 8px;
    width: 60px;
}

#comboBox {
    background: #1a1d2a;
    border: 1px solid #2a2e42;
    border-radius: 5px;
    color: #c8cce0;
    padding: 3px 8px;
    min-width: 140px;
}

#comboBox QAbstractItemView {
    background: #1a1d2a;
    border: 1px solid #2a2e42;
    selection-background-color: #3040a0;
}

#metaLabel {
    color: #6a7490;
    font-size: 11px;
    font-variant-numeric: tabular-nums;
}

QPushButton {
    background-color: #1e2235;
    color: #b0b8d0;
    border: 1px solid #2a2e42;
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #252a40;
    color: #d0d8f0;
}

#startBtn {
    background-color: #2a4ad0;
    color: #e0e8ff;
    border: none;
    font-weight: 600;
    font-size: 13px;
}

#startBtn:hover { background-color: #3050e0; }
#startBtn:checked {
    background-color: #1a3090;
    color: #a0aacc;
}

#stopBtn {
    background-color: #3a1a1a;
    color: #e08080;
    border: 1px solid #5a2020;
}

#stopBtn:hover { background-color: #4a2020; }

#testBtn {
    background-color: #1a3a2a;
    color: #70d0a0;
    border: 1px solid #20503a;
}

#testBtn:hover { background-color: #204830; }

#sceneBtn {
    background-color: #181c2a;
    color: #7080a0;
    border: 1px solid #22263a;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 11px;
}

#sceneBtn:hover { background-color: #20243a; color: #90a0c0; }
#sceneBtn:checked {
    background-color: #1e2e80;
    color: #b0c0ff;
    border-color: #3050d0;
}

QLineEdit {
    background-color: #1a1d2a;
    border: 1px solid #2a2e42;
    border-radius: 5px;
    color: #c8cce0;
    padding: 4px 8px;
}

#statusBar {
    background-color: #0a0c14;
    border-top: 1px solid #1a1e2a;
    color: #404860;
    font-size: 11px;
}

#statusDot {
    font-size: 14px;
}

#deviceFrame {
    background-color: #13161f;
    border: 1px solid #1e2030;
    border-radius: 8px;
    padding: 8px;
}

#perfLabel {
    color: #404e70;
    font-size: 11px;
    font-variant-numeric: tabular-nums;
}

#discoverBtn {
    background-color: #1a2a1a;
    color: #60c080;
    border: 1px solid #204030;
    padding: 4px 12px;
    font-size: 11px;
}
#discoverBtn:hover { background-color: #203420; }

#saveBtn {
    background-color: #1a2535;
    color: #70a0d0;
    border: 1px solid #203050;
}
#saveBtn:hover { background-color: #203040; }

#resetBtn {
    background-color: #201820;
    color: #9070a0;
    border: 1px solid #30204a;
}
#resetBtn:hover { background-color: #281e2e; }

#divider {
    background-color: #1a1e2a;
    max-height: 1px;
    min-height: 1px;
}
"""


class ColorUpdateSignal(QWidget):
    """Helper to safely pass color data from worker thread → main thread."""
    color_updated = Signal(int, int, int, int, list, float, float)
    status_changed = Signal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = config_manager.load()
        self._engine: SyncEngine = None
        self._signals = ColorUpdateSignal()

        self.setWindowTitle("Light Wiz")
        self.setMinimumSize(540, 820)
        self.setStyleSheet(STYLESHEET)
        self._build_ui()
        self._init_engine()
        self._start_refresh_timer()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(20, 20, 20, 10)
        root_layout.setSpacing(14)
        self.setCentralWidget(root)

        # Title
        title_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        t = QLabel("LIGHT WIZ")
        t.setObjectName("titleLabel")
        title_col.addWidget(t)
        sub = QLabel("SCREEN AMBIENT SYNC")
        sub.setObjectName("subtitleLabel")
        title_col.addWidget(sub)
        title_row.addLayout(title_col)
        title_row.addStretch()

        # Status dot + label
        self._lbl_status_dot = QLabel("●")
        self._lbl_status_dot.setObjectName("statusDot")
        self._lbl_status_dot.setStyleSheet("color: #304060;")
        self._lbl_status = QLabel("Stopped")
        self._lbl_status.setObjectName("metaLabel")
        title_row.addWidget(self._lbl_status_dot)
        title_row.addWidget(self._lbl_status)
        root_layout.addLayout(title_row)

        # Divider
        div = QFrame(); div.setObjectName("divider"); root_layout.addWidget(div)

        # Device row
        dev_frame = QFrame(); dev_frame.setObjectName("deviceFrame")
        dev_layout = QHBoxLayout(dev_frame)
        dev_layout.setContentsMargins(8, 6, 8, 6)
        dev_layout.setSpacing(8)
        dev_lbl = QLabel("Bulb IP:")
        dev_lbl.setObjectName("metaLabel")
        dev_layout.addWidget(dev_lbl)
        self._ip_edit = QLineEdit(self.cfg.get("device_ip", "192.168.0.100"))
        self._ip_edit.setFixedWidth(140)
        self._ip_edit.editingFinished.connect(self._on_ip_changed)
        dev_layout.addWidget(self._ip_edit)
        disc_btn = QPushButton("Discover")
        disc_btn.setObjectName("discoverBtn")
        disc_btn.clicked.connect(self._on_discover)
        dev_layout.addWidget(disc_btn)
        dev_layout.addStretch()
        self._lbl_perf = QLabel("FPS: –  |  Frame: –")
        self._lbl_perf.setObjectName("perfLabel")
        dev_layout.addWidget(self._lbl_perf)
        root_layout.addWidget(dev_frame)

        # Live preview
        self._preview = PreviewPanel()
        root_layout.addWidget(self._preview)

        div2 = QFrame(); div2.setObjectName("divider"); root_layout.addWidget(div2)

        # Scrollable controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollBar:vertical { width: 6px; background: #0f1117; }"
                             "QScrollBar::handle:vertical { background: #2a2e42; border-radius: 3px; }"
                             "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }")
        self._controls = ControlsPanel(self.cfg)
        self._controls.cfg_changed.connect(self._on_cfg_changed)
        scroll.setWidget(self._controls)
        root_layout.addWidget(scroll, 1)

        div3 = QFrame(); div3.setObjectName("divider"); root_layout.addWidget(div3)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._btn_start = QPushButton("▶  Start Sync")
        self._btn_start.setObjectName("startBtn")
        self._btn_start.setCheckable(True)
        self._btn_start.clicked.connect(self._on_start_stop)

        self._btn_stop = QPushButton("■  Stop")
        self._btn_stop.setObjectName("stopBtn")
        self._btn_stop.clicked.connect(self._on_stop)

        btn_test = QPushButton("◈  Test Color")
        btn_test.setObjectName("testBtn")
        btn_test.clicked.connect(self._on_test)

        btn_save = QPushButton("Save Config")
        btn_save.setObjectName("saveBtn")
        btn_save.clicked.connect(self._on_save)

        btn_reset = QPushButton("Reset")
        btn_reset.setObjectName("resetBtn")
        btn_reset.clicked.connect(self._on_reset)

        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_stop)
        btn_row.addWidget(btn_test)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_reset)
        root_layout.addLayout(btn_row)

        # Status bar
        self.statusBar().setObjectName("statusBar")
        self.statusBar().showMessage("Light Wiz ready.")

    # ── Engine init ───────────────────────────────────────────────────────────

    def _init_engine(self):
        self._engine = SyncEngine(self.cfg)
        self._signals.color_updated.connect(self._on_color_update)
        self._signals.status_changed.connect(self._on_status_change)

        self._engine.on_color_update = lambda r, g, b, br, cl, fps, ms: \
            self._signals.color_updated.emit(r, g, b, br, cl, fps, ms)
        self._engine.on_status_change = lambda s: \
            self._signals.status_changed.emit(s)

    def _start_refresh_timer(self):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(100)

    def _tick(self):
        """Periodic housekeeping (can be expanded)."""
        pass

    # ── Slots ─────────────────────────────────────────────────────────────────

    @Slot(int, int, int, int, list, float, float)
    def _on_color_update(self, r, g, b, brightness, clusters, fps, frame_ms):
        self._preview.update_color(r, g, b, brightness, clusters)
        self._lbl_perf.setText(f"FPS: {fps:.0f}  |  Frame: {frame_ms:.1f} ms")

    @Slot(str)
    def _on_status_change(self, status: str):
        self._lbl_status.setText(status)
        if status == "Running":
            self._lbl_status_dot.setStyleSheet("color: #40d080;")
            self._btn_start.setText("▶  Running…")
            self._btn_start.setChecked(True)
            self.statusBar().showMessage("Sync active.")
        else:
            self._lbl_status_dot.setStyleSheet("color: #304060;")
            self._btn_start.setText("▶  Start Sync")
            self._btn_start.setChecked(False)
            self.statusBar().showMessage("Sync stopped.")

    def _on_cfg_changed(self, key: str, value):
        self.cfg[key] = value
        if key in ("send_fps", "base_smooth", "fast_smooth"):
            pass  # picked up live by engine loop
        self.statusBar().showMessage(f"Updated {key} → {value}", 2000)

    def _on_ip_changed(self):
        ip = self._ip_edit.text().strip()
        if ip:
            self.cfg["device_ip"] = ip
            if self._engine:
                self._engine.update_device(ip, self.cfg.get("port", 38899))

    def _on_start_stop(self):
        if self._engine.is_running():
            self._engine.stop()
        else:
            self._engine.start()

    def _on_stop(self):
        if self._engine.is_running():
            self._engine.stop()

    def _on_test(self):
        """Send a test color burst (white, red, green, blue, off)."""
        if not self._engine:
            return
        was_running = self._engine.is_running()
        if was_running:
            self._engine.stop()

        from core.wiz_protocol import WizSender
        s = WizSender(self.cfg["device_ip"], self.cfg["port"])
        import time
        for (r, g, b) in [(255,255,255),(255,0,0),(0,255,0),(0,100,255),(0,0,0)]:
            s.send_color(r, g, b, 200)
            time.sleep(0.4)
        s.close()

        if was_running:
            self._engine.start()

    def _on_save(self):
        config_manager.save(self.cfg)
        self.statusBar().showMessage("Config saved.", 3000)

    def _on_reset(self):
        defaults = config_manager.DEFAULTS.copy()
        self.cfg.update(defaults)
        self._controls.load_cfg(self.cfg)
        self._ip_edit.setText(self.cfg["device_ip"])
        self.statusBar().showMessage("Config reset to defaults.", 3000)

    def _on_discover(self):
        self.statusBar().showMessage("Discovering WiZ bulbs…")

        def _done(results):
            self._signals.status_changed.emit("Stopped" if not self._engine.is_running() else "Running")
            if not results:
                self.statusBar().showMessage("No bulbs found on network.", 4000)
                return
            # Pick first result
            found = results[0]
            self._ip_edit.setText(found["ip"])
            self.cfg["device_ip"] = found["ip"]
            if self._engine:
                self._engine.update_device(found["ip"])
            self.statusBar().showMessage(
                f"Found {len(results)} bulb(s). Using {found['ip']} ({found['name']}).", 5000
            )

        device_discovery.discover_async(_done)

    def closeEvent(self, event):
        if self._engine:
            self._engine.close()
        super().closeEvent(event)
