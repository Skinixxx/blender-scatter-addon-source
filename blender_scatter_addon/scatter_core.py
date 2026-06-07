import math
import random
import json
import os
from typing import Optional, List

import numpy as np
import bpy
import bmesh
import mathutils
from mathutils import Vector, kdtree

from .texture_utils import load_texture_as_grayscale, get_value_from_map


def _pick_source(settings):
    if settings.source_objects:
        sources = [(s.object, s.weight) for s in settings.source_objects if s.object]
        if sources:
            objs, weights = zip(*sources)
            return random.Random(settings.random_seed).choices(objs, weights=weights, k=1)[0]
    return settings.source_object


def _ensure_geometry_nodes():
    if bpy.app.version >= (3, 0, 0):
        return True
    return bool(bpy.context.preferences.addons.get("geometry_nodes"))


def _scatter_gn(target, source, settings):
    group = bpy.data.node_groups.new(name=".ScatterGN", type='GeometryNodeTree')

    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')

    if settings.scatter_mode == 'FACE':
        total_area = sum(f.area for f in target.data.polygons) if target.data.polygons else 1.0
        mode = 'POISSON' if settings.avoid_overlap else 'RANDOM'

        count_val = group.nodes.new('ShaderNodeValue')
        count_val.outputs[0].default_value = float(settings.count)

        area_val = group.nodes.new('ShaderNodeValue')
        area_val.outputs[0].default_value = total_area

        density = group.nodes.new('ShaderNodeMath')
        density.operation = 'DIVIDE'
        group.links.new(count_val.outputs[0], density.inputs[0])
        group.links.new(area_val.outputs[0], density.inputs[1])

        distribute = group.nodes.new('GeometryNodeDistributePointsOnFaces')
        distribute.distribute_method = mode
        distribute.inputs[distribute.inputs.find('Seed')].default_value = settings.random_seed
        group.links.new(
            input_node.outputs['Geometry'],
            distribute.inputs[distribute.inputs.find('Mesh')],
        )
        group.links.new(
            density.outputs[0],
            distribute.inputs[distribute.inputs.find('Density')],
        )

        instance = group.nodes.new('GeometryNodeInstanceOnPoints')
        group.links.new(distribute.outputs['Points'], instance.inputs['Points'])
    else:
        mesh_line = group.nodes.new('GeometryNodeMeshToPoints')
        group.links.new(input_node.outputs['Geometry'], mesh_line.inputs['Mesh'])
        instance = group.nodes.new('GeometryNodeInstanceOnPoints')
        group.links.new(mesh_line.outputs['Points'], instance.inputs['Points'])

    obj_info = group.nodes.new('GeometryNodeObjectInfo')
    obj_info.transform_space = 'ORIGINAL'
    obj_info.inputs['Object'].default_value = source
    group.links.new(obj_info.outputs['Geometry'], instance.inputs['Instance'])

    rand_scale = group.nodes.new('FunctionNodeRandomValue')
    rand_scale.data_type = 'FLOAT_VECTOR'
    rand_scale.inputs['Min'].default_value = (settings.scale_min,) * 3
    rand_scale.inputs['Max'].default_value = (settings.scale_max,) * 3
    group.links.new(rand_scale.outputs['Value'], instance.inputs['Scale'])

    rand_rot = group.nodes.new('FunctionNodeRandomValue')
    rand_rot.data_type = 'FLOAT_VECTOR'
    rand_rot.inputs['Min'].default_value = (0.0, 0.0, 0.0)
    rand_rot.inputs['Max'].default_value = (0.0, 0.0, math.radians(360.0))
    group.links.new(rand_rot.outputs['Value'], instance.inputs['Rotation'])

    group.links.new(instance.outputs['Instances'], output_node.inputs['Geometry'])

    mod = target.modifiers.new(name="Scatter (GN)", type='NODES')
    mod.node_group = group
    return True


