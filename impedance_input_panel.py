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
import numpy as np
from extra_utils import gamma_from_normalized, swr_from_gamma
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QColorDialog,
    QLabel, QLineEdit, QPushButton, QScrollArea,

)

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
