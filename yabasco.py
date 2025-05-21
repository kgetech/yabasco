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
import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDockWidget, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QColorDialog, QSpinBox, QDoubleSpinBox,
                             QCheckBox, QAction, QFileDialog)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

def gamma_from_z(Z, Z0):
    with np.errstate(divide='ignore', invalid='ignore'):
        return (Z - Z0) / (Z + Z0)

def swr_from_gamma(gamma):
    abs_gamma = np.abs(gamma)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(abs_gamma >= 1, np.inf, (1 + abs_gamma) / (1 - abs_gamma))

def angle_between(p1, p2):
    delta = np.array(p2) - np.array(p1)
    return np.degrees(np.arctan2(delta[1], delta[0]))

class SmithChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        # Styling
        self.unit_circle_color = 'gray'
        self.resistance_color = 'lightgray'
        self.reactance_color = 'lightgray'
        self.gamma_circle_color = 'blue'
        self.radial_line_color = 'green'
        # R=1 circle
        self.show_r1 = False
        self.r1_color = 'magenta'
        # Grid settings
        self.num_r_lines = 10
        self.num_r_inner_lines = 10
        self.num_x_lines = 10
        self.label_resistance_every = 2
        self.label_reactance_every = 2
        self.x_label_at_r = 1.0
        # Initial impedances
        self.Z0 = 50 + 0j
        self.ZL = 100 + 50j
        self.Zin = 20 - 10j
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_path)

    def plot_chart(self, Z0, ZL, Zin):
        # Update and normalize
        self.Z0, self.ZL, self.Zin = Z0, ZL, Zin
        ZL_n = ZL / Z0
        Zin_n = Zin / Z0
        self.ax.clear()
        # Hide Cartesian frame
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        # Unit circle
        self.ax.add_patch(plt.Circle((0, 0), 1, fill=False, color=self.unit_circle_color, linestyle='--'))
        # Resistance constant circles + labels
        r_outer = np.linspace(1.1, 10, self.num_r_lines)
        r_inner = np.linspace(0.01, 1, self.num_r_inner_lines)
        for i, r in enumerate(np.concatenate((r_inner, r_outer))):
            z = r + 1j * np.linspace(-10, 10, 400)
            g = gamma_from_z(z, 1)
            self.ax.plot(g.real, g.imag, color=self.resistance_color, linewidth=0.8)
            if i % self.label_resistance_every == 0:
                idx = len(g) // 2
                self.ax.text(g.real[idx], g.imag[idx], f"{r:.2f}", fontsize=6,
                             color='black', rotation=90, rotation_mode='anchor')
        # Reactance constant circles + labels
        x_vals = np.linspace(0.1, 10, self.num_x_lines)
        for j, x in enumerate(x_vals):
            for sign in (1, -1):
                z = np.linspace(0.01, 10, 400) + 1j * sign * x
                g = gamma_from_z(z, 1)
                self.ax.plot(g.real, g.imag, color=self.reactance_color, linewidth=0.8)
                if j % self.label_reactance_every == 0:
                    zl = self.x_label_at_r + 1j * sign * x
                    gl = gamma_from_z(zl, 1)
                    # compute text angle
                    p1 = g[100]; p2 = g[102]
                    ang = angle_between((p1.real, p1.imag), (p2.real, p2.imag))
                    self.ax.text(gl.real, gl.imag, f"j{sign*x:.2f}", fontsize=6,
                                 color='black', rotation=ang, rotation_mode='anchor')
        # Reflection coefficients
        gL = gamma_from_z(ZL_n, 1)
        gIn = gamma_from_z(Zin_n, 1)
        mag_L = np.abs(gL)
        # Plot points and SWR circle
        self.ax.plot(gL.real, gL.imag, 'ro', label='Load')
        self.ax.plot(gIn.real, gIn.imag, 'bo', label='Input')
        self.ax.add_patch(plt.Circle((0, 0), mag_L, fill=False, color=self.gamma_circle_color))
        # R=1 line with intersections labeled
        if self.show_r1:
            x = np.linspace(-10, 10, 1000)
            pz = 1 + 1j * x
            g1 = gamma_from_z(pz, 1)
            self.ax.plot(g1.real, g1.imag, color=self.r1_color, label='R=1 Circle')
            diff = np.abs(np.abs(g1) - mag_L)
            mask = x >= 0
            idxs = [np.where(mask)[0][np.argmin(diff[mask])], np.where(~mask)[0][np.argmin(diff[~mask])]]
            for idx in idxs:
                p = g1[idx]
                phi = np.angle(p); phi_deg = np.degrees(phi)
                lam = (np.pi - phi) / (4 * np.pi)
                off = 0.05; d = p / np.abs(p)
                self.ax.plot([0, d.real], [0, d.imag], color=self.r1_color, linestyle=':')
                self.ax.plot(p.real, p.imag, 'x', color=self.r1_color)
                self.ax.text(p.real * (2.75 + off), p.imag * (2.75 + off),
                             f"{lam:.3f}λ, {phi_deg:.1f}°",
                             color=self.r1_color, ha='center', va='center', fontsize=8)
                self.ax.text(p.real * (2.5 + off), p.imag * (2.5 + off),
                             f"{p.real:.2f}+j{phi_deg:.2f}",
                             color=self.r1_color, ha='center', va='center', fontsize=8)
        # Load phase line endpoints
        if mag_L > 0:
            d = gL / mag_L
            self.ax.plot([d.real, -d.real], [d.imag, -d.imag],
                         color=self.radial_line_color, linestyle='--', label='Phase line')
            off = 0.05
            for sign, pt in [(1, d), (-1, -d)]:
                phi = np.angle(pt); phi_deg = np.degrees(phi)
                lam = (np.pi - phi) / (4 * np.pi) + (0.5 if sign == -1 else 0)
                self.ax.plot(pt.real, pt.imag, 'o', color=self.radial_line_color)
                self.ax.text(pt.real*(1.25+off), pt.imag*(1.25+off),
                             f"{lam:.3f}λ, {phi_deg:.1f}°",
                             color=self.radial_line_color, ha='center', va='center', fontsize=8)
        # Outer lambda/phase markers
        off = 0.05
        markers = [(-1, 0, np.pi, 0.0), (0, 1, np.pi/2, 0.125), (1, 0, 0, 0.25), (0, -1, -np.pi/2, 0.375)]
        for x, y, phi, lam in markers:
            phi_deg = int(np.degrees(phi))
            text = f"{lam:.3f}λ, {phi_deg}°"
            ha = 'right' if x < 0 else 'left' if x > 0 else 'center'
            va = 'bottom' if y > 0 else 'top' if y < 0 else 'center'
            self.ax.text(x*(1+off), y*(1+off), text, ha=ha, va=va, fontsize=8)
        # Black center dot and arrows
        self.ax.plot(0, 0, 'ko', label='Z_norm=1+0j')
        for x, y in [(0,1),(-1,0),(0,-1),(1,0)]:
            self.ax.annotate('', xy=(x,y), xytext=(0,0),
                             arrowprops=dict(arrowstyle='->', color='darkgray'))
        # Final legend and draw
        leg = self.ax.legend(loc='upper right', fontsize=8)
        leg.set_draggable(True)
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.set_aspect('equal')
        self.draw()

    def animate_path(self):
        pass

    def save_chart(self):
        path, _ = QFileDialog.getSaveFileName(None, "Save Chart", "smith_chart.png",
                                              "PNG Files (*.png);;SVG Files (*.svg)")
        if path:
            self.fig.savefig(path)
