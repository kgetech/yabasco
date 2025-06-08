import yaml
from dataclasses import dataclass, field

from PyQt5.QtGui import QColor, QFont, QIcon, QWindow

def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as yaml_exception:
            print(yaml_exception)
    return config

@dataclass(init=True)
class SaveFileStructure:
    window_settings = {
        "window_title": str,
        "window_size": QWindow.Size,
        "window_position": QWindow.Position,
        "window_icon_location": str,
        "window_icon": QIcon,
        "window_background_color": QWindow.Color,
        "window_foreground_color": QWindow.Color,
        "window_font": str,
        "window_font_size": int,
        "window_font_style": QFont.Style,
        "window_font_weight": QFont.Weight
    },
    chart_settings = {
        "background": QColor,
        "size": QWindow.Size,
        "position": QWindow.Position,
        "label_font": QFont.Style,
        "label_font_size": int,
        "label_font_style": QFont.Style,
        "label_font_weight": QFont.Weight,
        "show_impedance_grid": bool,
        "show_reactance_grid": bool,
        # For adjusting the base grid of the chart.
        "regions_count": int,
        "regions":{
            "starting_angle": int,
            "ending_angle": int,
            "color": QColor,
            "line_width": int,
            "line_style": str,
            "line_dash": str,
        }
    },

    _chart_object_template = {
        "number": int,
        "type": str, #impedance admittance or centerline trace
        "mode": str, # displaying: impedance or admittance
        "impedance": complex,
        "admittance": complex,
        "reflection_coefficient": complex,
        "reflection_phase": float,
        "reflection_magnitude": float,
        "standing_wave_ratio": float,
        "wavelengths_towards_generator": float,
        "intersections_with_unity": {
            "a": complex,
            "b": complex
        },
        "draggable": bool,
        "snap_to_lines": bool,
        "snap_to_points": bool,
        "visible": bool,
        "trace_resistance": bool,
        "trace_reactance": bool,
        "color": QColor,
        "line_width": int,
        "line_style": str,
        "line_dash": str,
        "line_dash_offset": int,
    }

    chart_objects_list = {
        "number_of_objects": int,
        "objects": list,

    }

    def update_chart_objects(self, operation, number):
        if operation == "add":
            self.chart_objects_list["number_of_objects"] += 1
            self.chart_objects_list["objects"].append(
                self._chart_object_template)
        elif operation == "remove":
            self.chart_objects_list["number_of_objects"] -= 1
            self.chart_objects_list["objects"].pop(number)
        else:
            raise ValueError("Invalid operation")

    def get_state(self, get_type):
        if get_type == "window_settings":
            return self.window_settings
        elif get_type == "chart_settings":
            return self.chart_settings
        elif get_type == "chart_objects_list":
            return self.chart_objects_list
        else:
            raise ValueError("Invalid get_type")

    def set_state(self, set_type, state):
        if set_type == "window_settings":
            self.window_settings = state
        elif set_type == "chart_settings":
            self.chart_settings = state
        elif set_type == "chart_objects_list":
            self.chart_objects_list = state
        else:
            raise ValueError("Invalid set_type")

class DataManagement:
    def __init__(self, config_file):
        self.config = load_config(config_file)

    def generate_save_file_structure(self):
        pass
        #return save_file_struct