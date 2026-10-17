"""Render the male chitin armour set with our vonduun textures, front and three-quarter views (CPU, Cycles).

    blender.exe -b --python preview_vonduu.py -- <mesh folder> <folder with texture PNGs> <out.png> [spec.json]

The texture PNGs are the staged DDS files decoded back (what the client will sample, before its lighting and hue).
With a spec (spec_mix.json) the pieces and the stock shader -> our texture map come from it; any other shader on a piece
(the visor, the marauder chainmail) gets a dark stand-in.
Preview only: no armature, no skin underneath, flat studio light; the client's own lighting will differ.
"""
import importlib
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:]
MESH_DIR, TEX_DIR, OUT = argv[0], argv[1], argv[2]
PIECES = {   # mesh -> our texture for its armour shader
    'armor_chitin_s01_bicep_l_m_l0.mgn': 'armor_vonduu_bicep', 'armor_chitin_s01_bicep_r_m_l0.mgn': 'armor_vonduu_bicep',
    'armor_chitin_s01_bracer_l_m_l0.mgn': 'armor_vonduu_bracer', 'armor_chitin_s01_bracer_r_m_l0.mgn': 'armor_vonduu_bracer',
    'armor_chitin_s01_boots_m_l0.mgn': 'armor_vonduu_boots', 'armor_chitin_s01_chest_plate_m_l0.mgn': 'armor_vonduu_chest_plate',
    'armor_chitin_s01_gloves_m_l0.mgn': 'armor_vonduu_gloves', 'armor_chitin_s01_helmet_m_l0.mgn': 'armor_vonduu_helmet',
    'armor_chitin_s01_leggings_m_l0.mgn': 'armor_vonduu_leggings',
}
SHADERS = None   # stock shader -> our texture, in spec mode
if len(argv) > 3:
    spec = json.load(open(argv[3]))
    SHADERS = {s: t for t, v in spec['textures'].items() for s in v['shaders']}
    PIECES = {p: None for p in spec['pieces']}
import_mgn = importlib.import_module('io_scene_swg.import_mgn')
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 48
scene.render.resolution_x, scene.render.resolution_y = 1024, 768
scene.world = bpy.data.worlds.new('studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.35, 0.36, 0.38, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8


def textured(name, image):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = image
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.45
    bsdf.inputs['Specular'].default_value = 0.4
    return mat


visor = bpy.data.materials.new('visor_stand_in')
visor.use_nodes = True
visor.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1)
visor.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.15

images, objects = {}, []
for mesh_file, tex in PIECES.items():
    before = set(bpy.data.objects)
    import_mgn.import_mgn(bpy.context, os.path.join(MESH_DIR, mesh_file), global_matrix=Matrix.Identity(4))
    (obj,) = set(bpy.data.objects) - before
    for slot in obj.material_slots:
        name = slot.material.name if slot.material else ''
        if SHADERS is not None:
            ours = SHADERS.get(name)
        else:
            ours = tex if name.startswith('armor_chitin') and 'has15' not in name else None
        if ours and ours not in images:
            images[ours] = bpy.data.images.load(os.path.join(TEX_DIR, ours + '.png'))
        slot.material = textured(ours, images[ours]) if ours else visor
    obj.matrix_world = Matrix.Rotation(math.radians(90), 4, 'X')   # SWG is Y-up, Blender Z-up
    objects.append(obj)

# frame the set
lo = Vector((min(min((o.matrix_world @ Vector(c))[i] for c in o.bound_box) for o in objects) for i in range(3)))
hi = Vector((max(max((o.matrix_world @ Vector(c))[i] for c in o.bound_box) for o in objects) for i in range(3)))
centre, height = (lo + hi) / 2, hi.z - lo.z
print('PREVIEW bounds', tuple(round(v, 2) for v in lo), tuple(round(v, 2) for v in hi))

sun = bpy.data.objects.new('key', bpy.data.lights.new('key', 'SUN'))
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(50), 0, math.radians(210))   # lights the front (the +Y side, where the visor faces)
scene.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.type = 'ORTHO'
cam.data.ortho_scale = height * 1.08 * scene.render.resolution_x / scene.render.resolution_y   # the scale spans the wider side
scene.collection.objects.link(cam)
scene.camera = cam

shots = []
for i, angle in enumerate((0, 35, 180)):
    a = math.radians(angle)
    d = 4.0
    cam.location = centre + Vector((d * math.sin(a), -d * math.cos(a), 0))
    cam.rotation_euler = (math.radians(90), 0, a)
    path = OUT.replace('.png', '_%d.png' % i)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    shots.append(path)
print('PREVIEW DONE', shots, flush=True)
