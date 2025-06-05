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


# ─────────────────────────────────────────────────────────────────────────────
# SmithChartCanvas: the central FigureCanvas that draws everything
# ─────────────────────────────────────────────────────────────────────────────

class SmithChartCanvas(FigureCanvas):
    """
    Qt widget that renders:
      • Resistance circles (R>1 and 0<R<1 separately),
      • Reactance arcs (±jX) “textbook style” (centers at (1, ±1/X)),
      • Labels for ±jX at an adjustable real radius “r = …”
      • Optional R=1 circle highlight + phase/λ tick marks,
      • Radial lines, unit circle, Γ-circle (|Γ|=1),
      • Multiple impedance markers (each color-coded).
    """

    # A cycle of colors for successive impedance traces:
    COLOR_CYCLE = [
        "#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
        "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999"
    ]

    def __init__(self, parent=None):
        # Create a Matplotlib Figure & Axes in dark‐mode background
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax  = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor('#121212')   # match Fusion dark theme
        super().__init__(self.fig)
        self.setParent(parent)

        # ─── Chart parameters (defaults) ───────────────────────────────────
        # Resistance circles:
        self.num_r_outer_lines = 7       # R = 1,2,…,7  (R > 1)
        self.num_r_inner_lines = 7       # 0 < R < 1 (evenly spaced 0.01→1)

        # Reactance arcs:
        self.num_x_lines = 9             # |X| = 0.1→9.0  (we’ll label every Nth)
        self.x_label_at_r = 1.0          # place “±jX” labels at Re(Z) = 1.0

        # Label skipping:
        self.label_resistance_every = 2  # label every 2nd R‐circle
        self.label_reactance_every = 2   # label every 2nd reactance arc

        # Toggles:
        self.show_radial = True
        self.show_unit   = True
        self.show_r1     = True

        # Colors:
        self.resistance_color   = "#323232"
        self.reactance_color    = "#323232"
        self.radial_line_color  = "#323232"
        self.unit_circle_color  = "#323232"
        self.gamma_circle_color = "#323232"
        self.r1_color           = "#e6550d"

        # Line‐width & styling
        self.grid_lw   = 0.5
        self.capstyle  = "round"
        self.joinstyle = "round"

        # Storage for multiple impedance traces:
        # panel_id → { 'zL':complex, 'z0':complex, 'color':"#rrggbb" }
        self.impedances = {}

        # Initial draw
        self._draw_chart()


    def _configure_axes(self):
        """Clear axes, set equal aspect & hide ticks/labels."""
        self.ax.clear()
        self.ax.set_aspect("equal", "box")
        self.ax.axis("off")
        self.ax.set_xlim(-1.05, 1.05)
        self.ax.set_ylim(-1.05, 1.05)


    def _draw_chart(self):
        """
        Redraw the entire Smith‐chart grid + labels + impedance markers.
        Called whenever a parameter or an impedance changes.
        """
        self._configure_axes()

        # 1) Draw all resistance circles:
        self._draw_resistance_circles()

        # 2) Highlight R=1 circle (if enabled)
        if self.show_r1:
            self._highlight_r1()

        # 3) Draw reactance arcs (±jX) and label them:
        self._draw_reactance_arcs_and_labels()

        # 5) Unit circle (|Γ|=1):
        if self.show_unit:
            self._draw_unit_circle()

        # 6) Resistance labels (on real axis) for R>1 and R<1:
        self._draw_resistance_labels()

        # 7) Plot any impedance‐points / traces the user has added:
        self._draw_impedances()

        # 8) Legend (if >1 trace)
        if self.impedances:
            handles, labels = self.ax.get_legend_handles_labels()
            leg = self.ax.legend(handles, labels, loc='upper right', fontsize=8)
            leg.set_draggable(True)

        # Finally, refresh the canvas
        self.fig.canvas.draw_idle()


    def _plot_inside(self, x, y, *, color=None, lw=None, ls='-'):
        """
        Helper: plot only those (x,y) points for which x^2 + y^2 ≤ 1.000001,
        broken into contiguous segments so that arcs outside |Γ|>1 are clipped away.
        """
        mask = (x*x + y*y) <= 1.000001
        if not mask.any():
            return
        idx = np.nonzero(mask)[0]
        breaks = np.where(np.diff(idx) != 1)[0]
        start = 0
        for b in breaks:
            seg = idx[start:b+1]
            self.ax.plot(
                x[seg], y[seg],
                color=color or self.grid_color(),
                lw=lw or self.grid_lw,
                ls=ls,
                solid_capstyle=self.capstyle,
                solid_joinstyle=self.joinstyle
            )
            start = b+1
        seg = idx[start:]
        self.ax.plot(
            x[seg], y[seg],
            color=color or self.grid_color(),
            lw=lw or self.grid_lw,
            ls=ls,
            solid_capstyle=self.capstyle,
            solid_joinstyle=self.joinstyle
        )


    def grid_color(self):
        """Return whichever grid color we’re currently using (resistance/reactance)."""
        return self.resistance_color


    def _draw_resistance_circles(self):
        """
        Draw constant-R circles:
          • Outer region (R > 1): R = 1,2,…,num_r_outer_lines
          • Inner region (0 < R < 1): R = linspace(0.01,1,num_r_inner_lines)
        Each circle is centered at (R/(R+1), 0), radius = 1/(R+1).
        """
        theta = np.linspace(0, 2*np.pi, 600)

        # 1a) Outer region: R = 1…num_r_outer_lines
        for R in range(1, self.num_r_outer_lines + 1):
            center = R / (R + 1)
            rad    = 1 / (R + 1)
            x = center + rad * np.cos(theta)
            y =           rad * np.sin(theta)
            self._plot_inside(x, y, color=self.resistance_color)

        # 1b) Inner region: 0 < R < 1
        if self.num_r_inner_lines > 0:
            r_inner = np.linspace(0.01, 1.0, self.num_r_inner_lines)
            for R in r_inner:
                center = R / (R + 1)
                rad    = 1 / (R + 1)
                x = center + rad * np.cos(theta)
                y =           rad * np.sin(theta)
                self._plot_inside(x, y, color=self.resistance_color)


    def _highlight_r1(self):
        """
        Draw the R=1 circle (center=(0.5,0), radius=0.5) in a special color.
        """
        theta = np.linspace(0, 2*np.pi, 600)
        center, rad = 0.5, 0.5
        x = center + rad * np.cos(theta)
        y =          rad * np.sin(theta)
        self._plot_inside(x, y, color=self.r1_color, lw=self.grid_lw + 0.2)


    def _draw_reactance_arcs_and_labels(self):
        """
        Draw constant‐reactance circles for +jX and –jX (X=0.1→num_x_lines).
        Each ±X circle is centered at (1, ±1/X) with radius=1/X.  We then
        clip it to |Γ|≤1.  If j%label_reactance_every==0, place “±jX” at the
        point where that circle intersects Re(Z)=x_label_at_r (normalized).
        """
        theta_full = np.linspace(0, 2*np.pi, 600)
        # X values: 0.1, 0.2, …, (num_x_lines*0.1).  (Spacing of 0.1 can be changed if desired.)
        # In the “classical” Smith‐chart, we often see ±j1, ±j2, ….  Here we simply let:
        x_vals = np.linspace(0.1, float(self.num_x_lines), self.num_x_lines)

        for j, X in enumerate(x_vals, start=1):
            rad = 1.0 / X

            # (a) Positive reactance circle (center = (1, +1/X)):
            cx_pos = 1.0
            cy_pos =  1.0 / X
            x_pos = cx_pos + rad * np.cos(theta_full)
            y_pos = cy_pos + rad * np.sin(theta_full)
            self._plot_inside(x_pos, y_pos, color=self.reactance_color)

            if j % self.label_reactance_every == 0:
                # Place “+jX” label at the point where that circle intersects Re(Z)=x_label_at_r:
                z_label = self.x_label_at_r + 1j * X
                # First normalize z_label to z0=1 → z_norm = z_label/1 = z_label.
                g_label = gamma_from_normalized(z_label)
                # Compute a tiny tangent‐angle for rotating the text:
                p1 = complex(x_pos[100], y_pos[100])
                p2 = complex(x_pos[102], y_pos[102])
                ang = angle_between((p1.real, p1.imag), (p2.real, p2.imag))
                self.ax.text(
                    g_label.real, g_label.imag,
                    f"+j{X:.2f}",
                    color=self.reactance_color,
                    fontsize=8,
                    rotation=ang,
                    rotation_mode='anchor',
                    ha='center', va='center'
                )

            # (b) Negative reactance circle (center = (1, –1/X)):
            cx_neg = 1.0
            cy_neg = -1.0 / X
            x_neg = cx_neg + rad * np.cos(theta_full)
            y_neg = cy_neg + rad * np.sin(theta_full)
            self._plot_inside(x_neg, y_neg, color=self.reactance_color)

            if j % self.label_reactance_every == 0:
                z_label = self.x_label_at_r - 1j * X
                g_label = gamma_from_normalized(z_label)
                p1n = complex(x_neg[100], y_neg[100])
                p2n = complex(x_neg[102], y_neg[102])
                ang_n = angle_between((p1n.real, p1n.imag), (p2n.real, p2n.imag))
                self.ax.text(
                    g_label.real, g_label.imag,
                    f"-j{X:.2f}",
                    color=self.reactance_color,
                    fontsize=8,
                    rotation=ang_n,
                    rotation_mode='anchor',
                    ha='center', va='center'
                )


    def _draw_radial_lines(self):
        """Draw dashed radial lines from the origin at equally spaced angles."""
        angles = np.linspace(0, 2*np.pi, self.num_x_lines, endpoint=False)
        for ang in angles:
            x = [0.0, np.cos(ang)]
            y = [0.0, np.sin(ang)]
            self.ax.plot(
                x, y,
                color=self.radial_line_color,
                lw=self.grid_lw, ls="--",
                solid_capstyle=self.capstyle
            )


    def _draw_unit_circle(self):
        """Draw the unit circle (|Γ|=1) as a thin dashed ring."""
        theta = np.linspace(0, 2*np.pi, 500)
        x = np.cos(theta)
        y = np.sin(theta)
        self.ax.plot(
            x, y,
            color=self.unit_circle_color,
            lw=self.grid_lw + 0.2,
            ls="--",
            solid_capstyle=self.capstyle
        )


    def _draw_resistance_labels(self):
        """
        Place numeric labels on the real axis for each R‐circle we’ve drawn.
        • For R>1: R=1,2,3,… at x = (R–1)/(R+1).
        • For 0<R<1: R=0.01→1.00 (as many as num_r_inner_lines) at x=(R–1)/(R+1).
        We skip according to label_resistance_every.
        """
        # Outer region: R=1…num_r_outer_lines
        for R in range(1, self.num_r_outer_lines + 1):
            if R % self.label_resistance_every != 0:
                continue
            # The left intersection with the real axis is x = (R/(R+1) – 1/(R+1)) = (R–1)/(R+1).
            x_label = (R - 1.0) / (R + 1.0)
            self.ax.text(
                x_label, -0.03,
                f"{R}",
                ha="center", va="top",
                fontsize=8,
                color=self.resistance_color
            )

        # Inner region: 0 < R < 1
        if self.num_r_inner_lines > 0:
            r_inner = np.linspace(0.01, 1.0, self.num_r_inner_lines)
            for idx, R in enumerate(r_inner, start=1):
                if idx % self.label_resistance_every != 0:
                    continue
                x_label = (R - 1.0) / (R + 1.0)
                self.ax.text(
                    x_label, -0.03,
                    f"{R:.2f}",
                    ha="center", va="top",
                    fontsize=8,
                    color=self.resistance_color
                )

    def _draw_impedances(self):
        """
        Plot each impedance in self.impedances:
          1) Normalize zL to z0 → z_norm = zL / z0
          2) Γ = (z_norm – 1)/(z_norm + 1)
          3) Dot at (Re{Γ}, Im{Γ})  (so negative‐Im falls in lower half)
          4) Dashed radial line from origin → that dot
          5) Annotate |Γ| and ∠Γ° next to the dot
          6) If show_swr is True, draw the SWR circle (|Γ| constant) in the impedance color
        """
        for pid, data in self.impedances.items():
            zL = data['zL']
            z0 = data['z0']
            color = data['color']

            try:
                z_norm = zL / z0
                gamma = gamma_from_normalized(z_norm)
                g_re = float(np.real(gamma))
                g_im = float(np.imag(gamma))

                # 3) Plot the marker
                self.ax.plot(g_re, g_im, 'o', color=color, label=f"Z{pid}")

                # 4) Radial dashed line from (0,0) → (g_re, g_im)
                self.ax.plot([0.0, g_re], [0.0, g_im], color=color, lw=0.8, ls=':')

                # 5) Annotate magnitude & angle
                mag = abs(gamma)
                ang = np.degrees(np.angle(gamma))
                text = f"|Γ|={mag:.2f}\n{ang:.1f}°"
                self.ax.text(g_re * 1.1, g_im * 1.1, text,
                             color=color, ha='center', va='center', fontsize=7)

                # 6) Draw SWR circle if toggled on for this pid
                if data.get('show_swr', False):
                    swr_radius = mag
                    theta = np.linspace(0, 2 * np.pi, 300)
                    x_circle = swr_radius * np.cos(theta)
                    y_circle = swr_radius * np.sin(theta)
                    self.ax.plot(
                        x_circle, y_circle,
                        color=color, ls='--', lw=0.8
                    )

            except Exception:
                # In case z0 == –zL or other exceptional cases, skip plotting
                continue

    def update_impedance(self, pid, zL=None, z0=None, color=None):
        """
        Called whenever a single ImpedancePanel changes. We store the new zL,z0,color
        (and now a show_swr flag) into self.impedances[pid] and then redraw the chart.
        """
        if pid not in self.impedances:
            default_color = self.COLOR_CYCLE[len(self.impedances) % len(self.COLOR_CYCLE)]
            self.impedances[pid] = {
                'zL': zL or (50 + 0j),
                'z0': z0 or (50 + 0j),
                'color': default_color,
                'show_swr': False
            }

        if zL is not None:
            self.impedances[pid]['zL'] = zL
        if z0 is not None:
            self.impedances[pid]['z0'] = z0
        if color is not None:
            self.impedances[pid]['color'] = color

        self._draw_chart()

    def tog_swrc(self, pid):
        """
        Toggle whether the SWR circle for impedance `pid` is drawn.
        """
        if pid in self.impedances:
            current = self.impedances[pid].get('show_swr', False)
            self.impedances[pid]['show_swr'] = not current
            self._draw_chart()

    def remove_impedance(self, pid):
        """Remove a given panel’s trace from self.impedances and redraw."""
        if pid in self.impedances:
            del self.impedances[pid]
            self._draw_chart()


    def update_grid(self,
                    num_r_outer=None, num_r_inner=None, num_x=None,
                    label_r_every=None, label_x_every=None,
                    x_label_at_r=None, show_radial=None,
                    show_unit=None, show_r1=None,
                    grid_color=None, r1_color=None, γ_color=None):
        """
        Called by the “Settings” panel on the right.  Any parameter that’s not None
        will be updated; then we trigger a full redraw of the chart.
        """
        if num_r_outer is not None:
            self.num_r_outer_lines = num_r_outer
        if num_r_inner is not None:
            self.num_r_inner_lines = num_r_inner
        if num_x is not None:
            self.num_x_lines = num_x
        if label_r_every is not None:
            self.label_resistance_every = label_r_every
        if label_x_every is not None:
            self.label_reactance_every = label_x_every
        if x_label_at_r is not None:
            self.x_label_at_r = x_label_at_r
        if show_unit is not None:
            self.show_unit = show_unit
        if show_r1 is not None:
            self.show_r1 = show_r1
        if grid_color is not None:
            # Apply to resistance/reactance/radial/unit/Γ circles all at once
            self.resistance_color   = grid_color
            self.reactance_color    = grid_color
            self.unit_circle_color  = grid_color
            self.gamma_circle_color = grid_color
        if r1_color is not None:
            self.r1_color = r1_color
        if γ_color is not None:
            self.gamma_circle_color = γ_color

        self._draw_chart()


    def save_chart(self, path):
        """Save the current figure to a file (PNG, SVG, etc.)."""
        self.fig.savefig(path, dpi=300)



