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

class RfObjectsPanel(QWidget):

    def __init__(self, rf_objects_panel):
        super().__init__()
        self.rf_objects_panel = rf_objects_panel

        layout = QGridLayout()
        layout.setSpacing(8)

        # “Add Impedance” button at the top
        self.add_btn = QPushButton("Add RF Object")
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
        self.panels: Dict[int, RfObject] = {}
        # Numeric ID to assign to the next new panel
        self.next_id = 0

    def clear_all(self):
        """Remove every panel."""
        for pid in list(self.panels.keys()):
            self._remove_panel(pid)

    def _add_panel(self):
        panel_id = self.next_id

        # 1) register a fresh RfObject for this panel on the chart


        # 2) create the UI panel, passing in the rf object callbacks
        panel = RfObject(
            #panel_id,
            #self.chart,
            #update_cb=self.chart.update_impedance,
            #remove_cb=self._remove_panel,
            #update_opts_cb=self.chart.update_impedance_options,  # seldom used
        )

        # 3) keep track of the panel instance and add it to the scroll‐area layout
        self.panels[self.next_id] = panel
        self.container_layout.addWidget(panel)

        # 4) advance to the next available ID
        self.next_id += 1

        # 5) (optional) if you ever need to immediately push defaults into the chart,
        #    you can uncomment these. Usually the panel’s own __init__ will fire off
        #    an initial update_cb, so you may not need it.
        self.rf_objects_panel.update_impedance(panel_id)
        panel.on_toggle()
        return panel


    def _remove_panel(self, panel_id):
        p = self.panels.pop(panel_id, None)
        if p:
            p.setParent(None)
            self.chart.remove_impedance(panel_id)