class ImpedancePanel(QWidget):
    def __init__(self, chart):
        super().__init__()
        self.chart = chart
        layout = QVBoxLayout()
        # Load impedance and admittance
        layout.addWidget(QLabel("Load Impedance ZL:"))
        self.zl_input = QLineEdit("100+50j")
        layout.addWidget(self.zl_input)
        layout.addWidget(QLabel("Load Admittance YL:"))
        self.yl_input = QLineEdit(self._format_complex(1/(100+50j)))
        layout.addWidget(self.yl_input)
        # Characteristic impedance and admittance
        layout.addWidget(QLabel("Characteristic Impedance Z0:"))
        self.z0_input = QLineEdit("50")
        layout.addWidget(self.z0_input)
        layout.addWidget(QLabel("Characteristic Admittance Y0:"))
        self.y0_input = QLineEdit(self._format_complex(1/50))
        layout.addWidget(self.y0_input)
        # Reflection labels
        self.gamma_label = QLabel("Γ = N/A")
        layout.addWidget(self.gamma_label)
        self.gamma_abs_label = QLabel("|Γ| = N/A")
        layout.addWidget(self.gamma_abs_label)
        self.swr_label = QLabel("SWR = N/A")
        layout.addWidget(self.swr_label)
        self.setLayout(layout)
        # Connect signals
        self.zl_input.textChanged.connect(self._on_zl_changed)
        self.yl_input.textChanged.connect(self._on_yl_changed)
        self.z0_input.textChanged.connect(self._on_z0_changed)
        self.y0_input.textChanged.connect(self._on_y0_changed)

    def _format_complex(self, c):
        return f"{c.real:.6g}{'+' if c.imag>=0 else '-'}{abs(c.imag):.6g}j"

    def _on_zl_changed(self, txt):
        try:
            ZL = complex(txt)
            YL = 1/ZL
            self.yl_input.blockSignals(True)
            self.yl_input.setText(self._format_complex(YL))
            self.yl_input.blockSignals(False)
            self._update_chart(ZL=ZL)
        except:
            pass

    def _on_yl_changed(self, txt):
        try:
            YL = complex(txt)
            ZL = 1/YL
            self.zl_input.blockSignals(True)
            self.zl_input.setText(self._format_complex(ZL))
            self.zl_input.blockSignals(False)
            self._update_chart(ZL=ZL)
        except:
            pass

    def _on_z0_changed(self, txt):
        try:
            Z0 = complex(txt)
            Y0 = 1/Z0
            self.y0_input.blockSignals(True)
            self.y0_input.setText(self._format_complex(Y0))
            self.y0_input.blockSignals(False)
            self._update_chart(Z0=Z0)
        except:
            pass

    def _on_y0_changed(self, txt):
        try:
            Y0 = complex(txt)
            Z0 = 1/Y0
            self.z0_input.blockSignals(True)
            self.z0_input.setText(self._format_complex(Z0))
            self.z0_input.blockSignals(False)
            self._update_chart(Z0=Z0)
        except:
            pass

    def _update_chart(self, Z0=None, ZL=None):
        try:
            Z0 = Z0 if Z0 is not None else complex(self.z0_input.text())
            ZL = ZL if ZL is not None else complex(self.zl_input.text())
            gamma = gamma_from_z(ZL, Z0)
            swr = swr_from_gamma(gamma)
            self.gamma_label.setText(f"Γ = {gamma:.3f}")
            self.gamma_abs_label.setText(f"|Γ| = {np.abs(gamma):.3f}")
            self.swr_label.setText(f"SWR = {swr:.2f}")
            self.chart.plot_chart(Z0, ZL, self.chart.Zin)
        except:
            self.gamma_label.setText("Γ = Error")
            self.gamma_abs_label.setText("|Γ| = Error")
            self.swr_label.setText("SWR = Error")

class SmithChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smith Chart GUI")
        self.chart = SmithChartCanvas(self)
        self.setCentralWidget(self.chart)
        self._create_menu()
        self._create_docks()
        self.chart.plot_chart(self.chart.Z0, self.chart.ZL, self.chart.Zin)

    def _create_menu(self):
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")
        animate_action = QAction("Animate Gamma Path", self)
        animate_action.triggered.connect(self.chart.animation_timer.start)
        view_menu.addAction(animate_action)
        export_action = QAction("Export Chart", self)
        export_action.triggered.connect(self.chart.save_chart)
        view_menu.addAction(export_action)

    def _create_docks(self):
        # Left dock
        dock_left = QDockWidget("Impedance & Admittance Input", self)
        dock_left.setWidget(ImpedancePanel(self.chart))
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_left)

        # Right dock
        dock_right = QDockWidget("Settings", self)
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        # Resistance lines >1
        layout.addWidget(QLabel("# Resistance Lines (R > 1):"))
        r1_spin = QSpinBox(); r1_spin.setRange(1,50); r1_spin.setValue(self.chart.num_r_lines)
        r1_spin.valueChanged.connect(lambda v:setattr(self.chart,'num_r_lines',v)); r1_spin.valueChanged.connect(lambda:self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin))
        layout.addWidget(r1_spin)
        # Resistance lines <1
        layout.addWidget(QLabel("# Resistance Lines (R < 1):"))
        r2_spin = QSpinBox(); r2_spin.setRange(1,50); r2_spin.setValue(self.chart.num_r_inner_lines)
        r2_spin.valueChanged.connect(lambda v:setattr(self.chart,'num_r_inner_lines',v)); r2_spin.valueChanged.connect(lambda:self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin))
        layout.addWidget(r2_spin)
        # Reactance lines
        layout.addWidget(QLabel("# Reactance Lines (±jX):"))
        x_spin = QSpinBox(); x_spin.setRange(1,50); x_spin.setValue(self.chart.num_x_lines)
        x_spin.valueChanged.connect(lambda v:setattr(self.chart,'num_x_lines',v)); x_spin.valueChanged.connect(lambda:self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin))
        layout.addWidget(x_spin)
        # Resistance label skip
        layout.addWidget(QLabel("Resistance Label Every N:"))
        rl_spin = QSpinBox(); rl_spin.setRange(1,10); rl_spin.setValue(self.chart.label_resistance_every)
        rl_spin.valueChanged.connect(lambda v:setattr(self.chart,'label_resistance_every',v)); rl_spin.valueChanged.connect(lambda:self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin))
        layout.addWidget(rl_spin)
        # Reactance label skip
        layout.addWidget(QLabel("Reactance Label Every N:"))
        xl_spin = QSpinBox(); xl_spin.setRange(1,10); xl_spin.setValue(self.chart.label_reactance_every)
        xl_spin.valueChanged.connect(lambda v:setattr(self.chart,'label_reactance_every',v)); xl_spin.valueChanged.connect(lambda:self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin))
        layout.addWidget(xl_spin)
        # Imaginary label location
        layout.addWidget(QLabel("Imaginary Label at r ="))
        il_spin = QDoubleSpinBox(); il_spin.setRange(0.01,10); il_spin.setSingleStep(0.1); il_spin.setValue(self.chart.x_label_at_r)
        il_spin.valueChanged.connect(lambda v:setattr(self.chart,'x_label_at_r',v)); il_spin.valueChanged.connect(lambda:self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin))
        layout.addWidget(il_spin)
        # Gamma color
        btn1 = QPushButton("Set Gamma Path Color"); btn1.clicked.connect(self._pick_gamma_color); layout.addWidget(btn1)
        # R=1 toggle and color
        chk = QCheckBox("Show R=1 Circle"); chk.stateChanged.connect(lambda s:setattr(self.chart,'show_r1',s==Qt.Checked)); chk.stateChanged.connect(lambda:self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin)); layout.addWidget(chk)
        btn2 = QPushButton("Set R=1 Color"); btn2.clicked.connect(self._pick_r1_color); layout.addWidget(btn2)
        dock_right.setWidget(settings_widget); self.addDockWidget(Qt.RightDockWidgetArea,dock_right)

    def _pick_gamma_color(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.chart.gamma_circle_color = c.name(); self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin)
    def _pick_r1_color(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.chart.r1_color = c.name(); self.chart.plot_chart(self.chart.Z0,self.chart.ZL,self.chart.Zin)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SmithChartWindow()
    window.resize(1000, 800)
    window.show()
    sys.exit(app.exec_())
