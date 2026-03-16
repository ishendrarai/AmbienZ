"""
controls.py — Sliders, radio buttons, and algorithm selectors for Light Wiz.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QRadioButton, QButtonGroup, QSpinBox, QGroupBox,
    QComboBox, QCheckBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal


class LabeledSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, label: str, min_val: float, max_val: float,
                 step: float, initial: float, fmt: str = ".2f", parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._step = step
        self._fmt = fmt
        self._scale = round(1.0 / step) if step < 1 else 1

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        self._name_lbl = QLabel(label)
        self._name_lbl.setObjectName("sliderLabel")
        self._name_lbl.setFixedWidth(130)
        row.addWidget(self._name_lbl)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(int(min_val * self._scale))
        self._slider.setMaximum(int(max_val * self._scale))
        self._slider.setValue(int(initial * self._scale))
        self._slider.setObjectName("paramSlider")
        row.addWidget(self._slider, 1)

        self._val_lbl = QLabel(format(initial, fmt))
        self._val_lbl.setObjectName("sliderValue")
        self._val_lbl.setFixedWidth(48)
        self._val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(self._val_lbl)

        self._slider.valueChanged.connect(self._on_change)

    def _on_change(self, v: int):
        val = v / self._scale
        self._val_lbl.setText(format(val, self._fmt))
        self.valueChanged.emit(val)

    def set_value(self, val: float):
        self._slider.blockSignals(True)
        self._slider.setValue(int(val * self._scale))
        self._val_lbl.setText(format(val, self._fmt))
        self._slider.blockSignals(False)

    def value(self) -> float:
        return self._slider.value() / self._scale


class ControlsPanel(QWidget):
    """
    All parameter controls. Emits cfg_changed(key, value) when anything changes.
    """
    cfg_changed = Signal(str, object)

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self._cfg = cfg
        self._setup_ui()

    def _section(self, title: str) -> QGroupBox:
        box = QGroupBox(title)
        box.setObjectName("controlGroup")
        return box

    def _setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(12)

        # ── Parameters ────────────────────────────────────────────────────────
        param_box = self._section("Parameters")
        pv = QVBoxLayout(param_box)
        pv.setSpacing(6)

        self._sl_sat  = LabeledSlider("Saturation Boost",  0.5, 3.0, 0.05, self._cfg["saturation_boost"])
        self._sl_bri  = LabeledSlider("Max Brightness",     10, 255,   1,   self._cfg["max_brightness"], ".0f")
        self._sl_fps  = LabeledSlider("Target FPS",          5, 120,   1,   self._cfg["send_fps"],       ".0f")
        self._sl_dark = LabeledSlider("Dark Threshold",      0,  80,   1,   self._cfg["dark_threshold"], ".0f")
        self._sl_cct  = LabeledSlider("Color Temp (K)",   2700, 9000, 50,   self._cfg["color_temp"],    ".0f")
        self._sl_smooth = LabeledSlider("Smoothness",       0.0,  1.0, 0.01, self._cfg["base_smooth"])

        for sl, key in (
            (self._sl_sat,    "saturation_boost"),
            (self._sl_bri,    "max_brightness"),
            (self._sl_fps,    "send_fps"),
            (self._sl_dark,   "dark_threshold"),
            (self._sl_cct,    "color_temp"),
            (self._sl_smooth, "base_smooth"),
        ):
            _key = key
            sl.valueChanged.connect(lambda v, k=_key: self.cfg_changed.emit(k, v))
            pv.addWidget(sl)

        main.addWidget(param_box)

        # ── Algorithm ─────────────────────────────────────────────────────────
        algo_box = self._section("Algorithm")
        av = QVBoxLayout(algo_box)
        av.setSpacing(6)

        self._algo_group = QButtonGroup(self)
        for label, key in (
            ("Dominant Color (KMeans)", "dominant"),
            ("Average Color (Fast)", "average"),
            ("Edge-Weighted Color", "edge_weighted"),
        ):
            rb = QRadioButton(label)
            rb.setObjectName("algoRadio")
            if self._cfg.get("algorithm_mode") == key:
                rb.setChecked(True)
            _key = key
            rb.toggled.connect(lambda checked, k=_key: checked and self.cfg_changed.emit("algorithm_mode", k))
            self._algo_group.addButton(rb)
            av.addWidget(rb)

        clust_row = QHBoxLayout()
        lbl = QLabel("Clusters:")
        lbl.setObjectName("sliderLabel")
        clust_row.addWidget(lbl)
        self._spin_clusters = QSpinBox()
        self._spin_clusters.setRange(1, 6)
        self._spin_clusters.setValue(self._cfg.get("num_clusters", 3))
        self._spin_clusters.setObjectName("spinBox")
        self._spin_clusters.valueChanged.connect(lambda v: self.cfg_changed.emit("num_clusters", v))
        clust_row.addWidget(self._spin_clusters)
        clust_row.addStretch()
        av.addLayout(clust_row)

        self._chk_temporal = QCheckBox("Temporal Stabilization (Kalman)")
        self._chk_temporal.setObjectName("checkBox")
        self._chk_temporal.setChecked(self._cfg.get("temporal_smooth", False))
        self._chk_temporal.toggled.connect(lambda v: self.cfg_changed.emit("temporal_smooth", v))
        av.addWidget(self._chk_temporal)

        main.addWidget(algo_box)

        # ── Capture ───────────────────────────────────────────────────────────
        cap_box = self._section("Capture")
        cv = QVBoxLayout(cap_box)
        cv.setSpacing(6)

        res_row = QHBoxLayout()
        rl = QLabel("Resolution:")
        rl.setObjectName("sliderLabel")
        res_row.addWidget(rl)
        self._cb_res = QComboBox()
        self._cb_res.setObjectName("comboBox")
        for label, val in (("Full (1.0×)", 1.0), ("Half (0.5×)", 0.5), ("Quarter (0.25×)", 0.25)):
            self._cb_res.addItem(label, val)
        cur_scale = self._cfg.get("capture_scale", 1.0)
        for i in range(self._cb_res.count()):
            if self._cb_res.itemData(i) == cur_scale:
                self._cb_res.setCurrentIndex(i)
        self._cb_res.currentIndexChanged.connect(
            lambda _: self.cfg_changed.emit("capture_scale", self._cb_res.currentData())
        )
        res_row.addWidget(self._cb_res)
        res_row.addStretch()
        cv.addLayout(res_row)

        region_row = QHBoxLayout()
        rl2 = QLabel("Region:")
        rl2.setObjectName("sliderLabel")
        region_row.addWidget(rl2)
        self._cb_region = QComboBox()
        self._cb_region.setObjectName("comboBox")
        for label, val in (("Full Screen", "full"), ("Top Edge", "top"), ("Bottom Edge", "bottom")):
            self._cb_region.addItem(label, val)
        cur_region = self._cfg.get("capture_region", "full")
        for i in range(self._cb_region.count()):
            if self._cb_region.itemData(i) == cur_region:
                self._cb_region.setCurrentIndex(i)
        self._cb_region.currentIndexChanged.connect(
            lambda _: self.cfg_changed.emit("capture_region", self._cb_region.currentData())
        )
        region_row.addWidget(self._cb_region)
        region_row.addStretch()
        cv.addLayout(region_row)

        main.addWidget(cap_box)

        # ── Scene presets ─────────────────────────────────────────────────────
        scene_box = self._section("Scene Preset")
        sv = QHBoxLayout(scene_box)
        sv.setSpacing(6)
        scenes = [("Movie", "movie"), ("Gaming", "gaming"), ("Music", "music"), ("Ambient", "ambient")]
        self._scene_btns = {}
        for label, key in scenes:
            btn = QPushButton(label)
            btn.setObjectName("sceneBtn")
            btn.setCheckable(True)
            if self._cfg.get("scene_mode") == key:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, k=key: self._apply_scene(k))
            sv.addWidget(btn)
            self._scene_btns[key] = btn

        main.addWidget(scene_box)
        main.addStretch()

    # Scene presets
    _SCENES = {
        "movie":   {"send_fps": 20, "base_smooth": 0.85, "num_clusters": 3, "saturation_boost": 1.3},
        "gaming":  {"send_fps": 60, "base_smooth": 0.3,  "num_clusters": 2, "saturation_boost": 1.6},
        "music":   {"send_fps": 30, "base_smooth": 0.5,  "num_clusters": 2, "saturation_boost": 2.0},
        "ambient": {"send_fps": 40, "base_smooth": 0.8,  "num_clusters": 3, "saturation_boost": 1.4},
    }

    def _apply_scene(self, key: str):
        # Uncheck other scene buttons
        for k, btn in self._scene_btns.items():
            btn.setChecked(k == key)
        self.cfg_changed.emit("scene_mode", key)
        for param, val in self._SCENES[key].items():
            self.cfg_changed.emit(param, val)
        # Update sliders to reflect new values
        scene = self._SCENES[key]
        self._sl_fps.set_value(scene["send_fps"])
        self._sl_smooth.set_value(scene["base_smooth"])
        self._spin_clusters.setValue(scene["num_clusters"])
        self._sl_sat.set_value(scene["saturation_boost"])

    def load_cfg(self, cfg: dict):
        """Refresh all controls from a config dict."""
        self._sl_sat.set_value(cfg.get("saturation_boost", 1.4))
        self._sl_bri.set_value(cfg.get("max_brightness", 255))
        self._sl_fps.set_value(cfg.get("send_fps", 40))
        self._sl_dark.set_value(cfg.get("dark_threshold", 20))
        self._sl_cct.set_value(cfg.get("color_temp", 6500))
        self._sl_smooth.set_value(cfg.get("base_smooth", 0.8))
        self._spin_clusters.setValue(cfg.get("num_clusters", 3))
        self._chk_temporal.setChecked(cfg.get("temporal_smooth", False))