def _add_wind_gn(target, settings):
    group = bpy.data.node_groups.new(name=".WindGN", type='GeometryNodeTree')

    group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    input_node = group.nodes.new('NodeGroupInput')
    output_node = group.nodes.new('NodeGroupOutput')

    scene_time = group.nodes.new('GeometryNodeInputSceneTime')

    phase = group.nodes.new('ShaderNodeMath')
    phase.operation = 'MULTIPLY'
    phase.inputs[1].default_value = settings.wind_frequency
    group.links.new(scene_time.outputs['Seconds'], phase.inputs[0])

    sine = group.nodes.new('ShaderNodeMath')
    sine.operation = 'SINE'
    group.links.new(phase.outputs[0], sine.inputs[0])

    strength = group.nodes.new('ShaderNodeMath')
    strength.operation = 'MULTIPLY'
    strength.inputs[1].default_value = settings.wind_strength * 0.2
    group.links.new(sine.outputs[0], strength.inputs[0])

    dir_scale = group.nodes.new('ShaderNodeVectorMath')
    dir_scale.operation = 'SCALE'
    dir_scale.inputs['Vector'].default_value = list(settings.wind_direction)
    group.links.new(strength.outputs[0], dir_scale.inputs['Scale'])

    set_pos = group.nodes.new('GeometryNodeSetPosition')
    group.links.new(input_node.outputs['Geometry'], set_pos.inputs['Geometry'])
    group.links.new(dir_scale.outputs['Vector'], set_pos.inputs['Offset'])
    group.links.new(set_pos.outputs['Geometry'], output_node.inputs['Geometry'])

    mod = target.modifiers.new(name="Wind", type='NODES')
    mod.node_group = group
    return True


def _create_lod(source, ratio):
    lod_obj = bpy.data.objects.new("_LOD_TMP", source.data.copy())
    bpy.context.scene.collection.objects.link(lod_obj)
    mod = lod_obj.modifiers.new(name="Decimate", type='DECIMATE')
    mod.ratio = ratio
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = lod_obj.evaluated_get(depsgraph)
    result = bpy.data.meshes.new_from_object(eval_obj, preserve_all_data_layers=True, depsgraph=depsgraph)
    result.name = f"{source.data.name}_LOD"
    bpy.data.objects.remove(lod_obj, do_unlink=True)
    lod_ref = bpy.data.objects.new(f"{source.name}_LOD", result)
    bpy.context.scene.collection.objects.link(lod_ref)
    lod_ref.hide_viewport = True
    lod_ref.hide_render = True
    return result


def scatter_objects(settings) -> bool:
    source = settings.source_object
    if settings.source_objects:
        source = _pick_source(settings)
    target = settings.target_object

    if not source or not target:
        return False

    wm = bpy.context.window_manager
    wm.progress_begin(0, settings.count)

    if settings.use_geometry_nodes and _ensure_geometry_nodes():
        _clear_gn_modifier(target)
        result = _scatter_gn(target, source, settings)
        if result and settings.use_wind:
            _add_wind_gn(target, settings)
        wm.progress_end()
        return result

    depsgraph = bpy.context.evaluated_depsgraph_get()
    target_eval = target.evaluated_get(depsgraph)

    mesh = bpy.data.meshes.new_from_object(
        target_eval, preserve_all_data_layers=True, depsgraph=depsgraph
    )
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.faces.ensure_lookup_table()

    if settings.scatter_mode == 'EDGE':
        bm.edges.ensure_lookup_table()
        edge_indices = list(range(len(bm.edges)))
        if not edge_indices:
            bm.free()
            bpy.data.meshes.remove(mesh)
            return False
        chosen_edges = random.Random(settings.random_seed).choices(edge_indices, k=settings.count)
    else:
        face_indices = list(range(len(bm.faces)))
        face_areas = [f.calc_area() for f in bm.faces]
        if sum(face_areas) == 0:
            bm.free()
            bpy.data.meshes.remove(mesh)
            return False
        chosen_faces = random.Random(settings.random_seed).choices(
            face_indices, weights=face_areas, k=settings.count
        )

    density_tex = load_texture_as_grayscale(settings.density_map) if settings.density_map else None
    scale_tex = load_texture_as_grayscale(settings.scale_map) if settings.scale_map else None
    rotation_tex = (
        load_texture_as_grayscale(settings.rotation_map) if settings.rotation_map else None
    )

    rng = random.Random(settings.random_seed)

    if settings.use_lod:
        lod_mesh = _create_lod(source, settings.lod_decimate_ratio)
        instance_mesh = lod_mesh
    else:
        lod_mesh = None
        instance_mesh = source.data

    collection_name = f"Scatter_{source.name}"
    if settings.use_collection:
        if collection_name in bpy.data.collections:
            scatter_col = bpy.data.collections[collection_name]
        else:
            scatter_col = bpy.data.collections.new(collection_name)
        master = bpy.context.scene.collection
        if scatter_col.name not in master.children:
            master.children.link(scatter_col)
    else:
        scatter_col = None

    if not bpy.context.view_layer.objects.active:
        bpy.context.view_layer.objects.active = source or target
    if not bpy.context.view_layer.objects.active:
        bm.free()
        bpy.data.meshes.remove(mesh)
        return False

    placed_positions: List[Vector] = []
    kd_overlap = kdtree.KDTree(settings.count) if settings.avoid_overlap else None
    placed_objects: List = []

    for idx in range(settings.count):
        wm.progress_update(idx)

        if settings.scatter_mode == 'EDGE':
            edge = bm.edges[chosen_edges[idx]]
            t = rng.random()
            v1 = edge.verts[0].co
            v2 = edge.verts[1].co
            centroid = v1.lerp(v2, t)
            normal = (edge.verts[0].normal + edge.verts[1].normal).normalized()
            uv_layer = bm.loops.layers.uv.active
            u, v = 0.0, 0.0
            if uv_layer:
                for loop in edge.link_loops:
                    u += loop[uv_layer].uv.x
                    v += loop[uv_layer].uv.y
                n = len(edge.link_loops)
                if n:
                    u /= n
                    v /= n
        else:
            face = bm.faces[chosen_faces[idx]]
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
            instance_mesh,
        )
        inst.scale = [scale_factor] * 3

        if settings.align_to_normal:
            world_normal = target.matrix_world.to_3x3() @ Vector(normal)
            world_normal.normalize()
            up = Vector((0.0, 0.0, 1.0))
            dot = world_normal.dot(up)
            if abs(dot) < 0.999:
                q = up.rotation_difference(world_normal)
                inst.rotation_mode = 'QUATERNION'
                inst.rotation_quaternion = q
            else:
                inst.rotation_mode = 'XYZ'
                inst.rotation_euler = (math.pi if dot < 0 else 0.0, 0.0, 0.0)
        else:
            inst.rotation_mode = 'XYZ'
            inst.rotation_euler = (0.0, 0.0, 0.0)

        loc_mat = mathutils.Matrix.Rotation(math.radians(rotation_angle), 4, 'Z')
        inst.matrix_world = loc_mat @ inst.matrix_world
        inst.matrix_world.translation = loc
        inst.scale = [scale_factor] * 3

        if scatter_col:
            scatter_col.objects.link(inst)
        else:
            bpy.context.scene.collection.objects.link(inst)

        placed_objects.append(inst)

    bm.free()
    bpy.data.meshes.remove(mesh)

    if settings.use_physics and placed_objects:
        _apply_physics(placed_objects, settings)

    if settings.use_wind and placed_objects:
        for obj in placed_objects:
            _add_wind_gn(obj, settings)

    bpy.context.view_layer.objects.active = target
    target.select_set(True)

    screen = bpy.context.screen
    if screen:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    wm.progress_end()
    return True


