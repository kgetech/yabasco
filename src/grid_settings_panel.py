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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QLabel,QPushButton, QColorDialog,
    QSpinBox, QDoubleSpinBox, QCheckBox
)
# ─────────────────────────────────────────────────────────────────────────────
# GridSettingsPanel: right-hand dock for all chart/grid parameters
# ─────────────────────────────────────────────────────────────────────────────

class GridSettingsPanel(QWidget):
    """
    Right-dock UI with settings for grid.
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
        # Initialize button to the chart’s current gamma_color:
        self.gamma_color_btn.setStyleSheet(f"background-color: {self.chart.gamma_circle_color};")
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
        # Initialize to chart’s current r1_color:
        self.r1_color_btn.setStyleSheet(f"background-color: {self.chart.r1_color};")
        layout.addWidget(self.r1_color_btn, 8, 0, 1, 2)

        # 10) Show Unit Circle
        self.unit_chk = QCheckBox("Show Unit Circle")
        self.unit_chk.setChecked(chart.show_unit)
        self.unit_chk.stateChanged.connect(
            lambda s: chart.update_grid(show_unit=(s == Qt.Checked))
        )
        layout.addWidget(self.unit_chk, 10, 0, 1, 2)

        # 11) Select Grid Color (applies to R/X/Radial/Unit/Γ)
        self.grid_color_btn = QPushButton("Select Grid Color")
        self.grid_color_btn.clicked.connect(self._pick_grid_color)
        # Initialize to chart’s current resistance_color (which is the grid color)
        self.grid_color_btn.setStyleSheet(f"background-color: {self.chart.resistance_color};")
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
            self._set_color_button(self.gamma_color_btn, c.name(), apply=True)


    def _pick_r1_color(self):
        """ColorDialog → set chart.r1_color."""
        c = QColorDialog.getColor(initial=QColor(self.chart.r1_color),
                                  parent=self,
                                  title="Pick R=1 Circle Color")
        if c.isValid():
            self._set_color_button(self.r1_color_btn, c.name(), apply=True)


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
            self._set_color_button(self.grid_color_btn, c.name(), apply=True)

    def _set_color_button(self, btn, color_str, apply=False):
        """
        Apply a saved color (hex string) to a standard QPushButton and, if requested,
        push the change into the chart via update_grid().
        """
        # 1) Show the color on the button
        btn.setStyleSheet(f"background-color: {color_str};")
        # 2) (Optional) keep it as a property in case your picker logic wants it
        btn.setProperty("pickedColor", color_str)

        # 3) If this is part of loading/applying saved state, update the chart
        if apply:
            if btn is self.grid_color_btn:
                self.chart.update_grid(grid_color=color_str)
            elif btn is self.r1_color_btn:
                self.chart.update_grid(r1_color=color_str)
            elif btn is self.gamma_color_btn:
                self.chart.update_grid(gamma_color=color_str)

    def get_state(self) -> dict:
        def btn_color(btn):
            # expect styleSheet like "background-color: #RRGGBB;"
            ss = btn.styleSheet() or ""
            parts = ss.split("background-color:")
            if len(parts) > 1:
                return parts[1].split(";")[0].strip()
            return "#000000"

        return {
            'num_r_outer_lines': self.r1_spin.value(),
            'num_r_inner_lines': self.r2_spin.value(),
            'num_x_lines': self.x_spin.value(),
            'label_resistance_every': self.rl_spin.value(),
            'label_reactance_every': self.xl_spin.value(),
            'x_label_at_r': self.il_spin.value(),
            'show_unit': self.unit_chk.isChecked(),
            'show_r1': self.r1_chk.isChecked(),
            'grid_color': btn_color(self.grid_color_btn),
            'r1_color': btn_color(self.r1_color_btn),
            'gamma_color': btn_color(self.gamma_color_btn),
        }

    def set_state(self, state: dict):
        """
        Restore widget settings from a state dict, then push them
        into the chart via update_grid().
        """
        self.r1_spin.setValue(state.get('num_r_outer_lines', self.r1_spin.value()))
        self.r2_spin.setValue(state.get('num_r_inner_lines', self.r2_spin.value()))
        self.x_spin.setValue(state.get('num_x_lines', self.x_spin.value()))
        self.rl_spin.setValue(state.get('label_resistance_every', self.rl_spin.value()))
        self.xl_spin.setValue(state.get('label_reactance_every', self.xl_spin.value()))
        self.il_spin.setValue(state.get('x_label_at_r', self.il_spin.value()))
        self.unit_chk.setChecked(state.get('show_unit', self.unit_chk.isChecked()))
        self.r1_chk.setChecked(state.get('show_r1', self.r1_chk.isChecked()))

        # Restore colors and apply
        if 'grid_color' in state:
            self._set_color_button(self.grid_color_btn, state['grid_color'], apply=True)
        if 'r1_color' in state:
            self._set_color_button(self.r1_color_btn, state['r1_color'], apply=True)
        if 'gamma_color' in state:
            self._set_color_button(self.gamma_color_btn, state['gamma_color'], apply=True)

        # Finally, push everything into the chart at once:
        # (this duplicates what get_state() would return, but ensures immediate redraw)
        # NOTE: btn_color() is used to retrieve the current button‐color string.
        def btn_color(btn):
            ss = btn.styleSheet() or ""
            parts = ss.split("background-color:")
            if len(parts) > 1:
                return parts[1].split(";")[0].strip()
            return "#000000"

        self.chart.update_grid(
            num_r_outer=self.r1_spin.value(),
            num_r_inner=self.r2_spin.value(),
            num_x=self.x_spin.value(),
            label_r_every=self.rl_spin.value(),
            label_x_every=self.xl_spin.value(),
            x_label_at_r=self.il_spin.value(),
            show_unit=self.unit_chk.isChecked(),
            show_r1=self.r1_chk.isChecked(),
            grid_color=btn_color(self.grid_color_btn),
            r1_color=btn_color(self.r1_color_btn),
            gamma_color=btn_color(self.gamma_color_btn),
        )
