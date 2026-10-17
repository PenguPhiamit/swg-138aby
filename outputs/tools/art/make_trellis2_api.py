"""Build our TRELLIS.2 image-to-3D workflow (API form) from ComfyUI's own template export (Claude, 17 Oct 2026).

    python -I make_trellis2_api.py <template_api.json> [out.json]

The input is ComfyUI 0.41.0's template "Pixal3D & TRELLIS.2: Image to Model" (3d_pixal3d_trellis2_image_to_model.json),
converted to API form by ComfyUI's own frontend (app.graphToPrompt(), which also writes the "dynamic combo" sub-inputs
such as sign_mode.qef correctly) and saved through ComfyUI's user-data store
(ComfyUI/user/default/trellis2_template_api.json, sha256 98dde0cd... on 17 Oct). This script then:

- resolves the template's switches statically: TRELLIS.2, not Pixal3D (the PrimitiveBoolean "Switch to Trellis2" feeds
  three ComfySwitchNodes), and background removal on;
- keeps only the nodes the Save 3D node needs, which drops Pixal3D, the MoGe model (not downloaded), the vertex-colour
  and raw-voxel previews and the UV-atlas preview;
- points the DINOv3 loader at dino_v3_vit_l.safetensors, the file we downloaded (ComfyUI's docs: either works);
- sets defaults for SWG props on a 12 GB card (each can be changed with um comfy run --set NODE.INPUT=...):
    upsample target_resolution 1024 (the minimum; the template asks 1536), remesh resolution 512 (768 ran out of
    memory on this card), texture resolution 1024 (SWG props use 256-512; we downscale), decimate to 20,000 faces
    (Blender takes it to the client's budget), file prefix 3d/trellis2;
- names the image loader "Concept image" so --set "Concept image.image=<file in ComfyUI/input>" works.
"""
import json
import sys

SRC = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else 'trellis2_image_to_3d_api.json'
SAVE = '322'            # Save3DAdvanced
USE_TRELLIS2 = True

wf = json.load(open(SRC, encoding='utf-8'))
assert wf['316']['class_type'] == 'PrimitiveBoolean' and wf['316']['_meta']['title'] == 'Boolean (Switch to Trellis2)'
assert wf[SAVE]['class_type'] == 'Save3DAdvanced'


def constant(ref):
    """The value of a switch input: a literal, or a PrimitiveBoolean's value."""
    if isinstance(ref, list):
        node = wf[ref[0]]
        assert node['class_type'] == 'PrimitiveBoolean', node
        return USE_TRELLIS2 if ref[0] == '316' else node['inputs']['value']
    return ref


# 1. resolve every ComfySwitchNode to the input it selects
switches = {k: v for k, v in wf.items() if v['class_type'] == 'ComfySwitchNode'}
chosen = {}
for k, v in switches.items():
    chosen[k] = v['inputs']['on_true'] if constant(v['inputs']['switch']) else v['inputs']['on_false']


def follow(ref):
    while isinstance(ref, list) and ref[0] in chosen:
        ref = chosen[ref[0]]
    return ref


for v in wf.values():
    for name, ref in list(v['inputs'].items()):
        if isinstance(ref, list) and len(ref) == 2 and isinstance(ref[0], str):
            v['inputs'][name] = follow(ref)

# 2. keep what the save node needs
keep, todo = set(), [SAVE]
while todo:
    k = todo.pop()
    if k in keep:
        continue
    keep.add(k)
    for ref in wf[k]['inputs'].values():
        if isinstance(ref, list) and len(ref) == 2 and isinstance(ref[0], str) and ref[0] in wf:
            todo.append(ref[0])
api = {k: wf[k] for k in sorted(keep, key=int)}
assert not any(v['class_type'] in ('ComfySwitchNode', 'Pixal3DConditioning', 'LoadMoGeModel', 'PrimitiveBoolean')
               for v in api.values()), sorted(v['class_type'] for v in api.values())

# 3. our files and defaults
api['15']['inputs']['clip_name'] = 'dino_v3_vit_l.safetensors'
api['122']['inputs']['image'] = 'concept.png'
api['122']['_meta']['title'] = 'Concept image'
api['94']['inputs']['target_resolution'] = 1024
api['288']['inputs']['value'] = 1024
api['186']['inputs']['target_face_count'] = 20000
api['241']['inputs']['resolution'] = 512   # remesh: 768 (the template) ran out of memory on the 12 GB card, 17 Oct
api[SAVE]['inputs']['filename_prefix'] = '3d/trellis2'

json.dump(api, open(OUT, 'w', encoding='utf-8', newline='\n'), indent=1)
print('kept %d of %d nodes -> %s' % (len(api), len(wf), OUT))
print(' '.join('%s:%s' % (k, v['class_type']) for k, v in api.items()))
