import bpy


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
        box.prop(settings, "avoid_overlap")
        row = box.row(align=True)
        row.prop(settings, "overlap_radius")
        row.enabled = settings.avoid_overlap

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("scatter.execute", text="Scatter", icon='PARTICLES')
        row.operator("scatter.clear", text="Clear", icon='X')


classes = (SCATTER_PT_main,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
