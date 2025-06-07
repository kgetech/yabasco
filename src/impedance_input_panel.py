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
###########################################################################################

import numpy as np
from typing import Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QGridLayout,
    QLabel,
    QLineEdit,
    QColorDialog,
    QHBoxLayout,
    QCheckBox
)

from .smith_chart_canvas import ImpedanceConfig
from .extra_utils import gamma_from_normalized, swr_from_gamma


class ImpedancePanel(QWidget):
    """
    Left‐side panel UI for a single impedance trace.
    Each panel consists of:
      - Z0 (characteristic impedance)
      - Y0 (characteristic admittance, optional)
      - ZL (load impedance)
      - YL (load admittance, optional)
      - color-pick button
      - SWR toggle / SWR circle
      - “to G” / “to L” toggle for wavelength probes
      - Remove button

    Whenever any field is edited, the “_on_change” method fires and pushes
    a new ImpedanceConfig to smith_chart_canvas.update_impedance(…).
    """

    def __init__(
        self,
        panel_id: int,
        chart,
        update_cb,
        remove_cb,
        update_opts_cb,  # NOT used for data, but available if needed
    ):
        super().__init__()
        self.panel_id = panel_id
        self.chart = chart
        self.update_cb = update_cb
        self.remove_cb = remove_cb
        self.update_opts_cb = update_opts_cb

        # ─── Build all widgets ──────────────────────────────────────────────────────────
        layout = QGridLayout()
        layout.setSpacing(4)
        row = 0

        # ZL input (default: “0+0j”)
        layout.addWidget(QLabel("ZL:"), row, 0, 1, 1, Qt.AlignRight)
        self.zl_input = QLineEdit("0+0j")
        self.zl_input.textChanged.connect(lambda: self._on_change())
        layout.addWidget(self.zl_input, row, 1, 1, 2)
        row += 1

        # YL input (optional). If non-zero admittance typed, we compute ZL = 1 / YL
        layout.addWidget(QLabel("YL (opt):"), row, 0, 1, 1, Qt.AlignRight)
        self.yl_input = QLineEdit()
        self.yl_input.setPlaceholderText("e.g. 0.005+0.003j")
        self.yl_input.textChanged.connect(lambda: self._on_change())
        layout.addWidget(self.yl_input, row, 1, 1, 2)
        row += 1

        # Z₀ input (default: “50+0j”)
        layout.addWidget(QLabel("Z₀:"), row, 0, 1, 1, Qt.AlignRight)
        self.z0_input = QLineEdit("50+0j")
        self.z0_input.textChanged.connect(lambda: self._on_change())
        layout.addWidget(self.z0_input, row, 1, 1, 2)
        row += 1

        # Y₀ input (optional). If non-zero admittance typed, we compute Z₀ = 1 / Y₀
        layout.addWidget(QLabel("Y₀ (opt):"), row, 0, 1, 1, Qt.AlignRight)
        self.y0_input = QLineEdit()
        self.y0_input.setPlaceholderText("e.g. 0.02-0.004j")
        self.y0_input.textChanged.connect(lambda: self._on_change())
        layout.addWidget(self.y0_input, row, 1, 1, 2)
        row += 1

        # SWR and Γ labels (read‐only), displayed at the bottom of the panel
        self.gamma_label = QLabel("Γ = 0.00 ∠ 0.0°")
        self.swr_label = QLabel("SWR = 1.00")
        layout.addWidget(self.gamma_label, row, 0, 1, 2)
        layout.addWidget(self.swr_label, row, 2, 1, 1)
        row += 1

        # Color pick (default: device will assign a color automatically if not set)
        self.color_btn = QPushButton("Color")
        # Show the default color assigned by the canvas if the user never clicked
        default_color = self.chart._trace_color(panel_id)
        self.color_btn.setStyleSheet(f"background-color: {default_color};")
        self.color_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.color_btn, row, 0, 1, 3)
        row += 1

        # SWR toggle—draw the SWR circle around this impedance
        self.tog_swrc_btn = QCheckBox("Show SWR Circle")
        self.tog_swrc_btn.setChecked(False)
        self.tog_swrc_btn.stateChanged.connect(self._on_change)
        layout.addWidget(self.tog_swrc_btn, row, 0, 1, 2)
        row += 1

        # Show “admittance intersection” (draw where the Y circle intersects the chart)
        self.chk_adm = QCheckBox("Show Admittance")
        self.chk_adm.stateChanged.connect(self._on_change)
        layout.addWidget(self.chk_adm, row, 0, 1, 2)
        row += 1

        # Show “SWR and R=1 Intersections”
        self.chk_swr_r1 = QCheckBox("Show SWR and R=1 Intersections")
        self.chk_swr_r1.stateChanged.connect(self._on_change)
        layout.addWidget(self.chk_swr_r1, row, 0, 1, 2)
        row += 1

        # To G (λ→0) / To L (λ→ℓ) probes
        hbox = QHBoxLayout()
        self.chk_to_gen = QCheckBox("λ→Generator")
        hbox.addWidget(self.chk_to_gen)
        self.chk_to_gen.stateChanged.connect(lambda: self._on_change())
        # NEW: Γ-angle label toggle
        self.chk_gamma_angle = QCheckBox("Show Γ angle")
        hbox.addWidget(self.chk_gamma_angle)
        self.chk_gamma_angle.stateChanged.connect(self._on_change)
        layout.addLayout(hbox, row, 0, 1, 2)
        row +=1

        # Remove panel button
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(lambda: self.remove_cb(self.panel_id))
        layout.addWidget(self.remove_btn, row, 0, 1, 3)
        row += 1

        # Stretch to push everything up
        layout.setRowStretch(row, 1)
        self.setLayout(layout)

        # ─── Initial calculation/push to chart ─────────────────────────────────────────
        self._on_change()


    def _pick_color(self):
        """Open a QColorDialog; once chosen, fire _on_change so the chart redraws."""
        c = QColorDialog.getColor()
        if c.isValid():
            self.color_btn.setStyleSheet(f"background-color: {c.name()};")
            self._on_change()


    def _on_change(self):
        """
        Called whenever Z₀, Y₀, ZL or YL edit.  Parses each field,
        applies reciprocal logic, computes Γ & SWR, then dispatches
        everything to the canvas via chart.update_impedance(...).
        """
        # little helper to turn widget.text() → complex or None
        def _parse(w):
            s = w.text().strip().lower().replace('i', 'j')
            try:
                return complex(s)
            except ValueError:
                return None

        # 1) Parse the four fields
        raw_z0 = _parse(self.z0_input)
        raw_y0 = _parse(self.y0_input)
        raw_zL = _parse(self.zl_input)
        raw_yL = _parse(self.yl_input)

        # 2) Determine Z₀:
        #    - If user typed a non-zero Y₀ → invert it.
        #    - Otherwise, if they typed a valid Z₀ string, use that.
        #    - Otherwise fallback to 50+0j.
        if raw_y0 is not None and raw_y0 != 0 + 0j:
            try:
                z0 = 1 / raw_y0
            except ZeroDivisionError:
                z0 = complex(float("inf"), 0)
        elif raw_z0 is not None:
            z0 = raw_z0
        else:
            z0 = 50 + 0j

        # 3) Determine ZL and yL:
        #    - If user typed a non-zero Yₗ → invert it.
        #    - Otherwise, if they typed a valid Zₗ string, use that.
        #    - Otherwise fallback to 0+0j.
        if raw_yL is not None and raw_yL != 0 + 0j:
            try:
                zL = 1 / raw_yL
            except ZeroDivisionError:
                zL = complex(float("inf"), 0)
            yL = raw_yL
        elif raw_zL is not None:
            zL = raw_zL
            yL = raw_yL  # may be 0 or None, but we don’t invert
        else:
            zL = 0 + 0j
            yL = raw_yL

        # 4) Compute reflection coefficient, SWR, phase, etc.
        z_norm = zL / z0
        gamma = gamma_from_normalized(z_norm)
        mag = abs(gamma)
        phase = np.degrees(np.angle(gamma))
        # Guard against NaN angle
        if np.isnan(phase):
            phase = 0.0
        swr = swr_from_gamma(gamma)

        # 5) Update the on-panel labels
        self.gamma_label.setText(f"Γ = {mag:.2f} ∠ {phase:.1f}°")
        self.swr_label.setText(f"SWR = {swr:.2f}")

        # 6) Build a kwargs dict for update_impedance (not update_impedance_options)
        cfg_kwargs = {
            "zL": zL,
            "yL": yL,
            "z0": z0,
            "y0": raw_y0,
            "color": self.color_btn.palette().button().color().name(),
            "to_gen": self.chk_to_gen.isChecked(),
            "swr": swr,
            "ref_coeff": gamma,
            "ref_coeff_mag": mag,
            "ref_coeff_degrees": int(phase),
            "tau": np.angle(z_norm),
            "show_swr": self.tog_swrc_btn.isChecked(),
            # CORRECTION: use self.chk_adm (not chk_tau) for "Show admittance intersection"
            "show_swr_r1_intersection": self.chk_swr_r1.isChecked(),
            "show_adm_intersection": self.chk_adm.isChecked(),
        }

        # 7) Dispatch to chart.update_impedance(...) (not update_opts_cb)
        self.update_cb(self.panel_id, **cfg_kwargs)

        self.update_opts_cb(
            self.panel_id,
            show_wav_to_gen=self.chk_to_gen.isChecked(),
            show_gamma_angle=self.chk_gamma_angle.isChecked(),
        )

    def on_toggle(self):
        """
        Called when the user toggles “Show SWR” or the λ→0/λ→ℓ checkboxes. These
        toggles do _not_ change zL or z0; they simply flip boolean flags in the
        existing ImpedanceConfig. So we call update_cb with only those two keys.
        """
        # Flip the “show SWR circle” checkbox
        ss = self.tog_swrc_btn.isChecked()
        # flip the “to‐generator” / “to‐load” checkboxes through panel_id
        self.update_cb(self.panel_id, show_swr=ss)

    def get_state(self) -> dict:
        """Return all user‐entered values & toggles as a serializable dict."""
        return {
            # parse complex inputs (accepts “j” or “i”)
            'z0': self.z0_input.text().strip(),
            'y0': self.y0_input.text().strip(),
            'zl': self.zl_input.text().strip(),
            'yl': self.yl_input.text().strip(),

            #'z0': complex(self.z0_input.text().strip().replace('i', 'j'))
            #if self.z0_input.text().strip() else 0 + 0j,
            #'y0': complex(self.y0_input.text().strip().replace('i', 'j'))
            #if self.y0_input.text().strip() else 0 + 0j,
            #'zL': complex(self.zl_input.text().strip().replace('i', 'j'))
            #if self.zl_input.text().strip() else 0 + 0j,
            #'yL': complex(self.yl_input.text().strip().replace('i', 'j'))
            #if self.yl_input.text().strip() else 0 + 0j,
            'color': self.chart.impedances.get(self.panel_id).color,
            'show_adm': self.chk_adm.isChecked(),
            'show_swr_r1': self.chk_swr_r1.isChecked(),
            'to_gen': self.chk_to_gen.isChecked(),
            'show_gamma_angle': self.chk_gamma_angle.isChecked(),
        }

    def set_state(self, state):
        """Restore fields from a state dict, then trigger an update."""
        # reference impedance z0
        self.z0_input.setText(state.get('z0', self.z0_input.text()))

        # If the saved string y0 is non-empty → turn on “Show Admittance”
        y0_str = state.get('y0', "").strip()

        if y0_str != "":
            self.y0_input.setText(y0_str)
            self.chk_adm.setChecked(True)
        else:
            self.y0_input.setText("")
            self.chk_adm.setChecked(False)

        # load ZL and YL (keys are 'zl' / 'yl', not 'zL'/'yL')
        self.zl_input.setText(state.get('zl', self.zl_input.text()))
        self.yl_input.setText(state.get('yl', self.yl_input.text()))

        # restore chosen color on button
        color = state.get('color', '#000000')
        self.color_btn.setStyleSheet(f"background-color: {color};")
        self.color_btn.setProperty("pickedColor", color)
        # other toggles
        self.chk_swr_r1.setChecked(state.get('show_swr_r1', self.chk_swr_r1.isChecked()))
        self.chk_to_gen.setChecked(state.get('to_gen', self.chk_to_gen.isChecked()))
        self.chk_gamma_angle.setChecked(
            state.get('show_gamma_angle', self.chk_gamma_angle.isChecked())
        )
        # finally redraw
        self._on_change()



