"""Shape lineup: render several stock armour sets in one finish so only the silhouettes differ (CPU, Cycles).

    blender.exe -b --python lineup_vonduu.py -- <lineup.json> <swatch.png> <out folder>

lineup.json maps a set name to its male _l0 .mgn files (no helmets). Every set gets the same material: our swatch by box
projection in object space, darkened by ambient occlusion, like bake_vonduu.py. For each set it renders a front and a
three-quarter view at the same orthographic scale, so the sets compare at true size. Preview only: no body underneath.
"""
import importlib
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:]
SPEC, SWATCH, OUT = argv[0], argv[1], argv[2]
SCALE = 1.5
import_mgn = importlib.import_module('io_scene_swg.import_mgn')

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.render.resolution_x, scene.render.resolution_y = 420, 760
scene.world = bpy.data.worlds.new('studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.35, 0.36, 0.38, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
swatch = bpy.data.images.load(SWATCH)


def finish():
    mat = bpy.data.materials.new('crab_finish')
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.45
    bsdf.inputs['Specular'].default_value = 0.4
    coord = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (SCALE, SCALE, SCALE)
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = swatch
    tex.projection = 'BOX'
    tex.projection_blend = 0.3
    gamma = nt.nodes.new('ShaderNodeGamma')               # the same 0.7 lift as the staged DDS
    gamma.inputs['Gamma'].default_value = 0.7
    nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], gamma.inputs['Color'])
    nt.links.new(gamma.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


mat = finish()
sun = bpy.data.objects.new('key', bpy.data.lights.new('key', 'SUN'))
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(50), 0, math.radians(30))
scene.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 2.05          # metres across the taller side, the same for every set
scene.collection.objects.link(cam)
scene.camera = cam

spec = json.load(open(SPEC))
shots = {}
for set_name, files in spec.items():
    for o in [o for o in bpy.data.objects if o.type == 'MESH']:
        bpy.data.objects.remove(o, do_unlink=True)
    objs = []
    for f in files:
        before = set(bpy.data.objects)
        import_mgn.import_mgn(bpy.context, f, global_matrix=Matrix.Identity(4))
        (obj,) = set(bpy.data.objects) - before
        for slot in obj.material_slots:
            slot.material = mat
        obj.matrix_world = Matrix.Rotation(math.radians(90), 4, 'X')   # SWG is Y-up, Blender Z-up
        objs.append(obj)
    lo = Vector((min(min((o.matrix_world @ Vector(c))[i] for c in o.bound_box) for o in objs) for i in range(3)))
    hi = Vector((max(max((o.matrix_world @ Vector(c))[i] for c in o.bound_box) for o in objs) for i in range(3)))
    centre = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0.93))   # body centre at about hip height
    shots[set_name] = []
    for i, angle in enumerate((180, 215)):        # front (the visor side in the chitin preview), three-quarter
        a = math.radians(angle)
        cam.location = centre + Vector((4 * math.sin(a), -4 * math.cos(a), 0))
        cam.rotation_euler = (math.radians(90), 0, a)
        path = os.path.join(OUT, 'lineup_%s_%d.png' % (set_name, i))
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        shots[set_name].append(path)
    print('LINEUP', set_name, len(objs), 'pieces, height %.2f m' % (hi.z - lo.z), flush=True)
json.dump(shots, open(os.path.join(OUT, 'lineup_shots.json'), 'w'), indent=1)
print('LINEUP DONE', flush=True)