# ─────────────────────────────────────────────────────────────────────────────
# ImpedancePanel: a single Z₀,Y₀ → ZL,YL panel (left dock)
# ─────────────────────────────────────────────────────────────────────────────

class ImpedancePanel(QWidget):
    """
    One “Load Impedance” panel on the left.  Contains:
      • Two QLineEdits for Z₀ (“50+0j” default) and Y₀ (“0+0j” default)
      • Two QLineEdits for ZL (“50+0j” default) and YL (“0+0j” default)
      • “Color” button, “Remove” button
      • Two QLabel’s to show Γ and SWR in real time
    Whenever any field changes, we recompute:
      1) If YL≠0 → ZL = 1/YL
      2) If Y₀≠0 → Z₀ = 1/Y₀
      3) Compute z_norm = zL / z0
      4) Γ = (z_norm – 1)/(z_norm + 1), SWR = (1+|Γ|)/(1–|Γ|)
      5) Update chart via chart.update_impedance(self.panel_id, zL, z0)
    """
    def __init__(self, panel_id, chart, remove_cb):
        super().__init__()
        self.panel_id  = panel_id
        self.chart     = chart
        self.remove_cb = remove_cb

        main_lay = QVBoxLayout(self)

        # ZL and YL row
        zl_lay = QHBoxLayout()
        zl_lay.addWidget(QLabel("ZL:"))
        self.zl_input = QLineEdit("50+0j")
        zl_lay.addWidget(self.zl_input)
        zl_lay.addWidget(QLabel("  YL:"))
        self.yl_input = QLineEdit("0+0j")
        zl_lay.addWidget(self.yl_input)
        main_lay.addLayout(zl_lay)

        # Z₀ and Y₀ row
        z0_lay = QHBoxLayout()
        z0_lay.addWidget(QLabel("Z₀:"))
        self.z0_input = QLineEdit("50+0j")
        z0_lay.addWidget(self.z0_input)
        z0_lay.addWidget(QLabel("  Y₀:"))
        self.y0_input = QLineEdit("0+0j")
        z0_lay.addWidget(self.y0_input)
        main_lay.addLayout(z0_lay)

        # Color & Remove buttons
        btn_lay = QHBoxLayout()
        self.color_btn  = QPushButton("Color")
        self.tog_swrc_btn = QPushButton("Toggle SWR Circle")
        self.remove_btn = QPushButton("Remove")
        btn_lay.addWidget(self.color_btn)
        btn_lay.addWidget(self.tog_swrc_btn)
        btn_lay.addWidget(self.remove_btn)
        main_lay.addLayout(btn_lay)

        # Γ and SWR display
        self.gamma_label = QLabel("Γ = 0.00 ∠ 0.0°")
        self.swr_label   = QLabel("SWR = 1.00")
        main_lay.addWidget(self.gamma_label)
        main_lay.addWidget(self.swr_label)

        # Connect signals
        for widget in (self.z0_input, self.y0_input, self.zl_input, self.yl_input):
            widget.textEdited.connect(self._on_change)
            widget.editingFinished.connect(lambda w=widget: self._on_edit_finished(w))
        self.color_btn.clicked.connect(self._on_pick_color)
        self.remove_btn.clicked.connect(self._on_remove)
        self.tog_swrc_btn.clicked.connect(self._tog_swrc)

        # Initial calculation
        self._on_change()


    def _format_complex(self, c: complex, precision=6):
        """Format a Python complex as “a±jb” with given precision."""
        r = round(c.real, precision)
        i = round(c.imag, precision)
        sign = '+' if i >= 0 else '-'
        return f"{r}{sign}{abs(i)}j"


    def _on_change(self):
        """
        Called on each user edit to update the chart.
        Do *not* re‐set widget text here!
        """
        # parse all four inputs
        try:
            zL = complex(self.zl_input.text().replace('i', 'j'))
            yl = complex(self.yl_input.text().replace('i', 'j'))
            z0 = complex(self.z0_input.text().replace('i', 'j'))
            y0 = complex(self.y0_input.text().replace('i', 'j'))
        except ValueError:
            return


        # Compute Γ & SWR, but first normalize:
        if z0 == 0:
            return  # avoid division by zero
        z_norm = zL / z0
        gamma = gamma_from_normalized(z_norm)
        mag   = abs(gamma)
        swr   = swr_from_gamma(gamma)
        phase = np.degrees(np.angle(gamma))

        self.gamma_label.setText(f"Γ = {mag:.2f} ∠ {phase:.1f}°")
        self.swr_label.setText(f"SWR = {swr:.2f}")

        # Tell the chart to keep/update this “panel_id” with the new zL,z0
        self.chart.update_impedance(self.panel_id, zL=zL, z0=z0)


    def _on_remove(self):
        """User clicked Remove → notify manager and remove this trace."""
        self.chart.remove_impedance(self.panel_id)
        self.remove_cb(self.panel_id)

    def _tog_swrc(self):
        """Enable the display of the SWR circle for this impedance."""
        self.chart.tog_swrc(self.panel_id)

    def _on_pick_color(self):
        """Open a QColorDialog → update both button background & trace color."""
        col = QColorDialog.getColor()
        if not col.isValid():
            return
        hexcol = col.name()
        self.color_btn.setStyleSheet(f"background: {hexcol}")
        self.chart.update_impedance(self.panel_id, color=hexcol)

    def _on_edit_finished(self, widget: QLineEdit):
        """
        Once the user leaves the field, re‐format it and fire a final update.
        """
        text = widget.text().strip()
        try:
            val = complex(text.replace('i', 'j'))
        except ValueError:
            return
        nice = self._format_complex(val)
        # block signals so we don’t immediately recurse
        widget.blockSignals(True)
        widget.setText(nice)
        widget.blockSignals(False)
        # push one last chart update with the formatted value
        self._on_change()


