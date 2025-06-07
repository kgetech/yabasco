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
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction, QFileDialog, QMessageBox
from .smith_chart_canvas import SmithChartCanvas
from .impedance_input_panel import ImpedancePanelManager
from .grid_settings_panel import GridSettingsPanel

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

        save_chart = QAction("&Save Chart...", self)
        save_chart.triggered.connect(self._save_chart)
        file_menu.addAction(save_chart)

        save_sess = QAction("Save &Session...", self)
        save_sess.triggered.connect(self._save_session)
        file_menu.addAction(save_sess)

        load_sess = QAction("&Load Session...", self)
        load_sess.triggered.connect(self._load_session)
        file_menu.addAction(load_sess)

        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _save_session(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save Session as JSON", "", "JSON (*.json)")
        if not fn:
            return
        session = {
            'grid':   self.grid_settings.get_state(),
            'panels': [p.get_state() for p in self.panel_mgr.panels.values()]
        }
        try:
            with open(fn, 'w') as f:
                json.dump(session, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error Saving Session", str(e))

    def _load_session(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open Session JSON", "", "JSON (*.json)")
        if not fn:
            return
        try:
            with open(fn) as f:
                session = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Session", str(e))
            return

        # restore grid settings
        self.grid_settings.set_state(session.get('grid', {}))

        # clear and restore impedance panels
        self.panel_mgr.clear_all()
        for st in session.get('panels', []):
            panel = self.panel_mgr._add_panel()
            panel.set_state(st)



    def _save_chart(self):
        from PyQt5.QtWidgets import QFileDialog
        fn, _ = QFileDialog.getSaveFileName(
            self,
            "Save Chart Image",
            "",
            "PNG (*.png);;SVG (*.svg)"
        )
        if fn:
            self.chart.save_chart(fn)