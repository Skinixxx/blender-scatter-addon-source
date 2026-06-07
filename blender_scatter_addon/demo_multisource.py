"""
Demo: Multi-source scatter
Run: blender --python demo_multisource.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from blender_scatter_addon import register
register()

bpy.ops.mesh.primitive_grid_add(x_subdivisions=15, y_subdivisions=15, size=5)
target = bpy.context.view_layer.objects.active
target.name = "Meadow"

bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.3)
stem = bpy.context.view_layer.objects.active
stem.name = "Flower_Stem"
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0, 0.3))
head = bpy.context.view_layer.objects.active
head.name = "Flower_Head"
bpy.ops.object.select_all(action='DESELECT')
head.select_set(True)
stem.select_set(True)
bpy.context.view_layer.objects.active = stem
try:
    bpy.ops.object.join()
except RuntimeError:
    pass
flower = stem
flower.name = "Flower"

bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, subdivisions=1)
pebble = bpy.context.view_layer.objects.active
pebble.name = "Pebble"

bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.5, location=(0, 0, 0.25))
grass = bpy.context.view_layer.objects.active
grass.name = "Grass"

s = bpy.context.scene.scatter_settings
s.source_object = flower
s.target_object = target
s.count = 100
s.scale_min = 0.5
s.scale_max = 1.5
s.random_seed = 55

bpy.ops.scatter.source_add()
s.source_objects[0].object = pebble
s.source_objects[0].weight = 0.5
bpy.ops.scatter.source_add()
s.source_objects[1].object = grass
s.source_objects[1].weight = 2.0

bpy.ops.scatter.execute()

if not bpy.app.background:
    for area in getattr(bpy.context.screen, 'areas', []):
        if area.type == 'VIEW_3D':
            area.spaces[0].shading.type = 'MATERIAL'
            area.spaces[0].region_3d.view_distance = 6

print(f"Multi-source: 3 sources (flower:1, pebble:0.5, grass:2.0) → {s.count} instances")
