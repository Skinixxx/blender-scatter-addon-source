"""
Demo: Presets save/load
Run: blender --python demo_presets.py
"""
import sys, os, tempfile
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from blender_scatter_addon import register
register()

bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10, size=4)
target = bpy.context.active_object
target.name = "Terrain"

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12)
source = bpy.context.active_object
source.name = "Seed"

s = bpy.context.scene.scatter_settings
s.source_object = source
s.target_object = target
s.count = 80
s.scale_min = 0.3
s.scale_max = 2.0
s.random_seed = 123
s.align_to_normal = True
s.use_collection = True

preset_path = os.path.join(tempfile.gettempdir(), "scatter_preset_demo.json")
bpy.ops.scatter.preset_save(filepath=preset_path)

s.count = 999
s.scale_min = 9.9
print(f"Before load: count={s.count}, scale_min={s.scale_min}")

bpy.ops.scatter.preset_load(filepath=preset_path)
print(f"After load:  count={s.count}, scale_min={s.scale_min}")

bpy.ops.scatter.execute()
print(f"Preset demo: scattered {s.count} instances from saved preset")