# ─────────────────────────────────────────────────────────────────────────────
# ImpedancePanelManager: left-hand dock for “Add/Remove Impedance” panels
# ─────────────────────────────────────────────────────────────────────────────

class ImpedancePanelManager(QWidget):
    """
    A scrollable container.  “Add Impedance” → new ImpedancePanel with incremental panel_id.
    Each panel notifies this manager when it is removed.
    """
    def __init__(self, chart):
        super().__init__()
        self.chart = chart
        self.panels = {}
        self.next_id = 0

        v = QVBoxLayout()
        self.add_btn = QPushButton("Add Impedance")
        v.addWidget(self.add_btn)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        container = QWidget()
        self.container_layout = QVBoxLayout()
        container.setLayout(self.container_layout)
        self.scroll.setWidget(container)
        v.addWidget(self.scroll)

        self.setLayout(v)
        self.add_btn.clicked.connect(self.add_panel)


    def add_panel(self):
        pid = self.next_id
        p = ImpedancePanel(pid, self.chart, self.remove_panel)
        self.panels[pid] = p
        self.container_layout.addWidget(p)
        self.next_id += 1


    def remove_panel(self, pid):
        p = self.panels.pop(pid, None)
        if p:
            p.setParent(None)
            self.chart.remove_impedance(pid)



