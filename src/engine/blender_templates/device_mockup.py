"""OmniPress Blender 3D Template: Dynamic Device Mockup (Smartphone).

Generates a photorealistic 3D smartphone mockup with procedural chassis,
dynamic screen texture UV mapping, studio 3-point lighting, and transparent background.

Usage (invoked via Blender CLI):
    blender -b -P device_mockup.py -- --texture <path> --output <path> [options]
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
    # Everything after '--' is intended for this script
    argv = sys.argv
    if "--" in argv:
        args_to_parse = argv[argv.index("--") + 1 :]
    else:
        args_to_parse = []

    parser = argparse.ArgumentParser(description="Render 3D Smartphone Device Mockup")
    parser.add_argument("--texture", required=True, help="Path to image texture for the screen")
    parser.add_argument("--output", required=True, help="Path for rendered output PNG")
    parser.add_argument("--engine", default="BLENDER_EEVEE_NEXT", choices=["BLENDER_EEVEE_NEXT", "CYCLES"])
    parser.add_argument("--resolution", default="1080x1080", help="Render resolution (e.g. 1080x1080, 1920x1080)")
    parser.add_argument("--tilt-x", type=float, default=8.0, help="Device tilt angle in degrees (pitch)")
    parser.add_argument("--tilt-y", type=float, default=-10.0, help="Device tilt angle in degrees (yaw)")
    parser.add_argument("--chassis-color", default="0.08,0.09,0.11", help="RGB chassis color (0.0 to 1.0)")
    parser.add_argument("--samples", type=int, default=32, help="Render sample count")
    return parser.parse_args(args_to_parse)


def setup_scene(args):
    # 1. Reset to empty factory scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 2. Parse resolution
    res_w, res_h = map(int, args.resolution.split("x"))
    scene.render.resolution_x = res_w
    scene.render.resolution_y = res_h
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.engine = args.engine

    # Configure render samples
    if args.engine == "BLENDER_EEVEE_NEXT":
        if hasattr(scene, "eevee"):
            scene.eevee.taa_render_samples = args.samples
    elif args.engine == "CYCLES":
        scene.cycles.samples = args.samples

    # 3. Create Root Collection
    coll = bpy.context.collection

    # 4. Create Smartphone Body
    # Smartphone dimensions: approx 75mm x 150mm x 8mm -> in blender units: 0.75, 1.5, 0.08
    phone_w = 0.76
    phone_h = 1.56
    phone_d = 0.06

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    chassis = bpy.context.active_object
    chassis.name = "PhoneChassis"
    chassis.scale = (phone_w, phone_h, phone_d)
    bpy.ops.object.transform_apply(scale=True)

    # Add Bevel modifier for rounded edges
    bevel = chassis.modifiers.new(name="Bevel", type="BEVEL")
    bevel.width = 0.04
    bevel.segments = 5
    bpy.ops.object.shade_smooth()

    # Chassis Material (Dark Brushed Titanium / Matte Metal)
    rgb = [float(c) for c in args.chassis_color.split(",")]
    if len(rgb) == 3:
        rgb.append(1.0)
    chassis_mat = bpy.data.materials.new(name="ChassisMaterial")
    chassis_mat.use_nodes = True
    bsdf = chassis_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = tuple(rgb)
        bsdf.inputs["Metallic"].default_value = 0.9
        bsdf.inputs["Roughness"].default_value = 0.25
    chassis.data.materials.append(chassis_mat)

    # 5. Create Screen Plane
    # Screen is slightly smaller than chassis and raised by +0.031 in Z
    screen_w = phone_w - 0.05
    screen_h = phone_h - 0.06
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, phone_d / 2.0 + 0.002))
    screen = bpy.context.active_object
    screen.name = "PhoneScreen"
    screen.scale = (screen_w, screen_h, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    # Parent screen to chassis so they rotate together
    screen.parent = chassis

    # Screen Material with Texture
    screen_mat = bpy.data.materials.new(name="ScreenMaterial")
    screen_mat.use_nodes = True
    nodes = screen_mat.node_tree.nodes
    links = screen_mat.node_tree.links
    nodes.clear()

    # Material nodes: Texture -> Emission / Principled BSDF -> Material Output
    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_tex = nodes.new(type="ShaderNodeTexImage")

    abs_tex_path = os.path.abspath(args.texture)
    if os.path.exists(abs_tex_path):
        image = bpy.data.images.load(abs_tex_path)
        node_tex.image = image
    else:
        print(f"[WARN] Texture not found: {abs_tex_path}, using default blank")

    # Connect texture color to Base Color and slight Emission for vibrant screen glow
    links.new(node_tex.outputs["Color"], node_bsdf.inputs["Base Color"])
    if "Emission Color" in node_bsdf.inputs:
        links.new(node_tex.outputs["Color"], node_bsdf.inputs["Emission Color"])
        node_bsdf.inputs["Emission Strength"].default_value = 0.15
    node_bsdf.inputs["Roughness"].default_value = 0.08

    links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    screen.data.materials.append(screen_mat)

    # 6. Apply Device Tilt & Rotation (Facing front camera at Y=-3.2)
    rad_x = math.radians(90.0 + args.tilt_x)
    rad_y = math.radians(args.tilt_y)
    chassis.rotation_euler = (rad_x, 0, rad_y)

    # 7. Studio 3-Point Lighting Setup
    # Key Light (Warm, upper-front-left)
    key_data = bpy.data.lights.new(name="KeyLight", type="AREA")
    key_data.energy = 150.0
    key_data.size = 2.0
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    coll.objects.link(key_obj)
    key_obj.location = (-1.8, -2.5, 2.2)
    key_obj.rotation_euler = (math.radians(45), math.radians(-25), math.radians(-30))

    # Fill Light (Cool, right side)
    fill_data = bpy.data.lights.new(name="FillLight", type="AREA")
    fill_data.energy = 60.0
    fill_data.size = 2.5
    fill_data.color = (0.85, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    coll.objects.link(fill_obj)
    fill_obj.location = (2.2, -2.0, 1.0)
    fill_obj.rotation_euler = (math.radians(50), math.radians(35), math.radians(40))

    # Rim Light (Accent from behind for crisp edge highlights)
    rim_data = bpy.data.lights.new(name="RimLight", type="SPOT")
    rim_data.energy = 200.0
    rim_data.spot_size = math.radians(60)
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    coll.objects.link(rim_obj)
    rim_obj.location = (0.0, 2.2, 1.8)
    rim_obj.rotation_euler = (math.radians(-45), 0, math.radians(180))

    # 8. Setup Camera
    cam_data = bpy.data.cameras.new(name="StudioCamera")
    cam_data.lens = 75  # 75mm portrait/product lens for minimal distortion
    cam_obj = bpy.data.objects.new("StudioCamera", cam_data)
    coll.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0.0, -3.2, 0.1)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)

    # 9. Output Path
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    scene.render.filepath = os.path.abspath(args.output)


def main():
    if bpy is None:
        print("[ERROR] bpy not available. Must be run within Blender.")
        sys.exit(1)

    args = parse_args()
    print(f"[OmniPress 3D] Setting up device mockup scene with texture: {args.texture}")
    setup_scene(args)
    print(f"[OmniPress 3D] Rendering to {args.output} via {args.engine}...")
    bpy.ops.render.render(write_still=True)
    print(f"[OmniPress 3D] Render complete: {args.output}")


if __name__ == "__main__":
    main()
