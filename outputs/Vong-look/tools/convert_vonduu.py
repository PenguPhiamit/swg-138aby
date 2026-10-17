"""Turn the baked vonduun PNGs into the client's DDS files (Vong look test, step 3 output).

    <ComfyUI's python_embeded>\\python.exe -I convert_vonduu.py [gamma]     (needs Pillow and numpy)

For each bake in ../bake it:
- lifts the midtones with a gamma (default 0.7);
- sets alpha to 0, because the armour shader reads the colour texture's alpha as its hue mask: 0 = no palette tint,
  so our colours show as they are (pixel_program/h_color2_envmask_specmap_*.psh: hue = lerp(colour0, colour1, alpha));
- writes BC3 (DXT5) with a full mip chain using texconv, as the stock armor_chitin_*.dds are.

Then it checks each DDS: DXT5, the stock size and mip count, alpha 0, and colour within a small tolerance of the source.
The output goes to ../staged/client/texture/ (gitignored; rebuild it with this script).
"""
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
# name -> (size, stock mip count), from the stock armor_chitin_*.dds headers (17 Oct)
TEXTURES = {
    'armor_vonduu_bicep': ((128, 256), 9), 'armor_vonduu_bracer': ((128, 256), 9),
    'armor_vonduu_boots': ((128, 256), 9), 'armor_vonduu_chest_plate': ((256, 256), 9),
    'armor_vonduu_gloves': ((128, 128), 8), 'armor_vonduu_helmet': ((256, 256), 9),
    'armor_vonduu_leggings': ((128, 256), 9),
}

os.makedirs(OUT, exist_ok=True)
ok = True
with tempfile.TemporaryDirectory() as tmp:
    for name, (size, mips) in TEXTURES.items():
        src = np.asarray(Image.open(os.path.join(BAKE, name + '.png')).convert('RGB')).astype(np.float64)
        assert (src.shape[1], src.shape[0]) == size, (name, src.shape)
        rgb = np.clip(255.0 * (src / 255.0) ** GAMMA + 0.5, 0, 255).astype(np.uint8)
        rgba = np.dstack([rgb, np.zeros(rgb.shape[:2], np.uint8)])
        png = os.path.join(tmp, name + '.png')
        Image.fromarray(rgba, 'RGBA').save(png)
        r = subprocess.run([TEXCONV, '-nologo', '-y', '-f', 'BC3_UNORM', '-m', '0', '-o', OUT, png],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        dds = os.path.join(OUT, name + '.dds')
        b = open(dds, 'rb').read()
        h, w = struct.unpack_from('<II', b, 12)
        mip_count = struct.unpack_from('<I', b, 28)[0]
        fourcc = b[84:88]
        back = np.asarray(Image.open(dds).convert('RGBA')).astype(int)
        colour_err = np.abs(back[..., :3] - rgb.astype(int)).mean()
        checks = {'DXT5': fourcc == b'DXT5', 'size': (w, h) == size, 'mips': mip_count == mips,
                  'alpha 0': int(back[..., 3].max()) == 0, 'colour': colour_err < 4.0}
        ok &= all(checks.values())
        print('%-26s %dx%d %s mips=%d alpha max=%d mean colour error=%.2f  %s' % (
            name + '.dds', w, h, fourcc.decode(), mip_count, back[..., 3].max(), colour_err,
            'OK' if all(checks.values()) else 'FAILED ' + str([k for k, v in checks.items() if not v])))
print('gamma', GAMMA, 'ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
