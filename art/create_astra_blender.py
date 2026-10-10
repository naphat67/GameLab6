"""Build Astra MK-06 as a Blender scene and export a rigged GLB for Godot."""
import bpy
import math
from mathutils import Euler, Vector
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLEND_OUT = ROOT / "assets" / "characters" / "source_blender" / "Astra_MK06.blend"
GLB_OUT = ROOT / "assets" / "characters" / "Astra_MK06.glb"
RENDER_OUT = ROOT / "art" / "astra_blender_render.png"
BLEND_OUT.parent.mkdir(parents=True, exist_ok=True)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def material(name, color, metallic=0.0, roughness=0.4, emission=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 1.2
    return mat


MATS = {
    "Armor": material("Ceramic / midnight blue", (0.105, 0.17, 0.28), 0.58, 0.31),
    "ArmorLight": material("Armor / slate edge", (0.22, 0.32, 0.45), 0.48, 0.32),
    "Cyan": material("Pulse / aqua", (0.18, 0.76, 0.72), 0.26, 0.27, (0.12, 0.85, 0.75)),
    "Gold": material("Hardware / warm brass", (0.76, 0.53, 0.23), 0.62, 0.29),
    "Skin": material("Face / warm porcelain", (0.63, 0.38, 0.29), 0.03, 0.46),
    "Dark": material("Visor / smoked glass", (0.018, 0.036, 0.064), 0.46, 0.18),
    "Blade": material("Blade / pale energy steel", (0.69, 0.98, 0.92), 0.72, 0.22, (0.34, 0.96, 0.83)),
}

ARMATURE = None
PARTS = {}


def remember(obj, bone_name, mat):
    obj.name = "Astra_%s_%02d" % (bone_name.replace(":", "_"), len(PARTS.get(bone_name, [])) + 1)
    obj.data.materials.append(mat)
    PARTS.setdefault(bone_name, []).append(obj)
    return obj


def cube(name, bone, loc, scale, mat, bevel=0.035):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bevel_mod = obj.modifiers.new("Machined edges", "BEVEL")
        bevel_mod.width = bevel
        bevel_mod.segments = 2
        obj.modifiers.new("Corner normals", "WEIGHTED_NORMAL")
    return remember(obj, bone, mat)


def sphere(name, bone, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return remember(obj, bone, mat)


def capsule(name, bone, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (radius, radius, depth / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return remember(obj, bone, mat)


def cylinder(name, bone, loc, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    bevel_mod = obj.modifiers.new("Soft facets", "BEVEL")
    bevel_mod.width = 0.018
    bevel_mod.segments = 2
    obj.modifiers.new("Corner normals", "WEIGHTED_NORMAL")
    return remember(obj, bone, mat)


def build_armature():
    bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
    arm = bpy.context.object
    arm.name = "Astra_Rig_MixamoStyle"
    arm.data.name = "Astra_MixamoStyle_Skeleton"
    bones = arm.data.edit_bones
    root = bones[0]
    root.name = "mixamorig:Root"
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.88)
    root.use_deform = False

    def add(name, head, tail, parent, connected=False):
        bone = bones.new(name)
        bone.head = head
        bone.tail = tail
        bone.parent = parent
        bone.use_connect = connected
        return bone

    hips = add("mixamorig:Hips", (0, 0, 0.88), (0, 0, 1.2), root, True)
    spine = add("mixamorig:Spine", (0, 0, 1.2), (0, 0, 1.52), hips, True)
    spine1 = add("mixamorig:Spine1", (0, 0, 1.52), (0, 0, 1.82), spine, True)
    neck = add("mixamorig:Neck", (0, 0, 1.82), (0, 0, 2.0), spine1, True)
    add("mixamorig:Head", (0, 0, 2.0), (0, 0, 2.39), neck, True)

    for side, sign in (("Left", 1), ("Right", -1)):
        sh = add("mixamorig:%sShoulder" % side, (0, 0, 1.72), (sign * 0.2, 0, 1.72), spine1)
        upper = add("mixamorig:%sArm" % side, (sign * 0.2, 0, 1.72), (sign * 0.49, 0, 1.4), sh, True)
        fore = add("mixamorig:%sForeArm" % side, (sign * 0.49, 0, 1.4), (sign * 0.58, 0, 1.09), upper, True)
        hand = add("mixamorig:%sHand" % side, (sign * 0.58, 0, 1.09), (sign * 0.61, 0, 0.98), fore, True)
        # Lower body bones use Mixamo naming so Godot's included BoneMap can be applied.
        upper_leg = add("mixamorig:%sUpLeg" % side, (sign * 0.15, 0, 0.99), (sign * 0.17, 0, 0.55), hips)
        lower_leg = add("mixamorig:%sLeg" % side, (sign * 0.17, 0, 0.55), (sign * 0.17, 0, 0.13), upper_leg, True)
        foot = add("mixamorig:%sFoot" % side, (sign * 0.17, 0, 0.13), (sign * 0.17, -0.2, 0.08), lower_leg, True)
        add("mixamorig:%sToeBase" % side, (sign * 0.17, -0.2, 0.08), (sign * 0.17, -0.31, 0.08), foot, True)
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.show_in_front = True
    arm.display_type = "WIRE"
    return arm


def build_character():
    # Legs and boots.
    for side, x in (("Left", -0.17), ("Right", 0.17)):
        bone = "mixamorig:%sUpLeg" % side
        capsule(side + " thigh", bone, (x, 0.0, 0.76), 0.14, 0.48, MATS["Armor"])
        bone = "mixamorig:%sLeg" % side
        capsule(side + " shin", bone, (x, 0.0, 0.33), 0.12, 0.42, MATS["ArmorLight"])
        cube(side + " greave", bone, (x, -0.105, 0.37), (0.19, 0.065, 0.26), MATS["Armor"])
        cube(side + " boot", "mixamorig:%sFoot" % side, (x, -0.09, 0.115), (0.28, 0.43, 0.17), MATS["Gold"])

    # Core, belt and chest plates.
    cube("Hip shell", "mixamorig:Hips", (0, 0, 1.02), (0.47, 0.34, 0.32), MATS["Armor"])
    cube("Belt", "mixamorig:Hips", (0, -0.014, 1.11), (0.57, 0.38, 0.105), MATS["Gold"], 0.025)
    cube("Buckle", "mixamorig:Hips", (0, -0.215, 1.115), (0.13, 0.035, 0.09), MATS["Dark"], 0.015)
    cube("Torso shell", "mixamorig:Spine", (0, 0, 1.43), (0.63, 0.4, 0.51), MATS["Armor"])
    cube("Shoulder rim", "mixamorig:Spine1", (0, 0, 1.7), (0.79, 0.38, 0.22), MATS["ArmorLight"])
    cube("Breast plate", "mixamorig:Spine1", (0, -0.214, 1.53), (0.46, 0.07, 0.27), MATS["ArmorLight"])
    cube("Pulse core", "mixamorig:Spine1", (0, -0.263, 1.55), (0.16, 0.035, 0.12), MATS["Cyan"], 0.025)
    capsule("Neck", "mixamorig:Neck", (0, 0, 1.91), 0.09, 0.2, MATS["Skin"])
    for side, x in (("Left", -0.37), ("Right", 0.37)):
        sphere(side + " pauldron", "mixamorig:%sShoulder" % side, (x, 0, 1.68), (0.17, 0.22, 0.15), MATS["Cyan"])

    # Arms with rigid armor sections.
    for side, sign in (("Left", 1), ("Right", -1)):
        upper = "mixamorig:%sArm" % side
        fore = "mixamorig:%sForeArm" % side
        hand = "mixamorig:%sHand" % side
        capsule(side + " upper arm", upper, (sign * 0.38, 0, 1.53), 0.105, 0.36, MATS["Armor"])
        capsule(side + " forearm", fore, (sign * 0.55, 0, 1.24), 0.105, 0.32, MATS["ArmorLight"])
        cube(side + " bracer", fore, (sign * 0.55, -0.094, 1.25), (0.2, 0.07, 0.25), MATS["Cyan"])
        sphere(side + " glove", hand, (sign * 0.6, 0, 1.04), (0.11, 0.12, 0.13), MATS["Gold"])

    # Head, smoked visor and brass crest.
    sphere("Face", "mixamorig:Head", (0, 0, 2.13), (0.205, 0.17, 0.25), MATS["Skin"])
    cube("Helmet crown", "mixamorig:Head", (0, 0.01, 2.34), (0.4, 0.34, 0.16), MATS["Gold"])
    cube("Visor", "mixamorig:Head", (0, -0.16, 2.17), (0.41, 0.045, 0.09), MATS["Dark"], 0.025)
    cube("Visor light", "mixamorig:Head", (0, -0.189, 2.17), (0.23, 0.015, 0.024), MATS["Cyan"], 0.006)
    cube("Crest", "mixamorig:Head", (0, 0.015, 2.48), (0.15, 0.19, 0.12), MATS["Gold"])

    # Training blade rides on the right hand, staying with the rig in every action.
    cube("Blade grip", "mixamorig:RightHand", (-0.61, 0.0, 0.87), (0.055, 0.065, 0.3), MATS["Dark"], 0.01)
    cube("Blade guard", "mixamorig:RightHand", (-0.61, 0.0, 1.02), (0.24, 0.075, 0.055), MATS["Gold"], 0.01)
    cube("Energy blade", "mixamorig:RightHand", (-0.61, 0.0, 1.34), (0.095, 0.06, 0.58), MATS["Blade"], 0.008)


def bind_meshes():
    for bone_name, objects in PARTS.items():
        if not objects:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        if len(objects) > 1:
            bpy.ops.object.join()
        mesh_obj = bpy.context.object
        mesh_obj.name = "AstraMesh_%s" % bone_name.replace(":", "_")
        group = mesh_obj.vertex_groups.new(name=bone_name)
        group.add(list(range(len(mesh_obj.data.vertices))), 1.0, "REPLACE")
        modifier = mesh_obj.modifiers.new("Astra skeletal rig", "ARMATURE")
        modifier.object = ARMATURE
        mesh_obj.parent = ARMATURE
        mesh_obj.matrix_parent_inverse = ARMATURE.matrix_world.inverted()
        mesh_obj["rig_bone"] = bone_name
        mesh_obj.select_set(False)


def action(name, frames):
    bpy.context.view_layer.objects.active = ARMATURE
    bpy.ops.object.mode_set(mode="POSE")
    for pose in ARMATURE.pose.bones:
        pose.rotation_mode = "XYZ"
        pose.rotation_euler = (0.0, 0.0, 0.0)
    act = bpy.data.actions.new(name)
    ARMATURE.animation_data_create()
    ARMATURE.animation_data.action = act
    for frame, transforms in frames:
        bpy.context.scene.frame_set(frame)
        for pose in ARMATURE.pose.bones:
            pose.rotation_euler = (0.0, 0.0, 0.0)
            pose.keyframe_insert(data_path="rotation_euler", frame=frame, group=pose.name)
        for bone_name, rotation in transforms.items():
            pose = ARMATURE.pose.bones.get(bone_name)
            if pose:
                pose.rotation_euler = Euler(rotation, "XYZ")
                pose.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone_name)
    # Keyframe defaults are smooth Bezier curves in Blender 5.2's layered Action API.
    act.use_fake_user = True
    bpy.ops.object.mode_set(mode="OBJECT")
    return act


def build_animations():
    hips = "mixamorig:Hips"
    spine = "mixamorig:Spine"
    head = "mixamorig:Head"
    la, ra = "mixamorig:LeftArm", "mixamorig:RightArm"
    ll, rl = "mixamorig:LeftUpLeg", "mixamorig:RightUpLeg"
    action("Idle", [(1, {}), (24, {spine: (0.0, 0.0, 0.025), head: (0.0, 0.025, 0.0)}), (48, {})])
    action("Locomotion", [(1, {ll: (0.38, 0.0, 0.0), rl: (-0.38, 0.0, 0.0), la: (-0.24, 0.0, 0.0), ra: (0.24, 0.0, 0.0)}), (9, {ll: (-0.38, 0.0, 0.0), rl: (0.38, 0.0, 0.0), la: (0.24, 0.0, 0.0), ra: (-0.24, 0.0, 0.0)}), (17, {ll: (0.38, 0.0, 0.0), rl: (-0.38, 0.0, 0.0), la: (-0.24, 0.0, 0.0), ra: (0.24, 0.0, 0.0)}), (25, {})])
    action("Melee_Slash", [(1, {}), (5, {hips: (0.0, 0.0, -0.1), spine: (0.0, 0.12, -0.1), ra: (-0.85, 0.0, -0.9)}), (10, {hips: (0.0, 0.0, 0.13), spine: (0.0, -0.18, 0.14), ra: (0.8, 0.0, 1.15)}), (18, {})])
    action("Shooter_Aim", [(1, {}), (6, {ra: (-0.95, 0.0, -0.1), la: (-0.85, 0.0, 0.12)}), (13, {ra: (-0.95, 0.0, -0.1), la: (-0.85, 0.0, 0.12)}), (20, {})])


def add_preview_setup():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(RENDER_OUT)
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"

    world = bpy.data.worlds.new("Astra Studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.025, 0.045, 0.075, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
    scene.world = world

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0.005))
    floor = bpy.context.object
    floor.name = "Preview floor"
    floor.data.materials.append(material("Preview / blue graphite", (0.035, 0.06, 0.09), 0.28, 0.62))

    bpy.ops.object.camera_add(location=(3.1, -6.4, 2.85))
    camera = bpy.context.object
    camera.name = "Preview camera"
    camera.data.lens = 65
    camera.rotation_euler = (Vector((0.0, 0.0, 1.23)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera

    def area(name, location, energy, color, size):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector((0, 0, 1.15)) - obj.location).to_track_quat("-Z", "Y").to_euler()

    area("Key / softbox", (-3.8, -4.3, 5.2), 560, (0.68, 0.82, 1.0), 4.2)
    area("Rim / aqua", (3.8, 1.4, 3.8), 720, (0.25, 0.8, 0.88), 3.4)
    area("Fill / warm", (-3.2, 1.0, 2.2), 240, (1.0, 0.72, 0.43), 3.2)


def main():
    global ARMATURE
    clear_scene()
    ARMATURE = build_armature()
    build_character()
    bind_meshes()
    build_animations()
    add_preview_setup()
    bpy.context.scene.frame_end = 48
    bpy.context.scene.render.fps = 24
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.frame_set(1)
    bpy.ops.object.select_all(action="DESELECT")
    ARMATURE.select_set(True)
    for obj in bpy.data.objects:
        if obj.name.startswith("AstraMesh_"):
            obj.select_set(True)
    bpy.context.view_layer.objects.active = ARMATURE
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_OUT))
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_OUT),
        export_format="GLB",
        export_animations=True,
        export_animation_mode="ACTIONS",
        export_skins=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        use_selection=True,
    )
    bpy.ops.render.render(write_still=True)
    print("Created", BLEND_OUT)
    print("Exported", GLB_OUT)


main()
