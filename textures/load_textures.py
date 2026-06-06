"""Загрузи этот файл в Text Editor Blender (View3D → Text Editor) и нажми Run Script"""
import bpy
import os

tex_dir = r"C:\Users\skinix\cursach\textures"

maps = {
    "density": ("density_map.png", "DensityMap", "density_map"),
    "scale": ("scale_map.png", "ScaleMap", "scale_map"),
    "rotation": ("rotation_map.png", "RotationMap", "rotation_map"),
    "stripe_density": ("stripe_density.png", "StripeDensity", None),
    "checker_scale": ("checker_scale.png", "CheckerScale", None),
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

print("\n=== Текстуры загружены ===")
print("DensityMap  → hotspot в левом нижнем углу (там будет больше экземпляров)")
print("ScaleMap    → градиент: мелкие сверху-слева, крупные справа-внизу")
print("RotationMap → угол вокруг центра: 0° слева → 360° полный круг")
print("StripeDensity → полосы: чёрные/белые (вкл/выкл плотность)")
print("CheckerScale → шахматка: мелкие/крупные зоны")
print("\nНажми Scatter чтобы увидеть результат!")
