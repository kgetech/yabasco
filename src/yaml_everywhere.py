import yaml
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtCore import QPoint, QSize

# Central registry of (Python type, YAML tag, representer, constructor)
_YAML_REGISTRY = [
    (
        QColor, '!QColor',
        lambda dumper, obj: dumper.represent_scalar('!QColor', obj.name()),
        lambda loader, node: QColor(loader.construct_scalar(node))
    ),
    (
        QFont.Style, '!QFontStyle',
        lambda dumper, obj: dumper.represent_scalar('!QFontStyle', str(int(obj))),
        lambda loader, node: QFont.Style(int(loader.construct_scalar(node)))
    ),
    (
        QFont.Weight, '!QFontWeight',
        lambda dumper, obj: dumper.represent_scalar('!QFontWeight', str(int(obj))),
        lambda loader, node: QFont.Weight(int(loader.construct_scalar(node)))
    ),
    (
        QPoint, '!QPoint',
        lambda dumper, obj: dumper.represent_sequence('!QPoint', [obj.x(), obj.y()]),
        lambda loader, node: QPoint(*loader.construct_sequence(node))
    ),
    (
        QSize, '!QSize',
        lambda dumper, obj: dumper.represent_sequence('!QSize', [obj.width(), obj.height()]),
        lambda loader, node: QSize(*loader.construct_sequence(node))
    ),
    (
        QIcon, '!QIcon',
        lambda dumper, obj: dumper.represent_scalar('!QIcon', obj.name()),
        lambda loader, node: QIcon(loader.construct_scalar(node))
    ),
]

def register_yaml_qt_types():
    """
    Register custom YAML representers and constructors for common Qt types.
    """
    for py_type, tag, repr_fn, ctor_fn in _YAML_REGISTRY:
        yaml.SafeDumper.add_representer(py_type, repr_fn)
        yaml.SafeLoader.add_constructor(tag, ctor_fn)