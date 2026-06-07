"""
Demo: LOD generation
Run: blender --python demo_lod.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from blender_scatter_addon import register
register()

bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10, size=4)
target = bpy.context.active_object
target.name = "Terrain"

bpy.ops.mesh.primitive_ico_sphere_add(radius=0.15, subdivisions=3)
source = bpy.context.active_object
source.name = "DetailRock"

s = bpy.context.scene.scatter_settings
s.source_object = source
s.target_object = target
s.count = 40
s.scale_min = 0.5
s.scale_max = 2.0
s.use_lod = True
s.lod_decimate_ratio = 0.2
s.random_seed = 11

bpy.ops.scatter.execute()

lod_objs = [o for o in bpy.data.objects if '_LOD' in o.name]
verts_before = len(source.data.vertices)
if lod_objs:
    verts_after = len(lod_objs[0].data.vertices)
    print(f"LOD demo: source={verts_before} verts → LOD={verts_after} verts (ratio={s.lod_decimate_ratio})")
    print(f"  LOD objects: {[o.name for o in lod_objs]}")
