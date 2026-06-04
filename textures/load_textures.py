"""Загрузи этот файл в Text Editor Blender (View3D → Text Editor) и нажми Run Script"""
import bpy
import os

tex_dir = r"C:\Users\skinix\cursach\textures"

maps = {
    "density": ("density_map.png", "DensityMap", "density_map"),
    "scale": ("scale_map.png", "ScaleMap", "scale_map"),
    "rotation": ("rotation_map.png", "RotationMap", "rotation_map"),
    "stripe_density": ("stripe_density.png", "StripeDensity", None),
}

for key, (filename, img_name, _) in maps.items():
    filepath = os.path.join(tex_dir, filename)
    if os.path.exists(filepath):
        if img_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[img_name])
        img = bpy.data.images.load(filepath, check_existing=False)
        img.name = img_name
        print(f"Loaded: {img.name} ({img.size[0]}x{img.size[1]})")

settings = bpy.context.scene.scatter_settings
settings.density_map = bpy.data.images.get("DensityMap")
settings.scale_map = bpy.data.images.get("ScaleMap")
settings.rotation_map = bpy.data.images.get("RotationMap")
print("Textures assigned to scatter settings!")

print("\nГотово! Текстуры загружены и привязаны к аддону.")
print("Нажми Scatter чтобы увидеть результат.")
