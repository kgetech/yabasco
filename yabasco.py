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
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

from src.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Apply a “Fusion” dark palette to match JetBrains‐quality UX
    dark = QPalette()
    dark.setColor(QPalette.Window,             QColor(53, 53, 53))
    dark.setColor(QPalette.WindowText,         Qt.white)
    dark.setColor(QPalette.Base,               QColor(25, 25, 25))
    dark.setColor(QPalette.AlternateBase,      QColor(53, 53, 53))
    dark.setColor(QPalette.ToolTipBase,        Qt.white)
    dark.setColor(QPalette.ToolTipText,        Qt.white)
    dark.setColor(QPalette.Text,               Qt.white)
    dark.setColor(QPalette.Button,             QColor(53, 53, 53))
    dark.setColor(QPalette.ButtonText,         Qt.white)
    dark.setColor(QPalette.BrightText,         Qt.red)
    dark.setColor(QPalette.Link,               QColor(42, 130, 218))
    dark.setColor(QPalette.Highlight,          QColor(42, 130, 218))
    dark.setColor(QPalette.HighlightedText,    Qt.black)
    app.setPalette(dark)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()