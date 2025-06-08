import yaml
from dataclasses import dataclass, field, fields

from PyQt5.QtGui import QColor, QFont, QIcon, QWindow


@dataclass(init=True)
class SaveFileStructure:
    window_settings: dict = field(default_factory=lambda: {
        "window_title": "",
        "window_size": (800, 600),             # you can pick sensible defaults
        "window_position": (100, 100),
        "window_icon_location": "",
        "window_icon": None,
        "window_background_color": QColor("white"),
        "window_foreground_color": QColor("black"),
        "window_font": "Arial",
        "window_font_size": 10,
        "window_font_style": QFont.StyleNormal,
        "window_font_weight": QFont.Weight.Normal,
    })
    chart_settings: dict = field(default_factory=lambda: {
        "background": QColor("white"),
        "size": (400, 400),
        "position": (0, 0),
        "label_font": QFont.StyleNormal,
        "label_font_size": 8,
        "label_font_style": QFont.StyleNormal,
        "label_font_weight": QFont.Weight.Normal,
        "show_impedance_grid": True,
        "show_reactance_grid": True,
        "regions_count": 0,
        "regions": [],
    })
    chart_objects_list: dict = field(default_factory=lambda: {
        "number_of_objects": 0,
        "objects": [],
    })

    def update_chart_objects(self, operation, number=None):
        if operation == "add":
            self.chart_objects_list["number_of_objects"] += 1
            self.chart_objects_list["objects"].append({})
        elif operation == "remove":
            self.chart_objects_list["objects"].pop(number)
            self.chart_objects_list["number_of_objects"] -= 1
        else:
            raise ValueError("Invalid operation")


    def get_state(self, get_type) -> dict:
        if get_type == "window_settings":
            return self.window_settings
        elif get_type == "chart_settings":
            return self.chart_settings
        elif get_type == "chart_objects_list":
            return self.chart_objects_list
        else:
            raise ValueError("Invalid get_type")

    def set_state(self, set_type, state: dict):
        if set_type == "window_settings":
            self.window_settings = state
        elif set_type == "chart_settings":
            self.chart_settings = state
        elif set_type == "chart_objects_list":
            self.chart_objects_list = state
        else:
            raise ValueError("Invalid set_type")

class DataManagement:
    def __init__(self,save_file):
        self.session_data = SaveFileStructure()
        self.save_file = save_file
        self.save_config()


    def load_config(self):
        with open(self.save_file, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as yaml_exception:
                print(yaml_exception)
        return config

    def save_config(self):
        tmp_dict = {}
        # iterate over all @dataclass fields
        for f in fields(self.session_data):
            name = f.name
            value = getattr(self.session_data, name)
            tmp_dict[name] = value
        with open(self.save_file, 'w') as stream:
            try:
                yaml.dump(tmp_dict, stream)
            except yaml.YAMLError as yaml_exception:
                print(yaml_exception)
