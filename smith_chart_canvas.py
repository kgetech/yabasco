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
from typing import Tuple
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from extra_utils import angle_between, gamma_from_normalized

# Data container for one impedance/admittance trace
TraceData = Tuple[np.ndarray, np.ndarray]

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


