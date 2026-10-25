"""OmniPress Blender 3D Template: Kinetic 3D Typography.

Generates 3D extruded and beveled text geometry with studio lighting,
custom metallic/glossy materials, and transparent background.

Usage (invoked via Blender CLI):
    blender -b -P kinetic_title.py -- --text "OMNIPRESS" --output <path> [options]
"""

import argparse
import math
import os
import sys

try:
    import bpy
except ImportError:
    bpy = None


def parse_args():
    argv = sys.argv
    if "--" in argv:
        args_to_parse = argv[argv.index("--") + 1 :]
    else:
        args_to_parse = []

    parser = argparse.ArgumentParser(description="Render Kinetic 3D Title")
    parser.add_argument("--text", default="OMNIPRESS", help="Title string to render in 3D")
    parser.add_argument("--output", required=True, help="Path for rendered output PNG")
    parser.add_argument("--material", default="chrome", choices=["chrome", "gold", "neon_cyan", "obsidian"])
    parser.add_argument("--extrude", type=float, default=0.10, help="Extrusion depth")
    parser.add_argument("--bevel", type=float, default=0.02, help="Bevel depth")
    parser.add_argument("--tilt-x", type=float, default=10.0, help="Tilt angle X (pitch)")
    parser.add_argument("--tilt-y", type=float, default=-8.0, help="Tilt angle Y (yaw)")
    parser.add_argument("--engine", default="BLENDER_EEVEE_NEXT", choices=["BLENDER_EEVEE_NEXT", "CYCLES"])
    parser.add_argument("--resolution", default="1920x1080", help="Render resolution (e.g. 1920x1080)")
    parser.add_argument("--samples", type=int, default=32, help="Render sample count")
    return parser.parse_args(args_to_parse)


MATERIAL_CONFIGS = {
    "chrome": {
        "color": (0.95, 0.95, 0.98, 1.0),
        "metallic": 1.0,
        "roughness": 0.08,
        "emission": None,
    },
    "gold": {
        "color": (1.0, 0.78, 0.18, 1.0),
        "metallic": 1.0,
        "roughness": 0.15,
        "emission": None,
    },
    "neon_cyan": {
        "color": (0.05, 0.95, 1.0, 1.0),
        "metallic": 0.2,
        "roughness": 0.1,
        "emission": (0.0, 0.8, 1.0, 1.0),
    },
    "obsidian": {
        "color": (0.08, 0.08, 0.10, 1.0),
        "metallic": 0.5,
        "roughness": 0.1,
        "emission": None,
    },
}


def setup_scene(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    res_w, res_h = map(int, args.resolution.split("x"))
    scene.render.resolution_x = res_w
    scene.render.resolution_y = res_h
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.engine = args.engine

    if args.engine == "BLENDER_EEVEE_NEXT":
        if hasattr(scene, "eevee"):
            scene.eevee.taa_render_samples = args.samples
    elif args.engine == "CYCLES":
        scene.cycles.samples = args.samples

    coll = bpy.context.collection

    # 1. Create 3D Text Curve
    text_data = bpy.data.curves.new(name="TextData", type="FONT")
    text_data.body = args.text
    text_data.extrude = args.extrude
    text_data.bevel_depth = args.bevel
    text_data.bevel_resolution = 4
    text_data.align_x = "CENTER"
    text_data.align_y = "CENTER"
    text_data.size = 1.0

    text_obj = bpy.data.objects.new("TextObject", text_data)
    coll.objects.link(text_obj)
    text_obj.location = (0, 0, 0)

    # Apply tilt rotation
    text_obj.rotation_euler = (
        math.radians(90.0 + args.tilt_x),
        0,
        math.radians(args.tilt_y),
    )

    # 2. Material
    mat_cfg = MATERIAL_CONFIGS.get(args.material, MATERIAL_CONFIGS["chrome"])
    text_mat = bpy.data.materials.new(name=f"Mat_{args.material}")
    text_mat.use_nodes = True
    bsdf = text_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = mat_cfg["color"]
        bsdf.inputs["Metallic"].default_value = mat_cfg["metallic"]
        bsdf.inputs["Roughness"].default_value = mat_cfg["roughness"]
        if mat_cfg["emission"] and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = mat_cfg["emission"]
            bsdf.inputs["Emission Strength"].default_value = 0.8

    text_obj.data.materials.append(text_mat)

    # 3. Studio Lighting (Dramatic side highlights)
    key_data = bpy.data.lights.new(name="KeyLight", type="AREA")
    key_data.energy = 140.0
    key_data.size = 4.0
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    coll.objects.link(key_obj)
    key_obj.location = (-3.0, -3.0, 2.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(-25), math.radians(-35))

    fill_data = bpy.data.lights.new(name="FillLight", type="AREA")
    fill_data.energy = 60.0
    fill_data.size = 4.0
    fill_data.color = (0.80, 0.90, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    coll.objects.link(fill_obj)
    fill_obj.location = (3.5, -2.5, 1.5)
    fill_obj.rotation_euler = (math.radians(45), math.radians(30), math.radians(40))

    rim_data = bpy.data.lights.new(name="RimLight", type="SPOT")
    rim_data.energy = 220.0
    rim_data.spot_size = math.radians(65)
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    coll.objects.link(rim_obj)
    rim_obj.location = (0.0, 3.0, 2.5)
    rim_obj.rotation_euler = (math.radians(-50), 0, math.radians(180))

    # 4. Camera (Position scaled according to text length)
    char_count = max(len(args.text), 4)
    cam_dist = max(4.0, char_count * 1.1)
    cam_data = bpy.data.cameras.new(name="TextCamera")
    cam_data.lens = 50  # 50mm lens for wider field of view
    cam_obj = bpy.data.objects.new("TextCamera", cam_data)
    coll.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0.0, -cam_dist, 0.1)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    scene.render.filepath = os.path.abspath(args.output)


def main():
    if bpy is None:
        print("[ERROR] bpy not available. Must be run within Blender.")
        sys.exit(1)

    args = parse_args()
    print(f"[OmniPress 3D] Setting up 3D text scene: '{args.text}' ({args.material})")
    setup_scene(args)
    print(f"[OmniPress 3D] Rendering to {args.output} via {args.engine}...")
    bpy.ops.render.render(write_still=True)
    print(f"[OmniPress 3D] Render complete: {args.output}")


if __name__ == "__main__":
    main()
