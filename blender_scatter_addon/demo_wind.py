"""
Demo: Wind animation via GN
Run: blender --python demo_wind.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from blender_scatter_addon import register
register()

bpy.ops.mesh.primitive_grid_add(x_subdivisions=20, y_subdivisions=20, size=6)
target = bpy.context.active_object
target.name = "Field"

bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.4)
stem = bpy.context.active_object
stem.name = "Stem"
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0, 0.4))
head = bpy.context.active_object
head.name = "Head"
bpy.ops.object.select_all(action='DESELECT')
head.select_set(True)
stem.select_set(True)
bpy.context.view_layer.objects.active = stem
bpy.ops.object.join()
plant = stem
plant.name = "GrassBlade"

s = bpy.context.scene.scatter_settings
s.source_object = plant
s.target_object = target
s.count = 300
s.scale_min = 0.4
s.scale_max = 1.8
s.use_wind = True
s.wind_strength = 0.8
s.wind_direction = (1.0, 0.5, 0.0)
s.wind_frequency = 2.0
s.random_seed = 33
s.use_geometry_nodes = True

bpy.ops.scatter.execute()

if not bpy.app.background:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].shading.type = 'MATERIAL'
            area.spaces[0].region_3d.view_distance = 7

wind_mods = [m for m in target.modifiers if 'Wind' in m.name]
print(f"Wind demo: {s.count} grass blades with {len(wind_mods)} wind modifier(s)")
print(f"  Settings: strength={s.wind_strength}, dir={tuple(s.wind_direction)}, freq={s.wind_frequency}")
print("  Scrub timeline to see animation")
