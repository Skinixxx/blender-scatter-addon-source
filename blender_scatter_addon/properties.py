import bpy
import json
import os


class ScatterSourceItem(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH',
    )
    weight: bpy.props.FloatProperty(
        name="Weight",
        default=1.0,
        min=0.01,
        max=100.0,
    )


class ScatterSettings(bpy.types.PropertyGroup):
    source_object: bpy.props.PointerProperty(
        name="Source Object",
        description="Object to scatter",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH',
    )

    target_object: bpy.props.PointerProperty(
        name="Target Surface",
        description="Surface to scatter onto",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH',
    )

    source_objects: bpy.props.CollectionProperty(
        type=ScatterSourceItem,
    )
    source_index: bpy.props.IntProperty(default=0)

    scatter_mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('FACE', "Face", "Scatter across faces"),
            ('EDGE', "Edge", "Scatter along edges"),
        ],
        default='FACE',
    )

    density_map: bpy.props.PointerProperty(
        name="Density Map",
        description="Texture controlling placement density (white=dense, black=sparse)",
        type=bpy.types.Image,
    )

    scale_map: bpy.props.PointerProperty(
        name="Scale Map",
        description="Texture controlling scale (white=100%, black=0%)",
        type=bpy.types.Image,
    )

    rotation_map: bpy.props.PointerProperty(
        name="Rotation Map",
        description="Texture controlling rotation (white=360deg, black=0deg)",
        type=bpy.types.Image,
    )

    count: bpy.props.IntProperty(
        name="Count",
        description="Number of instances to scatter",
        default=100,
        min=1,
        max=100000,
    )

    scale_min: bpy.props.FloatProperty(
        name="Scale Min",
        description="Minimum scale factor",
        default=0.5,
        min=0.01,
        max=10.0,
    )

    scale_max: bpy.props.FloatProperty(
        name="Scale Max",
        description="Maximum scale factor",
        default=2.0,
        min=0.01,
        max=10.0,
    )

    random_seed: bpy.props.IntProperty(
        name="Seed",
        description="Random seed for reproducibility",
        default=0,
        min=0,
        max=999999,
    )

    align_to_normal: bpy.props.BoolProperty(
        name="Align to Normal",
        description="Rotate instances to align with surface normal",
        default=True,
    )

    use_collection: bpy.props.BoolProperty(
        name="Use Collection",
        description="Create instances as collection for better performance",
        default=True,
    )

    avoid_overlap: bpy.props.BoolProperty(
        name="Avoid Overlap",
        description="Skip instances that would overlap with existing ones",
        default=False,
    )

    overlap_radius: bpy.props.FloatProperty(
        name="Overlap Radius",
        description="Minimum distance between instances (multiples of max scale)",
        default=0.5,
        min=0.1,
        max=5.0,
    )

    use_geometry_nodes: bpy.props.BoolProperty(
        name="Use Geometry Nodes",
        description="Use Geometry Nodes modifier for non-destructive scattering",
        default=False,
    )

    use_wind: bpy.props.BoolProperty(
        name="Wind Animation",
        description="Add wind animation to scattered instances",
        default=False,
    )

    wind_strength: bpy.props.FloatProperty(
        name="Wind Strength",
        default=0.3,
        min=0.0,
        max=5.0,
    )

    wind_direction: bpy.props.FloatVectorProperty(
        name="Wind Direction",
        default=(1.0, 0.0, 0.0),
        size=3,
        subtype='DIRECTION',
    )

    wind_frequency: bpy.props.FloatProperty(
        name="Wind Frequency",
        default=1.0,
        min=0.1,
        max=20.0,
    )

    use_lod: bpy.props.BoolProperty(
        name="Use LOD",
        description="Generate level-of-detail meshes for instances",
        default=False,
    )

    lod_decimate_ratio: bpy.props.FloatProperty(
        name="LOD Decimate",
        description="Decimation ratio for LOD levels",
        default=0.5,
        min=0.1,
        max=0.9,
    )

    use_physics: bpy.props.BoolProperty(
        name="Physics Placement",
        description="Use rigid body physics for natural placement",
        default=False,
    )

    physics_drop_height: bpy.props.FloatProperty(
        name="Drop Height",
        default=2.0,
        min=0.1,
        max=50.0,
    )

    physics_friction: bpy.props.FloatProperty(
        name="Friction",
        default=0.5,
        min=0.0,
        max=1.0,
    )

    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        default="My Preset",
    )


classes = (ScatterSourceItem, ScatterSettings,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.scatter_settings = bpy.props.PointerProperty(type=ScatterSettings)


def unregister():
    del bpy.types.Scene.scatter_settings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
