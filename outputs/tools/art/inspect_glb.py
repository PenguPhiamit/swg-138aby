"""Check an image-to-3D GLB in Blender 3.6 and try it at SWG prop size (CPU only).

    blender.exe -b --python inspect_glb.py -- <model.glb> <out folder> [target triangles, default 2000]

Prints and writes <out>/<name>_inspect.json:
- objects, triangles, vertices, UV layers, materials and their image textures with sizes, bounding-box size in metres;
- the same after a Decimate (collapse) to the target triangle count, which is the stock static-prop budget the asset
  pipeline uses (Fable-asset-pipeline/README.md: under about 2,000 triangles);
and renders <name>_full.png and <name>_decimated.png (Cycles, CPU, the GLB's own textures) for a side-by-side look.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
GLB, OUT = argv[0], argv[1]
TARGET = int(argv[2]) if len(argv) > 2 else 2000
NAME = os.path.splitext(os.path.basename(GLB))[0]
os.makedirs(OUT, exist_ok=True)

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.gltf(filepath=GLB)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']


def tris(objs):
    total = 0
    for o in objs:
        o.data.calc_loop_triangles()
        total += len(o.data.loop_triangles)
    return total


def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p[i] for p in pts) for i in range(3)))
    hi = Vector((max(p[i] for p in pts) for i in range(3)))
    return lo, hi


def info(objs):
    lo, hi = bounds(objs)
    mats = {}
    for o in objs:
        for s in o.material_slots:
            m = s.material
            if m and m.use_nodes:
                imgs = [(n.image.name, list(n.image.size)) for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
                mats[m.name] = imgs
    return {'objects': len(objs), 'triangles': tris(objs), 'vertices': sum(len(o.data.vertices) for o in objs),
            'uv_layers': sorted({u.name for o in objs for u in o.data.uv_layers}),
            'size_m': [round(hi[i] - lo[i], 3) for i in range(3)], 'materials': mats}


report = {'glb': GLB, 'bytes': os.path.getsize(GLB), 'imported': info(meshes)}
print('INSPECT imported', json.dumps(report['imported']), flush=True)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.render.resolution_x, scene.render.resolution_y = 640, 640
scene.world = bpy.data.worlds.new('studio')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.46, 0.48, 1)
lo, hi = bounds(meshes)
centre, size = (lo + hi) / 2, max(hi - lo)
sun = bpy.data.objects.new('key', bpy.data.lights.new('key', 'SUN'))
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(50), 0, math.radians(35))
scene.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.type = 'ORTHO'
cam.data.ortho_scale = size * 1.6
scene.collection.objects.link(cam)
scene.camera = cam
d = Vector((1.0, -1.2, 0.9)).normalized() * size * 4
cam.location = centre + d
cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()


def render(path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


render(os.path.join(OUT, NAME + '_full.png'))
for o in meshes:
    n = tris([o])
    if n > TARGET:
        mod = o.modifiers.new('to_budget', 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = max(TARGET / float(tris(meshes)), 0.0005)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
report['decimated'] = info(meshes)
report['decimate_target'] = TARGET
print('INSPECT decimated', json.dumps(report['decimated']), flush=True)
render(os.path.join(OUT, NAME + '_decimated.png'))
json.dump(report, open(os.path.join(OUT, NAME + '_inspect.json'), 'w'), indent=1)
print('INSPECT DONE', flush=True)
