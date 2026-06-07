"""
Demo: Physics-based placement
Run: blender --python demo_physics.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
from blender_scatter_addon import register
register()

bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10, size=5)
target = bpy.context.view_layer.objects.active
target.name = "Ground"

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12)
pebble = bpy.context.view_layer.objects.active
pebble.name = "Pebble"
bpy.ops.object.shade_smooth()

bpy.ops.mesh.primitive_cube_add(size=0.15)
cube = bpy.context.view_layer.objects.active
cube.name = "Rock"

s = bpy.context.scene.scatter_settings
s.source_object = pebble
s.target_object = target
s.count = 30
s.scale_min = 0.5
s.scale_max = 1.2
s.use_physics = True
s.physics_drop_height = 3.0
s.physics_friction = 0.3
s.random_seed = 88

bpy.ops.scatter.execute()

# Add cube as second source
bpy.ops.scatter.source_add()
s.source_objects[0].object = cube
s.source_objects[0].weight = 0.5
s.use_physics = True
s.count = 50
bpy.ops.scatter.execute()

print(f"Physics demo: scattered with rigid body simulation")
print(f"  Drop height: {s.physics_drop_height}m, Friction: {s.physics_friction}")
