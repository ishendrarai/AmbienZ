"""
preview_panel.py — Real-time color preview widget showing dominant color,
RGB/HSV values, brightness, and cluster swatches.
"""

import colorsys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QLinearGradient


class ColorSwatch(QWidget):
    """Single color swatch square."""

    def __init__(self, size: int = 28, parent=None):
        super().__init__(parent)
        self._color = QColor(30, 30, 30)
        self.setFixedSize(size, size)

    def set_color(self, r: int, g: int, b: int):
        self._color = QColor(r, g, b)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(QPen(QColor(60, 60, 60), 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)


class MainColorDisplay(QWidget):
    """Large gradient color preview rectangle."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._r, self._g, self._b = 20, 20, 30
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_color(self, r: int, g: int, b: int):
        self._r, self._g, self._b = r, g, b
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(2, 2, -2, -2)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        c = QColor(self._r, self._g, self._b)
        darker = c.darker(150)
        grad.setColorAt(0.0, c)
        grad.setColorAt(1.0, darker)
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(50, 50, 60), 1))
        p.drawRoundedRect(r, 10, 10)


class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header label
        hdr = QLabel("LIVE PREVIEW")
        hdr.setObjectName("sectionHeader")
        layout.addWidget(hdr)

        # Large color display
        self._main_color = MainColorDisplay()
        layout.addWidget(self._main_color)

        # Values row
        vals_row = QHBoxLayout()
        vals_row.setSpacing(16)
        self._lbl_rgb = QLabel("RGB — —")
        self._lbl_hsv = QLabel("HSV — —")
        self._lbl_bri = QLabel("BRI —")
        for lbl in (self._lbl_rgb, self._lbl_hsv, self._lbl_bri):
            lbl.setObjectName("metaLabel")
            vals_row.addWidget(lbl)
        vals_row.addStretch()
        layout.addLayout(vals_row)

        # Cluster swatches
        clust_row = QHBoxLayout()
        clust_row.setSpacing(6)
        clust_lbl = QLabel("Clusters:")
        clust_lbl.setObjectName("metaLabel")
        clust_row.addWidget(clust_lbl)
        self._swatches: list[ColorSwatch] = []
        for _ in range(6):
            sw = ColorSwatch(26)
            sw.setVisible(False)
            self._swatches.append(sw)
            clust_row.addWidget(sw)
        clust_row.addStretch()
        layout.addLayout(clust_row)

    def update_color(self, r: int, g: int, b: int, brightness: int, clusters: list):
        self._main_color.set_color(r, g, b)
        self._lbl_rgb.setText(f"RGB  {r}, {g}, {b}")

        # HSV
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        self._lbl_hsv.setText(f"HSV  {int(h*360)}°, {int(s*100)}%, {int(v*100)}%")
        self._lbl_bri.setText(f"BRI  {brightness}")

        # Clusters
        for i, sw in enumerate(self._swatches):
            if i < len(clusters):
                cr, cg, cb = clusters[i]
                sw.set_color(cr, cg, cb)
                sw.setVisible(True)
            else:
                sw.setVisible(False)
