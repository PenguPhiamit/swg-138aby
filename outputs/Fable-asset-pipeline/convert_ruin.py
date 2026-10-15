"""Run inside Blender 3.6 (with io_scene_swg enabled):
    blender -b -P convert_ruin.py -- <Wall_Broken.obj> <out_dir>
Imports one Quaternius OBJ, gives it a constant UV (the pack has flat-colour materials and no UVs), names the object
fable_ruin_01 and the two materials after their SWG shaders, then exports the .msh with the SWG add-on.
Prints the triangle count and the bounding box so the caller can check the size."""
import bpy, os, sys

obj_path, out_dir = sys.argv[sys.argv.index('--') + 1:][:2]
os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.preferences.addon_enable(module='io_scene_swg')
bpy.ops.import_scene.obj(filepath=obj_path)
ob = [o for o in bpy.context.scene.objects if o.type == 'MESH']
assert len(ob) == 1, ob
o = ob[0]
o.name = 'fable_ruin_01'
bpy.context.view_layer.objects.active = o
bpy.ops.object.select_all(action='DESELECT')
o.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
# constant UV: every loop at (0.5, 0.5), the middle of a flat-colour texture
me = o.data
uv = me.uv_layers.new(name='UVMap')
for d in uv.data:
    d.uv = (0.5, 0.5)
names = {'Main': 'fable_ruin_main_as8', 'Highlights': 'fable_ruin_highlights_as8'}
for m in me.materials:
    m.name = names[m.name.split('.')[0]]
    m['UVSets'] = 1
    m['DOT3'] = 0
bpy.ops.export_scene.msh(filepath=os.path.join(out_dir, 'fable_ruin_01.msh'))
tris = sum(len(p.vertices) - 2 for p in me.polygons)
xs = [v.co for v in me.vertices]
print('RESULT tris', tris, 'materials', [m.name for m in me.materials])
print('RESULT bbox', [round(min(c[i] for c in xs), 3) for i in range(3)], [round(max(c[i] for c in xs), 3) for i in range(3)])
