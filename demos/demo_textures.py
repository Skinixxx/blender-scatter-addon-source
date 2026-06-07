"""
Demo: scatter with texture maps (density, scale, rotation)
Run: blender --python demos/demo_textures.py
"""
import sys
import os
import struct
import random

import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import bpy

if "Cube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

from blender_scatter_addon import register, unregister
register()

bpy.ops.mesh.primitive_grid_add(x_subdivisions=32, y_subdivisions=32, size=8)
target = bpy.context.active_object
target.name = "Terrain"

mat = bpy.data.materials.new(name="TerrainMat")
mat.use_nodes = True
target.data.materials.append(mat)

bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.4)
stem = bpy.context.active_object
stem.name = "Grass_Stem"
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0, 0.4))
head = bpy.context.active_object
head.name = "Grass_Head"

bpy.ops.object.select_all(action='DESELECT')
head.select_set(True)
stem.select_set(True)
bpy.context.view_layer.objects.active = stem
bpy.ops.object.join()
grass = stem
grass.name = "Grass"

def _make_texture(name, width, height, pixel_gen):
    img = bpy.data.images.new(name, width=width, height=height, alpha=True)
    pixels = [0.0] * (width * height * 4)
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixel_gen(x, y, width, height)
            idx = (y * width + x) * 4
            pixels[idx] = r
            pixels[idx + 1] = g
            pixels[idx + 2] = b
            pixels[idx + 3] = a
    img.pixels = pixels
    img.pack()
    return img

def _density_pixel(x, y, w, h):
    cx, cy = w / 2, h / 2
    dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / (w / 2)
    val = max(0.0, 1.0 - dist * 0.8)
    return (val, val, val, 1.0)

def _scale_pixel(x, y, w, h):
    val = x / w
    return (val, val, val, 1.0)

def _rotation_pixel(x, y, w, h):
    val = y / h
    return (val, val, val, 1.0)

density_tex = _make_texture("DensityMap", 256, 256, _density_pixel)
scale_tex = _make_texture("ScaleMap", 256, 256, _scale_pixel)
rotation_tex = _make_texture("RotationMap", 256, 256, _rotation_pixel)

print(f"  Density map: {density_tex.name} ({density_tex.size[0]}x{density_tex.size[1]})")
print(f"  Scale map:   {scale_tex.name} ({scale_tex.size[0]}x{scale_tex.size[1]})")
print(f"  Rotation map:{rotation_tex.name} ({rotation_tex.size[0]}x{rotation_tex.size[1]})")

settings = bpy.context.scene.scatter_settings
settings.source_object = grass
settings.target_object = target
settings.count = 800
settings.scale_min = 0.5
settings.scale_max = 2.0
settings.random_seed = 42
settings.align_to_normal = True
settings.use_collection = True
settings.density_map = density_tex
settings.scale_map = scale_tex
settings.rotation_map = rotation_tex

bpy.ops.scatter.execute()

if bpy.app.background:
    print("(background mode — viewport setup skipped)")
else:
    for area in getattr(bpy.context.screen, 'areas', []):
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.region_3d.view_distance = 10
                    try:
                        space.region_3d.rotation_euler = (0.7, 0, 0.6)
                    except AttributeError:
                        pass

print("=== Demo textures complete ===")
print(f"Scattered {len([o for o in bpy.data.objects if 'instance' in o.name])} grass blades")
print("  Density: circular gradient (center dense)")
print("  Scale: horizontal gradient (small left, big right)")
print("  Rotation: vertical gradient (straight bottom, rotated top)")