class ImpedancePanelManager(QWidget):
    """
    Container for multiple ImpedancePanel instances. Handles “Add New Impedance”
    button, determines panel_ids, and wires the remove button so that panels can
    be deleted and the chart is updated accordingly.
    """

    def __init__(self, chart):
        super().__init__()
        self.chart = chart

        layout = QGridLayout()
        layout.setSpacing(8)

        # “Add Impedance” button at the top
        self.add_btn = QPushButton("Add Impedance")
        self.add_btn.clicked.connect(self._add_panel)
        layout.addWidget(self.add_btn, 0, 0, 1, 2)
        row = 1

        # Scrollable container (QWidget) with QVBoxLayout that holds each panel
        self.container = QWidget()
        self.container_layout = QGridLayout()
        self.container.setLayout(self.container_layout)
        layout.addWidget(self.container, row, 0, 1, 2)
        row += 1

        self.setLayout(layout)

        # Storage of panel instances by numeric ID
        self.panels: Dict[int, ImpedancePanel] = {}
        # Numeric ID to assign to the next new panel
        self.next_id = 0

    def clear_all(self):
        """Remove every panel."""
        for pid in list(self.panels.keys()):
            self._remove_panel(pid)

    def _add_panel(self):
        panel_id = self.next_id

        # 1) register a fresh ImpedanceConfig for this panel on the chart
        self.chart.register_impedance(panel_id)

        # 2) create the UI panel, passing in the chart callbacks
        panel = ImpedancePanel(
            panel_id,
            self.chart,
            update_cb=self.chart.update_impedance,
            remove_cb=self._remove_panel,
            update_opts_cb=self.chart.update_impedance_options,  # seldom used
        )

        # 3) keep track of the panel instance and add it to the scroll‐area layout
        self.panels[self.next_id] = panel
        self.container_layout.addWidget(panel)

        # 4) advance to the next available ID
        self.next_id += 1

        # 5) (optional) if you ever need to immediately push defaults into the chart,
        #    you can uncomment these. Usually the panel’s own __init__ will fire off
        #    an initial update_cb, so you may not need it.
        self.chart.update_impedance(panel_id)
        panel.on_toggle()
        return panel


    def _remove_panel(self, panel_id):
        p = self.panels.pop(panel_id, None)
        if p:
            p.setParent(None)
            self.chart.remove_impedance(panel_id)