def _apply_physics(objects, settings):
    if not bpy.context.scene.rigidbody_world:
        try:
            bpy.ops.rigidbody.world_add()
        except RuntimeError:
            return
    rb_world = bpy.context.scene.rigidbody_world
    rb_world.enabled = True

    for obj in objects:
        obj.location.z += settings.physics_drop_height
        bpy.context.view_layer.objects.active = obj
        try:
            bpy.ops.rigidbody.object_add()
        except RuntimeError:
            continue
        obj.rigid_body.type = 'ACTIVE'
        obj.rigid_body.friction = settings.physics_friction
        obj.rigid_body.collision_shape = 'CONVEX_HULL'

    try:
        bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
    except RuntimeError:
        return
    ground = bpy.context.view_layer.objects.active
    ground.name = "_physics_ground"
    try:
        bpy.ops.rigidbody.object_add()
    except RuntimeError:
        bpy.data.objects.remove(ground, do_unlink=True)
        return
    ground.rigid_body.type = 'PASSIVE'
    ground.rigid_body.friction = settings.physics_friction

    for frame in range(1, 60):
        bpy.context.scene.frame_set(frame)

    for obj in objects:
        if obj.rigid_body:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_remove()
        obj.location.z -= settings.physics_drop_height

    if ground.name in bpy.data.objects:
        bpy.data.objects.remove(ground, do_unlink=True)
    rb_world.enabled = False


def _clear_gn_modifier(target):
    for mod in list(target.modifiers):
        if mod.type == 'NODES' and mod.node_group:
            name = mod.node_group.name
            if name.startswith(".ScatterGN") or name.startswith(".WindGN"):
                node_group = mod.node_group
                target.modifiers.remove(mod)
                if node_group:
                    bpy.data.node_groups.remove(node_group)


def clear_scatter(source_name: str):
    collection_name = f"Scatter_{source_name}"
    if collection_name in bpy.data.collections:
        col = bpy.data.collections[collection_name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

    prefix = f"{source_name}_instance_"
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            _clear_gn_modifier(obj)

    for lod_obj in list(bpy.data.objects):
        if lod_obj.name.endswith("_LOD"):
            bpy.data.objects.remove(lod_obj, do_unlink=True)
