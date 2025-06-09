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
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod

from PyQt5.QtGui import QColor, QFont, QIcon, QWindow

## Get Constructors and Representers from yaml_everywhere.py
#from .yaml_everywhere import register_yaml_qt_types
#register_yaml_qt_types()

@dataclass
class DataManagementAbstract(ABC):
    BackgroundColor: QColor = field(default_factory=lambda: QColor("white"))
    ForegroundColor: QColor = field(default_factory=lambda: QColor("white"))
    # Titles
    TitleFont: QFont.Style = field(default=QFont.Style)
    TitleFontSize: int = field(default=8)
    TitleFontStyle: QFont.Style = field(default=QFont.Style)
    TitleFontWeight: QFont.Weight = field(default=QFont.Weight)
    TitleFontColor: QColor = field(default_factory=lambda: QColor("white"))
    # Labels
    LabelFont: QFont.Style = field(default=QFont.Style)
    LabelFontSize: int = field(default=8)
    LabelFontStyle: QFont.Style = field(default=QFont.Style)
    LabelFontWeight: QFont.Weight = field(default=QFont.Weight)
    LabelFontColor: QColor = field(default_factory=lambda: QColor("white"))
    # For Specific Line or Point Objects
    ObjectCount: int = field(default=0)
    ObjectColor: QColor = field(default_factory=lambda: QColor("white"))
    ObjectLineWidth: int = field(default=1)
    ObjectLineStyle: str = field(default="solid")
    ObjectLineDash: str = field(default="")
    # Visibility
    Visible: bool = field(default=True)

@dataclass
class ChartRegionsTemplate(DataManagementAbstract,ABC):
    # Using Constant Reactance Lines, so specify the complex portion
    StartingReactance: int = field(default=-90)
    EndingReactance: int = field(default=90)
    ReactanceLineDensity: int = field(default=5)
    # Using Constant Resistance Lines, so specify the real portion
    StartingResistance: int = field(default=1000)
    EndingResistance: int = field(default=1)
    ResistanceLineDensity: int = field(default=5)

@dataclass
class RfObjectTemplate(DataManagementAbstract):
    # For RF Object indexed by Number
    Number: int = 1
    # How RF Object is Instantiated: impedance, admittance, or centerline trace
    Type: str = field(default="impedance")
    # Mode is about displaying impedance or admittance
    Mode: str = field(default="impedance")
    Impedance: complex = field(default=complex(0,0))
    Admittance: complex = field(default=complex(0,0))
    ReflectionCoefficient: complex = field(default=complex(0,0))
    ReflectionPhase: float = field(default=0.0)
    ReflectionMagnitude: float = field(default=0.0)
    StandingWaveRatio: float = field(default=0.0)
    ShowSwrCircle: bool = field(default=True)
    WavelengthsTowardsGenerator: float = field(default=0.0)
    IntersectionWithUnityA: complex = field(default=complex(1,0))
    IntersectionWithUnityB: complex = field(default=complex(1,0))
    Draggable: bool = field(default=False)
    SnapToLines: bool = field(default=False)
    SnapToPoints: bool = field(default=False)
    TraceResistance: bool = field(default=True)
    TraceReactance: bool = field(default=True)

@dataclass()
class ChartState(DataManagementAbstract, ABC):
    # Chart Settings
    Size: QWindow.size = field(default=QWindow.size)
    Position: QWindow.position = field(default=QWindow.position)
    ShowImpedanceGrid: bool = field(default=True)
    ShowReactanceGrid: bool = field(default=True)
    ## For Chart Display Grid Settings
    RegionsCount: int = field(default=1)
    Regions: list[ChartRegionsTemplate] = field(default_factory=list)
    ## For RF Objects
    RfObjectsCount: int = field(default=1)
    RfObjects: list[RfObjectTemplate] = field(default_factory=list)
    def _update_regions(self, regions_count):
        if regions_count > len(self.Regions):
            for i in range(len(self.Regions), regions_count):
                self.Regions.append(ChartRegionsTemplate())
        elif regions_count < len(self.Regions):
            self.Regions = self.Regions[:regions_count]
    def _update_rf_objects(self, rf_objects_count):
        if rf_objects_count > len(self.RfObjects):
            for i in range(len(self.RfObjects), rf_objects_count):
                self.RfObjects.append(RfObjectTemplate())

    def parse_session(self, session):
        self.Size = session["Size"]
        self.Position = session["Position"]
        self.ShowImpedanceGrid = session["ShowImpedanceGrid"]
        self.ShowReactanceGrid = session["ShowReactanceGrid"]
        self.RegionsCount = session["RegionsCount"]
        self.Regions = session["Regions"]
        self.RfObjectsCount = session["RfObjectsCount"]
        self.RfObjects = session["RfObjects"]

    def __post_init__(self):
        self._update_regions(self.RegionsCount)
        self._update_rf_objects(self.RfObjectsCount)


@dataclass
class WindowState(DataManagementAbstract,ABC):
    # Window Settings
    WindowTitle: str = field(default="YABASCO")
    WindowSize: QWindow.size = field(default=QWindow.size)
    WindowPosition: QWindow.position = field(default=QWindow.position)
    WindowIconLocation: str = field(
        default="C:/repos/learning_python/yabasco_icon.ico")
    def parse_session(self, session):
        self.WindowTitle = session["WindowTitle"]
        self.WindowSize = session["WindowSize"]
        self.WindowPosition = session["WindowPosition"]
        self.WindowIconLocation = session["WindowIconLocation"]



class DataManagement:
    def __init__(self, session_file="session.yaml"):
        self.session = session_file
        self.window = WindowState()
        self.chart = ChartState()

    def _serialize(self, data):
        """
        Recursively convert dicts/lists of Qt objects or enums
        into basic Python types (str/int) so PyYAML can dump them.
        """
        if isinstance(data, dict):
            return {k: self._serialize(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._serialize(v) for v in data]
        # basic YAML types pass through
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        # QColor → its hex name
        if isinstance(data, QColor):
            return data.name()
        # fallback: convert anything else to str()
        return str(data)

    def save_yaml(self, session_file):
        with open(session_file, 'w') as outfile:
            chart_dict = asdict(self.chart)
            window_dict = asdict(self.window)
            # convert non-YAML-native objects into primitives
            chart_safe = self._serialize(chart_dict)
            window_safe = self._serialize(window_dict)

            yaml.dump(
                {"chart": chart_safe, "window": window_safe},
                #{"chart": chart_dict, "window": window_dict},
                outfile,
                Dumper=yaml.SafeDumper,
                default_flow_style=False
            )

    def load_yaml(self, session_file):
        with open(session_file, 'r') as stream:
            try:
                session = yaml.load(stream, Loader=yaml.FullLoader)
                print(
                    f"Loaded session from {session_file}:\n"
                    f"  Chart: {session['chart']}\n"
                    f"  Window: {session['window']}"
                )
                self.chart.parse_session(session.get("chart", {}))
                self.window.parse_session(session.get("window", {}))
            except yaml.YAMLError as yaml_exception:
                print(yaml_exception)