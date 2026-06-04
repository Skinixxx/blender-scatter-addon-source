bl_info = {
    "name": "Parametric Scatter",
    "author": "Variant 46",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Scatter",
    "description": "Parametric object scattering controlled by texture maps",
    "category": "Object",
}

import bpy

from . import operators
from . import ui
from . import properties


modules = (properties, operators, ui)


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in reversed(modules):
        mod.unregister()


if __name__ == "__main__":
    register()
