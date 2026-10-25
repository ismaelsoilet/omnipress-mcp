"""OmniPress Blender 3D Template: Rotating Coin / Badge.

Generates an embossed 3D coin or medallion with metallic shader,
beveled rim, studio 3-point lighting, and transparent background.

Usage (invoked via Blender CLI):
    blender -b -P rotating_badge.py -- --output <path> [options]
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

    parser = argparse.ArgumentParser(description="Render 3D Rotating Badge or Coin")
    parser.add_argument("--output", required=True, help="Path for rendered output PNG")
    parser.add_argument("--texture", default="", help="Optional face emblem/texture path")
    parser.add_argument("--material", default="gold", choices=["gold", "silver", "bronze", "obsidian"])
    parser.add_argument("--rotation-y", type=float, default=25.0, help="Rotation Y angle in degrees (spin)")
    parser.add_argument("--tilt-x", type=float, default=12.0, help="Tilt X angle in degrees (pitch)")
    parser.add_argument("--engine", default="BLENDER_EEVEE_NEXT", choices=["BLENDER_EEVEE_NEXT", "CYCLES"])
    parser.add_argument("--resolution", default="1080x1080", help="Render resolution (e.g. 1080x1080)")
    parser.add_argument("--samples", type=int, default=32, help="Render sample count")
    return parser.parse_args(args_to_parse)


MATERIAL_PRESETS = {
    "gold": {
        "color": (1.0, 0.76, 0.15, 1.0),
        "metallic": 1.0,
        "roughness": 0.18,
    },
    "silver": {
        "color": (0.92, 0.93, 0.95, 1.0),
        "metallic": 1.0,
        "roughness": 0.15,
    },
    "bronze": {
        "color": (0.80, 0.49, 0.20, 1.0),
        "metallic": 0.95,
        "roughness": 0.28,
    },
    "obsidian": {
        "color": (0.05, 0.05, 0.06, 1.0),
        "metallic": 0.3,
        "roughness": 0.08,
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

    # 1. Create Coin Geometry (Cylinder with bevel)
    radius = 1.0
    depth = 0.14
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=radius,
        depth=depth,
        location=(0, 0, 0),
    )
    coin = bpy.context.active_object
    coin.name = "BadgeCoin"

    # Add Bevel Modifier
    bevel = coin.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.03
    bevel.segments = 4
    bpy.ops.object.shade_smooth()

    # Apply Materials
    mat_preset = MATERIAL_PRESETS.get(args.material, MATERIAL_PRESETS["gold"])
    coin_mat = bpy.data.materials.new(name=f"Mat_{args.material}")
    coin_mat.use_nodes = True
    bsdf = coin_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = mat_preset["color"]
        bsdf.inputs["Metallic"].default_value = mat_preset["metallic"]
        bsdf.inputs["Roughness"].default_value = mat_preset["roughness"]

    coin.data.materials.append(coin_mat)

    # Optional emblem texture on face
    if args.texture and os.path.exists(args.texture):
        # Create thin face disk
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=64,
            radius=radius * 0.88,
            depth=0.005,
            location=(0, 0, depth / 2.0 + 0.003),
        )
        face_disk = bpy.context.active_object
        face_disk.name = "FaceEmblem"
        face_disk.parent = coin

        face_mat = bpy.data.materials.new(name="EmblemMat")
        face_mat.use_nodes = True
        nodes = face_mat.node_tree.nodes
        links = face_mat.node_tree.links
        nodes.clear()

        node_out = nodes.new(type="ShaderNodeOutputMaterial")
        node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        node_tex = nodes.new(type="ShaderNodeTexImage")
        image = bpy.data.images.load(os.path.abspath(args.texture))
        node_tex.image = image

        links.new(node_tex.outputs["Color"], node_bsdf.inputs["Base Color"])
        node_bsdf.inputs["Roughness"].default_value = 0.15
        node_bsdf.inputs["Metallic"].default_value = 0.5
        links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])
        face_disk.data.materials.append(face_mat)

    # 2. Apply Rotations (Euler angles)
    coin.rotation_euler = (
        math.radians(90.0 + args.tilt_x),
        0,
        math.radians(args.rotation_y),
    )

    # 3. Studio 3-Point Lighting
    key_data = bpy.data.lights.new(name="KeyLight", type="AREA")
    key_data.energy = 120.0
    key_data.size = 2.0
    key_data.color = (1.0, 0.98, 0.92)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    coll.objects.link(key_obj)
    key_obj.location = (-2.0, -2.5, 2.0)
    key_obj.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-30))

    fill_data = bpy.data.lights.new(name="FillLight", type="AREA")
    fill_data.energy = 50.0
    fill_data.size = 2.5
    fill_data.color = (0.85, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    coll.objects.link(fill_obj)
    fill_obj.location = (2.2, -1.8, 1.2)
    fill_obj.rotation_euler = (math.radians(45), math.radians(30), math.radians(35))

    rim_data = bpy.data.lights.new(name="RimLight", type="SPOT")
    rim_data.energy = 180.0
    rim_data.spot_size = math.radians(55)
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    coll.objects.link(rim_obj)
    rim_obj.location = (0.0, 2.5, 2.0)
    rim_obj.rotation_euler = (math.radians(-50), 0, math.radians(180))

    # 4. Camera Setup
    cam_data = bpy.data.cameras.new(name="CoinCamera")
    cam_data.lens = 75
    cam_obj = bpy.data.objects.new("CoinCamera", cam_data)
    coll.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0.0, -5.2, 0.0)
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
    print(f"[OmniPress 3D] Setting up coin/badge scene ({args.material})")
    setup_scene(args)
    print(f"[OmniPress 3D] Rendering to {args.output} via {args.engine}...")
    bpy.ops.render.render(write_still=True)
    print(f"[OmniPress 3D] Render complete: {args.output}")


if __name__ == "__main__":
    main()
