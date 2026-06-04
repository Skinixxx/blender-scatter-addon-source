import bpy
import os

tex_dir = r"C:\Users\skinix\cursach\textures"

files = [
    ("density_map.png", "DensityMap"),
    ("scale_map.png", "ScaleMap"),
    ("rotation_map.png", "RotationMap"),
    ("stripe_density.png", "StripeDensity"),
]

for filename, img_name in files:
    filepath = os.path.join(tex_dir, filename)
    if os.path.exists(filepath):
        if img_name in bpy.data.images:
            bpy.data.images.remove(bpy.data.images[img_name])
        img = bpy.data.images.load(filepath, check_existing=False)
        img.name = img_name
        print(f"Loaded: {img.name} ({img.size[0]}x{img.size[1]})")

blend_path = os.path.join(tex_dir, "textures_for_scatter.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"Saved to: {blend_path}")
