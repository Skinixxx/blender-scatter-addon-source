import numpy as np
import bpy
import bmesh
import mathutils
from mathutils import Vector
from mathutils import kdtree
import random
from typing import Optional, List

from .texture_utils import load_texture_as_grayscale, get_value_from_map


def _ensure_geometry_nodes():
    if not bpy.context.preferences.addons.get("geometry_nodes"):
        return False
    return True


def scatter_objects(settings) -> bool:
    source = settings.source_object
    target = settings.target_object

    if not source or not target:
        return False

    depsgraph = bpy.context.evaluated_depsgraph_get()
    target_eval = target.evaluated_get(depsgraph)

    mesh = bpy.data.meshes.new_from_object(target_eval, preserve_all_data_layers=True, depsgraph=depsgraph)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.faces.ensure_lookup_table()

    face_indices = list(range(len(bm.faces)))
    face_areas = [f.calc_area() for f in bm.faces]
    if sum(face_areas) == 0:
        bm.free()
        bpy.data.meshes.remove(mesh)
        return False

    density_tex = load_texture_as_grayscale(settings.density_map) if settings.density_map else None
    scale_tex = load_texture_as_grayscale(settings.scale_map) if settings.scale_map else None
    rotation_tex = load_texture_as_grayscale(settings.rotation_map) if settings.rotation_map else None

    rng = random.Random(settings.random_seed)

    count = settings.count

    chosen_faces = rng.choices(face_indices, weights=face_areas, k=count)

    collection_name = f"Scatter_{source.name}"
    if settings.use_collection:
        if collection_name in bpy.data.collections:
            scatter_col = bpy.data.collections[collection_name]
        else:
            scatter_col = bpy.data.collections.new(collection_name)
        if scatter_col.name not in bpy.context.collection.children:
            bpy.context.collection.children.link(scatter_col)
    else:
        scatter_col = None

    if not bpy.context.view_layer.objects.active:
        bm.free()
        bpy.data.meshes.remove(mesh)
        return False

    bm.faces.ensure_lookup_table()

    placed_positions: List[Vector] = []
    kd_overlap = kdtree.KDTree(count) if settings.avoid_overlap else None

    for idx, face_idx in enumerate(chosen_faces):
        face = bm.faces[face_idx]
        centroid = face.calc_center_median()
        normal = face.normal.copy()

        uv_layer = bm.loops.layers.uv.active
        u, v = 0.0, 0.0
        if uv_layer:
            for loop in face.loops:
                u += loop[uv_layer].uv.x
                v += loop[uv_layer].uv.y
            u /= len(face.loops)
            v /= len(face.loops)

        density_val = get_value_from_map(density_tex, u, v, 1.0)

        if density_val < rng.random():
            continue

        scale_val = get_value_from_map(scale_tex, u, v, 0.75)
        scale_factor = settings.scale_min + scale_val * (settings.scale_max - settings.scale_min)

        rot_val = get_value_from_map(rotation_tex, u, v, 0.5)
        rotation_angle = rot_val * 360.0

        loc = target.matrix_world @ Vector(centroid)

        # Collision detection: skip if too close to an existing instance
        if settings.avoid_overlap and kd_overlap is not None:
            if placed_positions:
                kd_overlap.balance()
                nearest, _, dist_sq = kd_overlap.find(loc)
                min_dist = settings.overlap_radius * settings.scale_max
                if nearest is not None and dist_sq < min_dist * min_dist:
                    continue
            kd_overlap.insert(loc, len(placed_positions))
            placed_positions.append(loc)

        inst = bpy.data.objects.new(
            f"{source.name}_instance_{idx:06d}",
            source.data,
        )

        inst.scale = Vector([scale_factor] * 3)

        if settings.align_to_normal:
            world_normal = target.matrix_world.to_3x3() @ Vector(normal)
            world_normal.normalize()
            up = Vector((0.0, 0.0, 1.0))
            if abs(world_normal.dot(up)) < 0.999:
                q = up.rotation_difference(world_normal)
                inst.rotation_mode = 'QUATERNION'
                inst.rotation_quaternion = q
            else:
                inst.rotation_mode = 'XYZ'
                inst.rotation_euler = (0.0, 0.0, 0.0)
                if world_normal.z < 0:
                    inst.rotation_euler.x = 3.14159
        else:
            inst.rotation_mode = 'XYZ'
            inst.rotation_euler = (0.0, 0.0, 0.0)

        loc_mat = mathutils.Matrix.Rotation(
            rotation_angle * 3.14159 / 180.0,
            4,
            'Z',
        )
        inst.matrix_world = loc_mat @ inst.matrix_world if settings.align_to_normal else loc_mat
        inst.matrix_world.translation = loc

        if scatter_col:
            scatter_col.objects.link(inst)
        else:
            bpy.context.collection.objects.link(inst)

    bm.free()
    bpy.data.meshes.remove(mesh)

    if scatter_col:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    return True


def clear_scatter(source_name: str):
    collection_name = f"Scatter_{source_name}"
    if collection_name in bpy.data.collections:
        col = bpy.data.collections[collection_name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