# ─────────────────────────────────────────────────────────────────────────────
# GridSettingsPanel: right-hand dock for all chart/grid parameters
# ─────────────────────────────────────────────────────────────────────────────

class GridSettingsPanel(QWidget):
    """
    Right-dock UI exactly matching yabasco_3.py’s fields plus our reactance labeling.
    Whenever a widget changes, we call chart.update_grid(…).
    """
    def __init__(self, chart):
        super().__init__()
        self.chart = chart

        layout = QGridLayout(self)
        layout.setContentsMargins(8,8,8,8)
        layout.setVerticalSpacing(6)

        # 1) # Resistance Lines (R > 1)
        layout.addWidget(QLabel("# Resistance Lines (R > 1):"), 0, 0)
        self.r1_spin = QSpinBox()
        self.r1_spin.setRange(1, 50)
        self.r1_spin.setValue(chart.num_r_outer_lines)
        self.r1_spin.valueChanged.connect(
            lambda v: chart.update_grid(num_r_outer=v)
        )
        layout.addWidget(self.r1_spin, 0, 1)

        # 2) # Resistance Lines (R < 1)
        layout.addWidget(QLabel("# Resistance Lines (R < 1):"), 1, 0)
        self.r2_spin = QSpinBox()
        self.r2_spin.setRange(1, 50)
        self.r2_spin.setValue(chart.num_r_inner_lines)
        self.r2_spin.valueChanged.connect(
            lambda v: chart.update_grid(num_r_inner=v)
        )
        layout.addWidget(self.r2_spin, 1, 1)

        # 3) # Reactance Lines (±jX)
        layout.addWidget(QLabel("# Reactance Lines (±jX):"), 2, 0)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(1, 50)
        self.x_spin.setValue(chart.num_x_lines)
        self.x_spin.valueChanged.connect(
            lambda v: chart.update_grid(num_x=v)
        )
        layout.addWidget(self.x_spin, 2, 1)

        # 4) Resistance Label Every N
        layout.addWidget(QLabel("Resistance Label Every N:"), 3, 0)
        self.rl_spin = QSpinBox()
        self.rl_spin.setRange(1, 10)
        self.rl_spin.setValue(chart.label_resistance_every)
        self.rl_spin.valueChanged.connect(
            lambda v: chart.update_grid(label_r_every=v)
        )
        layout.addWidget(self.rl_spin, 3, 1)

        # 5) Reactance Label Every N
        layout.addWidget(QLabel("Reactance Label Every N:"), 4, 0)
        self.xl_spin = QSpinBox()
        self.xl_spin.setRange(1, 10)
        self.xl_spin.setValue(chart.label_reactance_every)
        self.xl_spin.valueChanged.connect(
            lambda v: chart.update_grid(label_x_every=v)
        )
        layout.addWidget(self.xl_spin, 4, 1)

        # 6) Imaginary Label at r = ___
        layout.addWidget(QLabel("Imaginary Label at r ="), 5, 0)
        self.il_spin = QDoubleSpinBox()
        self.il_spin.setRange(0.01, 10.0)
        self.il_spin.setSingleStep(0.1)
        self.il_spin.setValue(chart.x_label_at_r)
        self.il_spin.valueChanged.connect(
            lambda v: chart.update_grid(x_label_at_r=v)
        )
        layout.addWidget(self.il_spin, 5, 1)

        # 7) Set Γ Path Color
        self.gamma_color_btn = QPushButton("Set Γ Path Color")
        self.gamma_color_btn.clicked.connect(self._pick_gamma_color)
        layout.addWidget(self.gamma_color_btn, 6, 0, 1, 2)

        # 8) Show R = 1 Circle
        self.r1_chk = QCheckBox("Show R=1 Circle")
        self.r1_chk.setChecked(chart.show_r1)
        self.r1_chk.stateChanged.connect(
            lambda s: chart.update_grid(show_r1=(s == Qt.Checked))
        )
        layout.addWidget(self.r1_chk, 7, 0, 1, 2)

        # 9) Set R = 1 Color
        self.r1_color_btn = QPushButton("Set R=1 Color")
        self.r1_color_btn.clicked.connect(self._pick_r1_color)
        layout.addWidget(self.r1_color_btn, 8, 0, 1, 2)

        # 10) Show Radial Lines
        self.rad_chk = QCheckBox("Show Radial Lines")
        self.rad_chk.setChecked(chart.show_radial)
        self.rad_chk.stateChanged.connect(
            lambda s: chart.update_grid(show_radial=(s == Qt.Checked))
        )
        layout.addWidget(self.rad_chk, 9, 0, 1, 2)

        # 11) Show Unit Circle
        self.unit_chk = QCheckBox("Show Unit Circle")
        self.unit_chk.setChecked(chart.show_unit)
        self.unit_chk.stateChanged.connect(
            lambda s: chart.update_grid(show_unit=(s == Qt.Checked))
        )
        layout.addWidget(self.unit_chk, 10, 0, 1, 2)

        # 12) Select Grid Color (applies to R/X/Radial/Unit/Γ)
        self.grid_color_btn = QPushButton("Select Grid Color")
        self.grid_color_btn.clicked.connect(self._pick_grid_color)
        layout.addWidget(self.grid_color_btn, 11, 0, 1, 2)

        # Dark background for this panel to match the rest of the app
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#2b2b2b"))
        self.setAutoFillBackground(True)
        self.setPalette(pal)


    def _pick_gamma_color(self):
        """ColorDialog → set chart.gamma_circle_color."""
        c = QColorDialog.getColor(initial=QColor(self.chart.gamma_circle_color),
                                  parent=self,
                                  title="Pick Γ Circle Color")
        if c.isValid():
            self.chart.update_grid(γ_color=c.name())


    def _pick_r1_color(self):
        """ColorDialog → set chart.r1_color."""
        c = QColorDialog.getColor(initial=QColor(self.chart.r1_color),
                                  parent=self,
                                  title="Pick R=1 Circle Color")
        if c.isValid():
            self.chart.update_grid(r1_color=c.name())


    def _pick_grid_color(self):
        """
        ColorDialog → apply this color to:
          resistance_color, reactance_color, radial_line_color,
          unit_circle_color, gamma_circle_color all at once.
        """
        c = QColorDialog.getColor(initial=QColor(self.chart.resistance_color),
                                  parent=self,
                                  title="Pick Grid Color")
        if c.isValid():
            self.chart.update_grid(grid_color=c.name())



