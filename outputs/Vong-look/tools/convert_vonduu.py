"""Turn the baked vonduun PNGs into the client's DDS files (Vong look test).

    <ComfyUI's python_embeded>\\python.exe -I convert_vonduu.py [gamma] [spec.json bake-folder]     (needs Pillow, numpy)

Without a spec it converts the first (chitin) set in ../bake. With a spec (spec_mix.json, the owner's bone + marauder
s02 mix) the texture list, sizes and the bake folder come from the arguments, and every texture with an `sm_size` also
gets its `_sm` version (the stock _sm shaders on the lower LODs read texture/<name>_sm.dds at that size).

For each texture it:
- lifts the midtones with a gamma (default 0.7; the bakes are as dark as swatch 12);
- sets alpha to 0, because the armour shaders read the colour texture's alpha as their hue mask: 0 = colour 0 only,
  so our colours show (pixel programs h_color2_*: hue = lerp(colour0, colour1, alpha));
- writes BC3 (DXT5) with the full mip chain using texconv, as the stock armour textures are (log2 of the long side + 1).

Then it checks each DDS: DXT5, size, mip count, alpha 0, and colour within a small tolerance of what was written.
The output goes to ../staged/client/texture/ (gitignored; rebuild it with this script).
"""
import json
import os
import struct
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BAKE = os.path.join(HERE, '..', 'bake')
OUT = os.path.join(HERE, '..', 'staged', 'client', 'texture')
TEXCONV = r'C:\Users\Pengw\Tools\texconv\texconv.exe'
GAMMA = float(sys.argv[1]) if len(sys.argv) > 1 else 0.7
# name -> (size, sm size or None); the first set (chitin, 17 Oct morning) has no _sm shaders
TEXTURES = {
    'armor_vonduu_bicep': ((128, 256), None), 'armor_vonduu_bracer': ((128, 256), None),
    'armor_vonduu_boots': ((128, 256), None), 'armor_vonduu_chest_plate': ((256, 256), None),
    'armor_vonduu_gloves': ((128, 128), None), 'armor_vonduu_helmet': ((256, 256), None),
    'armor_vonduu_leggings': ((128, 256), None),
}
if len(sys.argv) > 3:
    TEXTURES = {k: (tuple(v['size']), tuple(v['sm_size']) if v.get('sm_size') else None)
                for k, v in json.load(open(sys.argv[2]))['textures'].items()}
    BAKE = sys.argv[3]


def write_dds(name, rgb, tmp):
    """rgb: uint8 HxWx3. Writes OUT/name.dds and returns the check line and whether it passed."""
    h, w = rgb.shape[:2]
    rgba = np.dstack([rgb, np.zeros((h, w), np.uint8)])
    png = os.path.join(tmp, name + '.png')
    Image.fromarray(rgba, 'RGBA').save(png)
    r = subprocess.run([TEXCONV, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', '0', '-o', OUT, png],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    b = open(os.path.join(OUT, name + '.dds'), 'rb').read()
    dh, dw = struct.unpack_from('<II', b, 12)
    mips = struct.unpack_from('<I', b, 28)[0]
    back = np.asarray(Image.open(os.path.join(OUT, name + '.dds')).convert('RGBA')).astype(int)
    err = np.abs(back[..., :3] - rgb.astype(int)).mean()
    checks = {'DXT5': b[84:88] == b'DXT5', 'size': (dw, dh) == (w, h), 'mips': mips == max(w, h).bit_length(),
              'alpha 0': int(back[..., 3].max()) == 0, 'colour': err < 4.0}
    ok = all(checks.values())
    line = '%-30s %dx%d %s mips=%d alpha max=%d mean colour error=%.2f  %s' % (
        name + '.dds', dw, dh, b[84:88].decode(), mips, back[..., 3].max(), err,
        'OK' if ok else 'FAILED ' + str([k for k, v in checks.items() if not v]))
    return line, ok


os.makedirs(OUT, exist_ok=True)
all_ok = True
with tempfile.TemporaryDirectory() as tmp:
    for name, (size, sm_size) in TEXTURES.items():
        src = np.asarray(Image.open(os.path.join(BAKE, name + '.png')).convert('RGB')).astype(np.float64)
        assert (src.shape[1], src.shape[0]) == size, (name, src.shape)
        rgb = np.clip(255.0 * (src / 255.0) ** GAMMA + 0.5, 0, 255).astype(np.uint8)
        line, ok = write_dds(name, rgb, tmp)
        print(line)
        all_ok &= ok
        if sm_size:
            small = np.asarray(Image.fromarray(rgb, 'RGB').resize(sm_size, Image.LANCZOS))
            line, ok = write_dds(name + '_sm', small, tmp)
            print(line)
            all_ok &= ok
print('gamma', GAMMA, 'ALL OK' if all_ok else 'SOME FAILED')
sys.exit(0 if all_ok else 1)
