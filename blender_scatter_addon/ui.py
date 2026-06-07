import bpy


class SCATTER_OT_source_add(bpy.types.Operator):
    bl_idname = "scatter.source_add"
    bl_label = "Add Source"
    bl_description = "Add current source object to multi-source list"

    def execute(self, context):
        settings = context.scene.scatter_settings
        item = settings.source_objects.add()
        item.object = settings.source_object
        item.weight = 1.0
        settings.source_index = len(settings.source_objects) - 1
        return {'FINISHED'}


class SCATTER_OT_source_remove(bpy.types.Operator):
    bl_idname = "scatter.source_remove"
    bl_label = "Remove Source"

    def execute(self, context):
        settings = context.scene.scatter_settings
        if settings.source_objects:
            settings.source_objects.remove(settings.source_index)
            settings.source_index = max(0, settings.source_index - 1)
        return {'FINISHED'}


class SCATTER_OT_preset_save(bpy.types.Operator):
    bl_idname = "scatter.preset_save"
    bl_label = "Save Preset"

    filename_ext = ".json"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        settings = context.scene.scatter_settings
        data = {
            "count": settings.count,
            "scale_min": settings.scale_min,
            "scale_max": settings.scale_max,
            "random_seed": settings.random_seed,
            "align_to_normal": settings.align_to_normal,
            "use_collection": settings.use_collection,
            "avoid_overlap": settings.avoid_overlap,
            "overlap_radius": settings.overlap_radius,
            "use_geometry_nodes": settings.use_geometry_nodes,
            "scatter_mode": settings.scatter_mode,
            "use_wind": settings.use_wind,
            "wind_strength": settings.wind_strength,
            "wind_direction": list(settings.wind_direction),
            "wind_frequency": settings.wind_frequency,
            "use_lod": settings.use_lod,
            "lod_decimate_ratio": settings.lod_decimate_ratio,
            "use_physics": settings.use_physics,
            "physics_drop_height": settings.physics_drop_height,
            "physics_friction": settings.physics_friction,
        }
        import json
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)
        self.report({'INFO'}, f"Preset saved: {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SCATTER_OT_preset_load(bpy.types.Operator):
    bl_idname = "scatter.preset_load"
    bl_label = "Load Preset"

    filename_ext = ".json"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        settings = context.scene.scatter_settings
        import json
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        for key, val in data.items():
            if hasattr(settings, key):
                setattr(settings, key, val)
        self.report({'INFO'}, f"Preset loaded: {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SCATTER_PT_main(bpy.types.Panel):
    bl_label = "Parametric Scatter"
    bl_idname = "SCATTER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Scatter"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.scatter_settings

        box = layout.box()
        box.label(text="Objects", icon='OBJECT_DATA')
        box.prop(settings, "source_object", text="Source")
        box.prop(settings, "target_object", text="Surface")

        row = box.row(align=True)
        row.operator("scatter.source_add", text="Add to Multi", icon='ADD')
        row.operator("scatter.source_remove", text="", icon='REMOVE')
        if settings.source_objects:
            box.template_list(
                "UI_UL_list",
                "sources",
                settings,
                "source_objects",
                settings,
                "source_index",
                rows=2,
            )

        box = layout.box()
        box.label(text="Mode", icon='MODIFIER')
        box.prop(settings, "scatter_mode", expand=True)

        box = layout.box()
        box.label(text="Texture Maps", icon='TEXTURE')
        box.prop(settings, "density_map", text="Density")
        box.prop(settings, "scale_map", text="Scale")
        box.prop(settings, "rotation_map", text="Rotation")

        box = layout.box()
        box.label(text="Parameters", icon='SETTINGS')
        box.prop(settings, "count")
        row = box.row(align=True)
        row.prop(settings, "scale_min")
        row.prop(settings, "scale_max")
        box.prop(settings, "random_seed")

        box = layout.box()
        box.prop(settings, "align_to_normal")
        box.prop(settings, "use_collection")

        box = layout.box()
        box.prop(settings, "use_geometry_nodes")
        box.prop(settings, "avoid_overlap")
        row = box.row(align=True)
        row.prop(settings, "overlap_radius")
        row.enabled = settings.avoid_overlap

        box = layout.box()
        box.label(text="Wind", icon='FORCE_WIND')
        box.prop(settings, "use_wind")
        if settings.use_wind:
            box.prop(settings, "wind_strength")
            box.prop(settings, "wind_direction")
            box.prop(settings, "wind_frequency")

        box = layout.box()
        box.label(text="LOD", icon='LOD')
        box.prop(settings, "use_lod")
        if settings.use_lod:
            box.prop(settings, "lod_decimate_ratio")

        box = layout.box()
        box.label(text="Physics", icon='PHYSICS')
        box.prop(settings, "use_physics")
        if settings.use_physics:
            box.prop(settings, "physics_drop_height")
            box.prop(settings, "physics_friction")

        box = layout.box()
        box.label(text="Presets", icon='PRESET')
        row = box.row(align=True)
        row.operator("scatter.preset_save", text="Save")
        row.operator("scatter.preset_load", text="Load")

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("scatter.execute", text="Scatter", icon='PARTICLES')
        row.operator("scatter.clear", text="Clear", icon='X')


classes = (
    SCATTER_OT_source_add,
    SCATTER_OT_source_remove,
    SCATTER_OT_preset_save,
    SCATTER_OT_preset_load,
    SCATTER_PT_main,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
