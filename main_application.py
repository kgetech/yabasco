###########################################################################################
## yabasco: Yet Another BAsic Smith Chart gizmO
## Copyright (C) 2025  Kyle Thomas Goodman
## email: kylegoodman@kgindustrial.com
## GitHub: https://github.com/kgetech/
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <https://www.gnu.org/licenses/>.
###########################################################################################

# language: python
import sys
import numpy as np
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QDockWidget, QColorDialog, QAction, QSpinBox, QDoubleSpinBox, QCheckBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ─────────────────────────────────────────────────────────────────────────────
# Utility functions (identical to classical Smith‐chart routines)
# ─────────────────────────────────────────────────────────────────────────────

def gamma_from_normalized(z_norm):
    """
    Given a normalized impedance z_norm = (zL / z0), return Γ = (z_norm – 1)/(z_norm + 1).
    That way, a load with negative reactance (Im(z_norm)<0) → Im(Γ)<0 → lower half of chart.
    """
    # Use Python’s complex arithmetic directly; no NumPy arrays here.
    try:
        return (z_norm - 1) / (z_norm + 1)
    except ZeroDivisionError:
        return complex(np.inf, 0)


def swr_from_gamma(gamma):
    """
    SWR = (1 + |Γ|)/(1 – |Γ|).  If |Γ| ≥ 1 → SWR = ∞.
    """
    abs_gamma = abs(gamma)
    if abs_gamma >= 1:
        return np.inf
    return (1 + abs_gamma) / (1 - abs_gamma)


def angle_between(p1, p2):
    """
    Given two points p1=(x1,y1), p2=(x2,y2), return the angle (in degrees)
    of the line from p1→p2. Used to rotate reactance labels so they are tangent.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return np.degrees(np.arctan2(dy, dx))

from smith_chart_window import SmithChartWindow

def main():
    app = QApplication(sys.argv)
    win = SmithChartWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()