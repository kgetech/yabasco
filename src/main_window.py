from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction, QFileDialog, QMessageBox
import yaml

from .rf_objects_panel import RfObjectsPanel
from .chart_settings_panel import ChartSettingsPanel

class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.dm = data_manager

        # Window title: call the method (or use attribute) to get a string
        title = (self.dm.window.WindowTitle()
                 if callable(self.dm.window.WindowTitle)
                 else self.dm.window.WindowTitle)
        self.setWindowTitle(title)

        # Window size: normalize to (w, h)
        ws = getattr(self.dm.window, "WindowSize", None)
        if ws is None:
            width, height = 800, 600  # fallback default
        else:
            if callable(ws):
                try:
                    raw = ws()
                except TypeError:
                    raw = ws
            else:
                raw = ws

            if isinstance(raw, QSize):
                width, height = raw.width(), raw.height()
            elif isinstance(raw, (tuple, list)) and len(raw) == 2:
                width, height = raw
            else:
                print(f"Warning: WindowSize must be QSize or (w,h), got {type(raw)}; using default.")
                width, height = 800, 600

        self.resize(width, height)

        # — Immediately store a real QSize back into your data model —
        self.dm.window.WindowSize = QSize(width, height)

        # Menu bar → File → Save Chart / Exit
        self._create_menu()

        # Left dock: rf object settings
        self.left_dock = QDockWidget("RF Objects", self)
        self.left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.left_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        #self.left_dock.setWidget()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        # Right dock: Chart Settings
        self.right_dock = QDockWidget("Chart Settings", self)
        self.right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.right_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        #self.right_dock.setWidget(self.dm.chart_settings_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

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
        fn, _ = QFileDialog.getSaveFileName(self, "Save Session as YAML", "",
                                            "YAML (*.yaml *.yml);;All Files (*.*)")
        if not fn:
            return
        try:
            self.dm.save_yaml(session_file=fn)
        except yaml.YAMLError as err:
            print(str(err))
            QMessageBox.critical(self, "Error Saving Session", str(err))

    def _load_session(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open Session YAML", "",
                                            "YAML (*.yaml *.yml);;All Files (*.*)")
        if not fn:
            return
        try:
            self.dm.load_yaml(session_file=fn)
        except yaml.YAMLError as err:
            QMessageBox.critical(self, "Error Loading Session", str(err))
            return

    def _save_chart(self,path):
        self.dm.chart.fig.savefig(path, dpi=300)