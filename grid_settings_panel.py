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
from typing import Any
from PyQt5.QtWidgets import QWidget, QCheckBox, QSpinBox, QVBoxLayout

class GridSettingsPanel(QWidget):
    def __init__(self, apply_cb: Any):
        super().__init__()
        self._apply_cb = apply_cb

        self.show_unit = QCheckBox("Show Unit Circle")
        self.show_unit.setChecked(True)
        # connect signals…
        # self.show_unit.stateChanged.connect(self._on_setting_change)

        layout = QVBoxLayout(self)
        layout.addWidget(self.show_unit)
        # … add other controls

    def _on_setting_change(self) -> None:
        # gather all settings and call back:
        cfg = {
            'show_unit': self.show_unit.isChecked(),
            # …
        }
        self._apply_cb(cfg)