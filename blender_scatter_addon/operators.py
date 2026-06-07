import bpy
from .scatter_core import scatter_objects, clear_scatter


class SCATTER_OT_scatter(bpy.types.Operator):
    bl_idname = "scatter.execute"
    bl_label = "Scatter Objects"
    bl_description = "Scatter source object over target surface"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.scatter_settings
        if not settings.source_object:
            self.report({'ERROR'}, "No source object selected")
            return {'CANCELLED'}
        if not settings.target_object:
            self.report({'ERROR'}, "No target surface selected")
            return {'CANCELLED'}
        success = scatter_objects(settings)
        if not success:
            self.report({'ERROR'}, "Scattering failed")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Scattered {settings.count} instances")
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
                try:
                    area.spaces[0].region_3d.view_distance = max(
                        settings.target_object.dimensions.x,
                        settings.target_object.dimensions.y,
                        settings.target_object.dimensions.z,
                    ) * 2.5
                except AttributeError:
                    pass
        return {'FINISHED'}


class SCATTER_OT_clear(bpy.types.Operator):
    bl_idname = "scatter.clear"
    bl_label = "Clear Scatter"
    bl_description = "Remove all scattered instances"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.scatter_settings
        if settings.source_object:
            clear_scatter(settings.source_object.name)
            self.report({'INFO'}, "Scatter cleared")
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


classes = (
    SCATTER_OT_scatter,
    SCATTER_OT_clear,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
