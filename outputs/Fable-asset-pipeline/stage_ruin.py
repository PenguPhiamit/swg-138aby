"""Stage the first outside-art prop (F86) in the test-session archive.

    python -I Fable-asset-pipeline/stage_ruin.py <work_dir> [--install]

<work_dir> holds the converted files: fable_ruin_01.msh (Blender add-on export), fable_ruin_main.dds and fable_ruin_highlights.dds (texconv).
This script builds the two small IFF files (the .apt and the .sht), then packs
    appearance/mesh/fable_ruin_01.msh      the mesh
    appearance/fable_ruin_01.apt           names the mesh (the add-on's own .apt layout)
    shader/fable_ruin_<material>_as8.sht   two clones of a stock one-texture shader, texture path replaced
    texture/fable_ruin_<material>.dds      two flat-colour textures (the pack has no atlas)
    appearance/eqp_camping_log_fresh.apt   OVERRIDE of the stock campfire log's appearance so it names our mesh:
                                           the owner sees the piece by spawning a stock campfire (no server change)
on top of the entries already in SWG-client/local_planets.tre, into Fable-asset-pipeline/staged/local_planets.tre.
With --install the client copy is backed up (Local-content/old-client-local_planets.tre.<sha8>) and replaced.
Every reference is checked to resolve (in the new archive or the stock load order) before anything is written.
"""
import hashlib, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(OUT, 'tools', 'swgfmt'))
import trn_iff as T  # noqa: E402
import tre_write  # noqa: E402

CLIENT_TRE = os.path.join(OUT, 'SWG-client', 'local_planets.tre')
STOCK_SHADER = 'shader/eqp_camping_ground_fresh_as8.sht'
OVERRIDE_APT = 'appearance/eqp_camping_log_fresh.apt'
MESH_PATH = 'appearance/mesh/fable_ruin_01.msh'
MATERIALS = ('main', 'highlights')   # the pack's two flat-colour materials, one shader + one DDS each
SHADERS = {m: f'shader/fable_ruin_{m}_as8.sht' for m in MATERIALS}
TEXTURES = {m: f'texture/fable_ruin_{m}.dds' for m in MATERIALS}


def cstr(s):
    return s.encode('ascii') + b'\0'


def build_apt(mesh_path):
    return T.build([T.form('APT ', T.form('0000', T.chunk('NAME', cstr(mesh_path))))])


def build_sht(tex_path):
    stock = T.client_file(STOCK_SHADER)
    nodes = T.parse(stock)
    hits = []

    def walk(ns, under_txm=False):
        for n in ns:
            if n.is_form:
                walk(n.children, under_txm or n.form == 'TXM ')
            elif n.tag == 'NAME' and under_txm:
                hits.append(n)
    walk(nodes)
    assert len(hits) == 1, 'expected exactly one texture NAME in the stock shader'
    hits[0].data = cstr(tex_path)
    out = T.build(nodes)
    assert T.build(T.parse(out)) == out
    return out


def check_dds(data):
    assert data[:4] == b'DDS '
    h, w = int.from_bytes(data[12:16], 'little'), int.from_bytes(data[16:20], 'little')
    mips = int.from_bytes(data[28:32], 'little')
    four = data[84:88]
    assert four in (b'DXT1', b'DXT5'), four
    assert w & (w - 1) == 0 and h & (h - 1) == 0, (w, h)
    assert mips == max(w, h).bit_length(), (mips, w, h)
    return f'{w}x{h} {four.decode()} {mips} mips'


def main(argv):
    work = argv[0]
    install = '--install' in argv
    msh = open(os.path.join(work, 'fable_ruin_01.msh'), 'rb').read()
    new = {
        MESH_PATH: msh,
        'appearance/fable_ruin_01.apt': build_apt(MESH_PATH),
        OVERRIDE_APT: build_apt(MESH_PATH),
    }
    for m in MATERIALS:
        dds = open(os.path.join(work, f'fable_ruin_{m}.dds'), 'rb').read()
        print(f'dds {m}:', check_dds(dds))
        new[TEXTURES[m]] = dds
        new[SHADERS[m]] = build_sht(TEXTURES[m])
    # existing archive contents, unchanged
    files = {}
    from swgfmt.fmt_tools import read_tre, _inflate
    with open(CLIENT_TRE, 'rb') as s:
        for e in read_tre(CLIENT_TRE):
            s.seek(e['offset'])
            blob = s.read(e['comp_size'] if e['comp'] else e['size'])
            files[e['name'].lower()] = _inflate(blob, e['comp'], e['size'])
    old_n = len(files)
    if any(k in files for k in new if k != OVERRIDE_APT):
        print('note: replacing earlier staged copies of this prop')
    files.update({k.lower(): v for k, v in new.items()})

    # reference closure
    msh_nodes = T.parse(msh)
    shaders = []

    def names(ns):
        for n in ns:
            if n.is_form:
                names(n.children)
            elif n.tag == 'NAME':
                shaders.append(n.data.rstrip(b'\0').decode())
    names(msh_nodes)
    assert sorted(shaders) == sorted(SHADERS.values()), shaders
    assert T.client_file('effect/a_simple.eft'), 'effect missing'
    for m in MATERIALS:
        sht_names = []

        def names2(ns):
            for n in ns:
                if n.is_form:
                    names2(n.children)
                elif n.tag == 'NAME':
                    sht_names.append(n.data.rstrip(b'\0').decode())
        names2(T.parse(new[SHADERS[m]]))
        assert sorted(sht_names) == sorted([TEXTURES[m], 'effect/a_simple.eft']), sht_names
        assert SHADERS[m] in files and TEXTURES[m] in files
    assert MESH_PATH in files
    print('closure OK: apt -> msh -> 2 sht -> 2 dds, effect/a_simple.eft in stock')

    data = tre_write.pack(files)
    staged = os.path.join(HERE, 'staged')
    os.makedirs(staged, exist_ok=True)
    out = os.path.join(staged, 'local_planets.tre')
    open(out, 'wb').write(data)
    # read back
    back = {}
    with open(out, 'rb') as s:
        for e in read_tre(out):
            s.seek(e['offset'])
            blob = s.read(e['comp_size'] if e['comp'] else e['size'])
            back[e['name'].lower()] = _inflate(blob, e['comp'], e['size'])
    assert back == files, 'read-back mismatch'
    sha = hashlib.sha256(data).hexdigest()
    print(f'staged {out}: {old_n} -> {len(files)} entries, {len(data)} bytes, sha256 {sha}')
    for k in new:
        print('  +', k, len(new[k]))
    if install:
        old_sha = hashlib.sha256(open(CLIENT_TRE, 'rb').read()).hexdigest()
        backup = os.path.join(OUT, 'Local-content', 'old-client-local_planets.tre.' + old_sha[:8])
        if not os.path.exists(backup):
            shutil.copy2(CLIENT_TRE, backup)
        shutil.copy2(out, CLIENT_TRE)
        print('installed to', CLIENT_TRE, '; previous copy kept as', backup)


if __name__ == '__main__':
    main(sys.argv[1:])
