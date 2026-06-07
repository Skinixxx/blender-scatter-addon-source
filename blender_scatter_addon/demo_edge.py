"""
Demo: Edge scatter
Run: blender --python demo_edge.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from blender_scatter_addon import register
register()

bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
bpy.ops.object.shade_smooth()
target = bpy.context.active_object
target.name = "Suzanne"

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08)
source = bpy.context.active_object
source.name = "Spike"

s = bpy.context.scene.scatter_settings
s.source_object = source
s.target_object = target
s.count = 120
s.scatter_mode = 'EDGE'
s.scale_min = 0.4
s.scale_max = 1.2
s.align_to_normal = True
s.random_seed = 77

bpy.ops.scatter.execute()

if not bpy.app.background:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].shading.type = 'MATERIAL'
            area.spaces[0].region_3d.view_distance = 5

print(f"Edge scatter: {s.count} spikes along edges of Suzanne")
