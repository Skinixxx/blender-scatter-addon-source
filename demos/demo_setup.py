"""
Demo setup script - run with: blender --python demo_setup.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import bpy

# Remove default cube
if "Cube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

# Register addon
from blender_scatter_addon import register, unregister
register()

# Create target surface
bpy.ops.mesh.primitive_grid_add(x_subdivisions=20, y_subdivisions=20, size=6)
target = bpy.context.active_object
target.name = "Terrain"

# Add a simple material to target
mat = bpy.data.materials.new(name="TerrainMat")
mat.use_nodes = True
target.data.materials.append(mat)

# Create source object - a simple flower/tree shape
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=0.3)
stem = bpy.context.active_object
stem.name = "Plant_Stem"
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, 0.3))
head = bpy.context.active_object
head.name = "Plant_Head"

bpy.ops.object.select_all(action='DESELECT')
head.select_set(True)
stem.select_set(True)
bpy.context.view_layer.objects.active = stem
bpy.ops.object.join()
plant = stem
plant.name = "Plant"

# Create scatter settings
settings = bpy.context.scene.scatter_settings
settings.source_object = plant
settings.target_object = target
settings.count = 150
settings.scale_min = 0.6
settings.scale_max = 1.8
settings.random_seed = 123
settings.align_to_normal = True
settings.use_collection = True

# Execute scatter
bpy.ops.scatter.execute()

# Set up viewport (skip in background mode)
if bpy.app.background:
    print("(background mode — viewport setup skipped)")
else:
    for area in getattr(bpy.context.screen, 'areas', []):
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.region_3d.view_distance = 8
                    try:
                        space.region_3d.rotation_euler = (0.8, 0, 0.5)
                    except AttributeError:
                        pass

print("=== Demo setup complete ===")
print(f"Scattered {settings.count} plants on terrain")
