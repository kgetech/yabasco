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
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui  import QRegularExpressionValidator

class ComplexValidator(QRegularExpressionValidator):
    def __init__(self, parent=None):
        rx = QRegularExpression(
            r"^[+-]?\d*\.?\d+([eE][+-]?\d+)?"
            r"([+-]\d*\.?\d+([eE][+-]?\d+)?)?[ij]?$"
        )
        super().__init__(rx, parent)
