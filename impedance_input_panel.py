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
from typing import Callable
from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QHBoxLayout, QLabel, QPushButton
)
from complex_number_validator import ComplexValidator

class ImpedancePanel(QWidget):
    def __init__(self,
                 panel_id: int,
                 update_cb: Callable,
                 remove_cb: Callable):
        super().__init__()
        self.panel_id = panel_id
        self._update_cb = update_cb
        self._remove_cb = remove_cb

        self.zl_input = QLineEdit()
        self.yl_input = QLineEdit()
        for w in (self.zl_input, self.yl_input):
            w.setValidator(ComplexValidator(self))
            w.editingFinished.connect(self._on_change)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(lambda: remove_cb(self.panel_id))

        # layout
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("ZL"))
        layout.addWidget(self.zl_input)
        layout.addWidget(QLabel("YL"))
        layout.addWidget(self.yl_input)
        layout.addWidget(self.remove_btn)

    def _on_change(self) -> None:
        zl_text = self.zl_input.text()
        yl_text = self.yl_input.text()
        if not (self.zl_input.hasAcceptableInput()
                and self.yl_input.hasAcceptableInput()):
            return
        zl = complex(zl_text.replace('i','j'))
        yl = complex(yl_text.replace('i','j'))
        self._update_cb(self.panel_id, zl, yl)