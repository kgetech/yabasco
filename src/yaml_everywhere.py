###############################################################################
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
###############################################################################
## Purpose: Core data structures, isolated from the GUI.
###############################################################################

import yaml
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtCore import QPoint, QSize, QPointF, QSizeF, QRect, QRectF

# QColor
def qcolor_representer(dumper, data):
    return dumper.represent_scalar('!QColor', data.name())

# QFont Style and Weight
def qfont_style_representer(dumper, data):
    return dumper.represent_scalar('!QFontStyle', str(int(data)))

def qfont_weight_representer(dumper, data):
    return dumper.represent_scalar('!QFontWeight', str(int(data)))

# QPoint
def qpoint_representer(dumper, data):
    return dumper.represent_sequence('!QPoint', [data.x(), data.y()])

# QSize
def qsize_representer(dumper, data):
    return dumper.represent_sequence('!QSize', [data.width(), data.height()])

# QIcon (represented as the file path only)
def qicon_representer(dumper, data):
    return dumper.represent_scalar('!QIcon', data.name())



# Constructors for loading YAML back into Qt types
# QColor
def qcolor_constructor(loader, node):
    value = loader.construct_scalar(node)
    return QColor(value)

# QFont.Style
def qfont_style_constructor(loader, node):
    value = int(loader.construct_scalar(node))
    return QFont.Style(value)

# QFont.Weight
def qfont_weight_constructor(loader, node):
    value = int(loader.construct_scalar(node))
    return QFont.Weight(value)

# QPoint
def qpoint_constructor(loader, node):
    values = loader.construct_sequence(node)
    return QPoint(*values)

# QSize
def qsize_constructor(loader, node):
    values = loader.construct_sequence(node)
    return QSize(*values)

# QIcon
def qicon_constructor(loader, node):
    path = loader.construct_scalar(node)
    return QIcon(path)

#deploy the constructors and representers
def update_yams():
    # Registration
    yaml.SafeDumper.add_representer(QColor, qcolor_representer)
    yaml.SafeDumper.add_representer(QFont.Style, qfont_style_representer)
    yaml.SafeDumper.add_representer(QFont.Weight, qfont_weight_representer)
    yaml.SafeDumper.add_representer(QPoint, qpoint_representer)
    yaml.SafeDumper.add_representer(QSize, qsize_representer)
    yaml.SafeDumper.add_representer(QIcon, qicon_representer)


    # Register constructors
    yaml.SafeLoader.add_constructor('!QColor', qcolor_constructor)
    yaml.SafeLoader.add_constructor('!QFontStyle', qfont_style_constructor)
    yaml.SafeLoader.add_constructor('!QFontWeight', qfont_weight_constructor)
    yaml.SafeLoader.add_constructor('!QPoint', qpoint_constructor)
    yaml.SafeLoader.add_constructor('!QSize', qsize_constructor)
    yaml.SafeLoader.add_constructor('!QIcon', qicon_constructor)

