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
from typing import Optional, Dict, List, Tuple
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QSize

# Data container for one impedance/admittance trace
TraceData = Tuple[np.ndarray, np.ndarray]

class SmithChartCanvas(FigureCanvasQTAgg):
    """A matplotlib-based Smith chart renderer."""
    def __init__(self,
                 *,
                 figsize: Tuple[float, float] = (5.0, 5.0),
                 dpi: int = 100):
        fig = Figure(figsize=figsize, dpi=dpi)
        super().__init__(fig)
        # Axes
        self.ax = fig.add_subplot(111, projection='polar')
        self.fig = fig

        # Static background cache
        self._background = None
        self._init_chart()

        # dynamic traces: panel_id -> artists
        self._traces: Dict[int, List] = {}

    def sizeHint(self) -> QSize:
        return QSize(500, 500)

    def _init_chart(self) -> None:
        """Draw grid + unit circle once, cache as background."""
        # configure axes
        self.ax.clear()
        self.ax.set_theta_zero_location('E')
        self.ax.set_theta_direction(-1)
        self._draw_static_elements()
        # cache background
        self._background = self.copy_from_bbox(self.fig.bbox)

    def _draw_static_elements(self) -> None:
        # draw grid, resistance & reactance circles, unit circle…
        # (extract your existing methods _draw_unit_circle, etc.)
        pass

    def update_impedance(self,
                         panel_id: int,
                         z: complex,
                         y: complex,
                         z0: Optional[complex] = None,
                         y0: Optional[complex] = None) -> None:
        """Add or update one trace on the chart."""
        # restore background
        self.restore_region(self._background)

        # compute Gamma curve for this impedance
        gamma = (z - z0) / (z + z0) if z0 else np.array([])
        theta = np.linspace(0, 2*np.pi, 400)
        r = np.abs(gamma)
        # (replace with your gamma_from_normalized)

        # if existing artists, remove them
        for art in self._traces.get(panel_id, []):
            art.remove()

        # plot new
        line, = self.ax.plot(theta, r, label=f"ID {panel_id}")
        self._traces[panel_id] = [line]

        # blit just the updated region
        self.blit(self.fig.bbox)

    def remove_impedance(self, panel_id: int) -> None:
        """Remove a trace completely."""
        for art in self._traces.pop(panel_id, []):
            art.remove()
        self.draw_idle()