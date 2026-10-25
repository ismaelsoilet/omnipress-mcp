"""OmniPress Blender 3D Template: Waving 3D Silk Flag / Banner.

Generates a photorealistic 3D waving flag or banner with satin/silk fabric shaders,
harmonic cloth wave displacement, polished golden flagpole, studio lighting,
and transparent background. Works universally with any flag, logo, or banner texture.

Usage (invoked via Blender CLI):
    blender -b -P waving_flag.py -- --texture <path> --output <path> [options]
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

    parser = argparse.ArgumentParser(description="Render 3D Waving Silk Flag or Banner")
    parser.add_argument("--texture", required=True, help="Path to flag/banner texture image")
    parser.add_argument("--output", required=True, help="Path for rendered output PNG")
    parser.add_argument("--engine", default="BLENDER_EEVEE_NEXT", choices=["BLENDER_EEVEE_NEXT", "CYCLES"])
    parser.add_argument("--resolution", default="1920x1080", help="Render resolution (e.g. 1920x1080, 1080x1080)")
    parser.add_argument("--wave-height", type=float, default=0.18, help="Cloth wave height amplitude")
    parser.add_argument("--with-pole", action="store_true", default=True, help="Include golden flagpole")
    parser.add_argument("--samples", type=int, default=32, help="Render sample count")
    return parser.parse_args(args_to_parse)


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

    # 1. Create Flag Cloth Mesh (Grid with high subdivision)
    # Ratio: 2.4m width x 1.68m height (~10:7 standard flag ratio)
    flag_w = 2.4
    flag_h = 1.68
    subdiv_x = 120
    subdiv_y = 84

    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=subdiv_x,
        y_subdivisions=subdiv_y,
        size=1.0,
        location=(flag_w / 2.0 - 1.1, 0, 0),
    )
    flag = bpy.context.active_object
    flag.name = "FlagCloth"
    flag.scale = (flag_w, flag_h, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    # 2. Add Wave Modifiers for Natural Waving Cloth Simulation
    # Wave 1: Primary large horizontal wind wave
    wave1 = flag.modifiers.new(name="WindWavePrimary", type="WAVE")
    wave1.use_x = True
    wave1.use_y = False
    wave1.height = args.wave_height
    wave1.width = 0.95
    wave1.speed = 0.0
    wave1.time_offset = 2.8
    wave1.narrowness = 1.4

    # Wave 2: Harmonic secondary wave for organic cloth folds
    wave2 = flag.modifiers.new(name="WindWaveHarmonic", type="WAVE")
    wave2.use_x = True
    wave2.use_y = True
    wave2.height = args.wave_height * 0.55
    wave2.width = 0.55
    wave2.speed = 0.0
    wave2.time_offset = 6.0
    wave2.narrowness = 1.8

    # Smooth Shading and Subdivision Surface
    subsurf = flag.modifiers.new(name="Subsurf", type="SUBSURF")
    subsurf.levels = 1
    subsurf.render_levels = 2
    bpy.ops.object.shade_smooth()

    # 3. Satin/Silk Flag Fabric Material
    mat = bpy.data.materials.new(name="SilkFabric_Universal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_tex = nodes.new(type="ShaderNodeTexImage")

    abs_tex = os.path.abspath(args.texture)
    if os.path.exists(abs_tex):
        node_tex.image = bpy.data.images.load(abs_tex)
    else:
        print(f"[WARN] Flag texture not found at {abs_tex}")

    # Fabric parameters: rich satin sheen
    links.new(node_tex.outputs["Color"], node_bsdf.inputs["Base Color"])
    node_bsdf.inputs["Roughness"].default_value = 0.28
    node_bsdf.inputs["Metallic"].default_value = 0.08
    if "Sheen Weight" in node_bsdf.inputs:
        node_bsdf.inputs["Sheen Weight"].default_value = 0.95
        if "Sheen Roughness" in node_bsdf.inputs:
            node_bsdf.inputs["Sheen Roughness"].default_value = 0.25
    elif "Sheen" in node_bsdf.inputs:
        node_bsdf.inputs["Sheen"].default_value = 0.95

    links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])
    flag.data.materials.append(mat)

    # 4. Optional Golden Flagpole & Finial
    if args.with_pole:
        pole_mat = bpy.data.materials.new(name="GoldPole")
        pole_mat.use_nodes = True
        p_bsdf = pole_mat.node_tree.nodes.get("Principled BSDF")
        if p_bsdf:
            p_bsdf.inputs["Base Color"].default_value = (1.0, 0.78, 0.22, 1.0)
            p_bsdf.inputs["Metallic"].default_value = 1.0
            p_bsdf.inputs["Roughness"].default_value = 0.12

        # Vertical Pole (aligned with flag's local Y axis, right at left cloth edge)
        pole_x = -1.13
        pole_depth = flag_h * 1.40
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.032,
            depth=pole_depth,
            location=(pole_x, 0, 0),
        )
        pole = bpy.context.active_object
        pole.name = "FlagPole"
        pole.rotation_euler = (math.radians(90), 0, 0)
        bpy.ops.object.shade_smooth()
        pole.data.materials.append(pole_mat)
        pole.parent = flag

        # Top Gold Finial Sphere (at the very top crown of the flagpole)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.065,
            location=(pole_x, pole_depth / 2.0 + 0.03, 0),
        )
        finial = bpy.context.active_object
        finial.name = "PoleFinial"
        bpy.ops.object.shade_smooth()
        finial.data.materials.append(pole_mat)
        finial.parent = flag

        # Bottom Pole Cap Sphere
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.05,
            location=(pole_x, -pole_depth / 2.0 - 0.02, 0),
        )
        bottom_cap = bpy.context.active_object
        bottom_cap.name = "PoleBottomCap"
        bpy.ops.object.shade_smooth()
        bottom_cap.data.materials.append(pole_mat)
        bottom_cap.parent = flag

    # 5. Position & Angle of the Flag
    # Elegant dynamic perspective tilt
    flag.rotation_euler = (
        math.radians(82.0),
        math.radians(-3.0),
        math.radians(-16.0),
    )

    # 6. Studio Lighting Setup (Emphasizes Fabric Folds and Wave Crests)
    # Key Light (Warm, upper-front-left)
    key_data = bpy.data.lights.new(name="KeyLight", type="AREA")
    key_data.energy = 140.0
    key_data.size = 3.5
    key_data.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    coll.objects.link(key_obj)
    key_obj.location = (-2.0, -3.8, 2.5)
    key_obj.rotation_euler = (math.radians(45), math.radians(-20), math.radians(-25))

    # Fill Light (Soft cool fill, front-right)
    fill_data = bpy.data.lights.new(name="FillLight", type="AREA")
    fill_data.energy = 55.0
    fill_data.size = 4.5
    fill_data.color = (0.85, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    coll.objects.link(fill_obj)
    fill_obj.location = (3.2, -3.0, 1.2)
    fill_obj.rotation_euler = (math.radians(35), math.radians(25), math.radians(30))

    # Rim / Hair Light (Back-top rim creating silk glint on ripple edges)
    rim_data = bpy.data.lights.new(name="RimLight", type="SPOT")
    rim_data.energy = 220.0
    rim_data.spot_size = math.radians(75)
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    coll.objects.link(rim_obj)
    rim_obj.location = (0.5, 3.0, 2.6)
    rim_obj.rotation_euler = (math.radians(-50), 0, math.radians(180))

    # 7. Camera Setup (Full framing with elegant margins)
    cam_data = bpy.data.cameras.new(name="FlagCamera")
    cam_data.lens = 48
    cam_obj = bpy.data.objects.new("FlagCamera", cam_data)
    coll.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0.05, -4.6, 0.05)
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
    print(f"[OmniPress 3D] Setting up 3D Waving Flag scene with texture: {args.texture}")
    setup_scene(args)
    print(f"[OmniPress 3D] Rendering to {args.output} via {args.engine}...")
    bpy.ops.render.render(write_still=True)
    print(f"[OmniPress 3D] Render complete: {args.output}")


if __name__ == "__main__":
    main()
