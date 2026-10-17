"""Bake our vonduun-crab swatch onto the stock chitin armour's UV layouts (Vong look test, step 3).

Run inside Blender 3.6 with NSG SWG Tools enabled (the portable install's own config; never --factory-startup):

    blender.exe -b --python bake_vonduu.py -- <folder with the male _l0 .mgn files> <swatch.png> <out folder> [scale]

For each texture the warrior needs, it imports one stock mesh with the add-on's importer, keeps only the mesh's own UVs,
and paints it with our swatch by box (triplanar) projection in object space, darkened by ambient occlusion from the
geometry. No stock texture pixel is read. It then bakes that colour (an EMIT bake on the CPU) into an image at the stock
texture's size, plus a white coverage mask of the UV islands for the orientation check. Faces that use another shader
(the helmet visor) bake into a throwaway image, so the visor keeps its stock texture.
"""
import importlib
import json
import os
import sys

import bpy
from mathutils import Matrix

argv = sys.argv[sys.argv.index('--') + 1:]
MESH_DIR, SWATCH, OUT = argv[0], argv[1], argv[2]
SCALE = float(argv[3]) if len(argv) > 3 else 1.5   # repeats per metre of the box projection

# our texture -> (stock mesh to bake from, stock shader whose faces it covers, stock texture size)
TARGETS = {
    'armor_vonduu_bicep': ('armor_chitin_s01_bicep_l_m_l0.mgn', 'armor_chitin_bicep_hces24', (128, 256)),
    'armor_vonduu_bracer': ('armor_chitin_s01_bracer_l_m_l0.mgn', 'armor_chitin_bracer_hces24', (128, 256)),
    'armor_vonduu_boots': ('armor_chitin_s01_boots_m_l0.mgn', 'armor_chitin_boots_hces24', (128, 256)),
    'armor_vonduu_chest_plate': ('armor_chitin_s01_chest_plate_m_l0.mgn', 'armor_chitin_chest_plate_hces24', (256, 256)),
    'armor_vonduu_gloves': ('armor_chitin_s01_gloves_m_l0.mgn', 'armor_chitin_gloves_hces24', (128, 128)),
    'armor_vonduu_helmet': ('armor_chitin_s01_helmet_m_l0.mgn', 'armor_chitin_visor_hces24', (256, 256)),
    'armor_vonduu_leggings': ('armor_chitin_s01_leggings_m_l0.mgn', 'armor_chitin_leggings_hces24', (128, 256)),
}

import_mgn = importlib.import_module('io_scene_swg.import_mgn')

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'          # keep the GPU free for the owner
scene.cycles.samples = 64
scene.render.bake.margin = 8
scene.render.bake.use_clear = True

swatch = bpy.data.images.load(SWATCH)
throwaway = bpy.data.images.new('throwaway', 16, 16)


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)


def our_material(name, target, mode):
    """mode 'color': swatch by box projection x AO, emitted; mode 'mask': plain white."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emit = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    if mode == 'color':
        coord = nt.nodes.new('ShaderNodeTexCoord')
        mapping = nt.nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value = (SCALE, SCALE, SCALE)
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = swatch
        tex.projection = 'BOX'
        tex.projection_blend = 0.3
        ao = nt.nodes.new('ShaderNodeAmbientOcclusion')
        ao.inputs['Distance'].default_value = 0.05
        ao.samples = 16
        shade = nt.nodes.new('ShaderNodeMapRange')          # AO 0..1 -> 0.55..1, a gentle darkening
        shade.inputs['To Min'].default_value = 0.55
        mix = nt.nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Fac'].default_value = 1.0
        nt.links.new(coord.outputs['Object'], mapping.inputs['Vector'])
        nt.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
        nt.links.new(ao.outputs['AO'], shade.inputs['Value'])
        nt.links.new(tex.outputs['Color'], mix.inputs['Color1'])
        nt.links.new(shade.outputs['Result'], mix.inputs['Color2'])
        nt.links.new(mix.outputs['Color'], emit.inputs['Color'])
    else:
        emit.inputs['Color'].default_value = (1, 1, 1, 1)
    bake_node = nt.nodes.new('ShaderNodeTexImage')
    bake_node.image = target
    nt.nodes.active = bake_node
    return mat


def throwaway_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    node.image = throwaway
    mat.node_tree.nodes.active = node
    return mat


report = {}
for tex_name, (mesh_file, shader, (w, h)) in TARGETS.items():
    results = {}
    for mode in ('color', 'mask'):
        clear_scene()
        import_mgn.import_mgn(bpy.context, os.path.join(MESH_DIR, mesh_file), global_matrix=Matrix.Identity(4))
        obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
        stock = [s.material.name if s.material else None for s in obj.material_slots]
        assert shader in stock, (mesh_file, stock)
        target = bpy.data.images.new('%s_%s' % (tex_name, mode), w, h, alpha=False)
        for i, slot in enumerate(obj.material_slots):
            slot.material = our_material('ours_%d' % i, target, mode) if stock[i] == shader else \
                throwaway_material('skip_%d' % i)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        scene.render.bake.margin = 8 if mode == 'color' else 0   # the mask shows the bare UV islands
        bpy.ops.object.bake(type='EMIT')
        path = os.path.join(OUT, '%s%s.png' % (tex_name, '' if mode == 'color' else '_mask'))
        target.filepath_raw = path
        target.file_format = 'PNG'
        target.save()
        results[mode] = path
    report[tex_name] = {'mesh': mesh_file, 'shader': shader, 'size': [w, h], 'materials': stock,
                        'triangles': len(obj.data.polygons), 'uv_layers': [u.name for u in obj.data.uv_layers],
                        'files': results}
    print('BAKED', tex_name, w, h, stock, len(obj.data.polygons), flush=True)

with open(os.path.join(OUT, 'bake_report.json'), 'w') as f:
    json.dump({'swatch': SWATCH, 'scale': SCALE, 'textures': report}, f, indent=1)
print('BAKE DONE', len(report), flush=True)
