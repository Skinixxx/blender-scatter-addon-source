"""
Demo: Geometry Nodes scatter (non-destructive)
Run: blender --python demo_gn.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from blender_scatter_addon import register
register()

bpy.ops.mesh.primitive_grid_add(x_subdivisions=20, y_subdivisions=20, size=6)
target = bpy.context.view_layer.objects.active
target.name = "Terrain"

bpy.ops.mesh.primitive_ico_sphere_add(radius=0.15, subdivisions=2)
source = bpy.context.view_layer.objects.active
source.name = "Rock"

s = bpy.context.scene.scatter_settings
s.source_object = source
s.target_object = target
s.count = 200
s.scale_min = 0.3
s.scale_max = 1.5
s.use_geometry_nodes = True
s.random_seed = 42
s.avoid_overlap = True

bpy.ops.scatter.execute()

if not bpy.app.background:
    for area in getattr(bpy.context.screen, 'areas', []):
        if area.type == 'VIEW_3D':
            area.spaces[0].shading.type = 'MATERIAL'
            area.spaces[0].region_3d.view_distance = 8

print(f"GN scatter: {s.count} rocks via modifier"
      f" ({len([m for m in target.modifiers if 'Scatter' in m.name])} modifier)")
