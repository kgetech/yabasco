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
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter
from smith_chart_renderer import SmithChartCanvas
from impedance_input_panel import ImpedancePanel
from grid_settings_panel import GridSettingsPanel

class SmithChartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chart = SmithChartCanvas()
        self.panel_mgr = {}  # panel_id -> ImpedancePanel
        self.next_id = 1

        # layout
        root = QWidget()
        layout = QVBoxLayout(root)
        splitter = QSplitter()
        layout.addWidget(splitter)
        splitter.addWidget(self.chart)

        self.controls = QWidget()
        c_layout = QVBoxLayout(self.controls)
        self.controls.setLayout(c_layout)
        splitter.addWidget(self.controls)

        # “Add Panel” button
        from PyQt5.QtWidgets import QPushButton
        btn = QPushButton("Add Impedance")
        btn.clicked.connect(self.add_panel)
        c_layout.addWidget(btn)

        # grid settings
        grid_panel = GridSettingsPanel(self.chart._draw_static_elements)
        c_layout.addWidget(grid_panel)

        self.setCentralWidget(root)

    def add_panel(self) -> None:
        pid = self.next_id
        self.next_id += 1
        panel = ImpedancePanel(pid,
                               update_cb=self.chart.update_impedance,
                               remove_cb=self._remove_panel)
        self.panel_mgr[pid] = panel
        self.controls.layout().addWidget(panel)

    def _remove_panel(self, pid: int) -> None:
        panel = self.panel_mgr.pop(pid, None)
        if panel:
            panel.setParent(None)
            panel.deleteLater()
            self.chart.remove_impedance(pid)