# ─────────────────────────────────────────────────────────────────────────────
# Main Application Window
# ─────────────────────────────────────────────────────────────────────────────

class SmithChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YaBaSco New – Smith Chart Explorer")
        self.resize(1100, 800)

        # 1) Central SmithChartCanvas
        self.chart = SmithChartCanvas(self)
        self.setCentralWidget(self.chart)

        # 2) Right dock: GridSettingsPanel
        grid_dock = QDockWidget("Settings", self)
        self.grid_settings = GridSettingsPanel(self.chart)
        grid_dock.setWidget(self.grid_settings)
        grid_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, grid_dock)

        # 3) Left dock: ImpedancePanelManager
        dock_left = QDockWidget("Load Impedances", self)
        self.panel_mgr = ImpedancePanelManager(self.chart)
        dock_left.setWidget(self.panel_mgr)
        dock_left.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_left)

        # 4) Menu bar → File → Save Chart / Exit
        self._create_menu()


    def _create_menu(self):
        mb = self.menuBar()
        file_menu = mb.addMenu("&File")
        save_action = QAction("&Save Chart...", self)
        save_action.triggered.connect(self._save_chart)
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)


    def _save_chart(self):
        from PyQt5.QtWidgets import QFileDialog
        fn, _ = QFileDialog.getSaveFileName(
            self,
            "Save Chart",
            "",
            "PNG (*.png);;SVG (*.svg)"
        )
        if fn:
            self.chart.save_chart(fn)



def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Apply a “Fusion” dark palette to match JetBrains‐quality UX
    dark = QPalette()
    dark.setColor(QPalette.Window,             QColor(53, 53, 53))
    dark.setColor(QPalette.WindowText,         Qt.white)
    dark.setColor(QPalette.Base,               QColor(25, 25, 25))
    dark.setColor(QPalette.AlternateBase,      QColor(53, 53, 53))
    dark.setColor(QPalette.ToolTipBase,        Qt.white)
    dark.setColor(QPalette.ToolTipText,        Qt.white)
    dark.setColor(QPalette.Text,               Qt.white)
    dark.setColor(QPalette.Button,             QColor(53, 53, 53))
    dark.setColor(QPalette.ButtonText,         Qt.white)
    dark.setColor(QPalette.BrightText,         Qt.red)
    dark.setColor(QPalette.Link,               QColor(42, 130, 218))
    dark.setColor(QPalette.Highlight,          QColor(42, 130, 218))
    dark.setColor(QPalette.HighlightedText,    Qt.black)
    app.setPalette(dark)

    window = SmithChartWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
