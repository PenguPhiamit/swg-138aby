"""The Togruta customization map (Fable species S6, 14 Oct 2026). No ACST table anywhere (stock, the 2016 package copy) maps
appearance/togruta_f.sat, so the creation sliders the package's customization_data rows name (muscle, weight, chest,
skin colour) would have nothing to drive. This module adds one map for it to a copy of the package's 2016 ACST, so that
species_tables.stage_species(..., acst_other=...) splices it into today's table exactly as it splices Nautolan's.

What the map declares, and why (read from the files, not guessed):
- the four blend shapes the Togruta meshes carry (appearance/mesh/togruta_f_body_l0.mgn: blend_fat, blend_flat_chest,
  blend_muscle, blend_skinny; the head mesh togruta_f_l0.mgn: fat, flat_chest, skinny), with the ranges every stock
  female map uses (0..256; flat_chest -155..156 stored as the u32 pair 4294967141, 156 like hum_f.sat / chiss_f.sat);
- /shared_owner/index_color_skin on palette/npc_togruta.pal, the one palette shader/togruta_body.sht and
  togruta_head.sht reference (both stock + MTG files), default 0.
No face blends: the Togruta head mesh has none (an NPC head), so no face sliders are offered (the package's
customization_data rows for togruta_female name only the body group, consistent with that).
Our own code; uses s4/tools/acst.py's tables.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECIES = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(SPECIES, 's4', 'tools'))
import acst  # noqa: E402
from swg_tables import soe_crc  # noqa: E402

APPEARANCE = 'appearance/togruta_f.sat'
TOGRUTA_VARS = [
    ('/shared_owner/index_color_skin', ('palette', 'palette/npc_togruta.pal'), 0),
    ('/shared_owner/blend_fat', ('range', 0, 256), 0),
    ('/shared_owner/blend_flat_chest', ('range', 4294967141, 156), 0),
    ('/shared_owner/blend_muscle', ('range', 0, 256), 0),
    ('/shared_owner/blend_skinny', ('range', 0, 256), 0),
]


def with_togruta(other_bytes, variables=TOGRUTA_VARS, appearance=APPEARANCE):
    """A copy of `other_bytes` (an ACST table) with one new map for `appearance` declaring `variables`. Returns
    (bytes, key). Refuses to touch a table that already maps the appearance."""
    d = acst.read_acst(other_bytes)
    acst._tables(d)
    crc = soe_crc(appearance)
    assert crc not in d['_c'], appearance + ' is already mapped'
    for k in ('_u', '_l', '_c'):
        d.pop(k, None)
    key = max([k for _, k in d['cidx']] + [k for k, _, _ in d['uidx']] + [k for k, _, _ in d['lidx']]) + 1
    start = len(d['ulst'])
    for name, typ, default in variables:
        vi = acst._index_of(d['vnof'], acst._add_name(d, name))
        if typ[0] == 'palette':
            pi = acst._index_of(d['pnof'], acst._add_name(d, typ[1]))
            ri = acst._index_of(d['rtyp'], 0x8000 | pi)
        else:
            ii = acst._index_of(d['irng'], (typ[1], typ[2]))
            ri = acst._index_of(d['rtyp'], ii)
        di = acst._index_of(d['defv'], default)
        d['ulst'].append(acst._index_of(d['ucmp'], (vi, ri, di)))
    d['uidx'].append((key, start, len(variables)))
    d['cidx'].append((crc, key))
    d['uidx'].sort(key=lambda r: r[0])
    d['cidx'].sort(key=lambda r: r[0])
    out = acst.write_acst(d)
    back = acst.read_acst(out)
    got = acst.flatten(acst.resolve(back, acst.lookup(back, appearance)))
    assert got == list(variables), got
    # every map the table had before resolves as before
    before = acst.read_acst(other_bytes)
    acst._tables(before); acst._tables(back)
    changed = [c for c, k in before['cidx'] if acst.flatten(acst.resolve(before, k)) != acst.flatten(acst.resolve(back, back['_c'][c]))]
    assert not changed, changed[:5]
    return out, key


def resolved(table_bytes, appearance=APPEARANCE):
    d = acst.read_acst(table_bytes)
    k = acst.lookup(d, appearance)
    return None if k is None else acst.flatten(acst.resolve(d, k))
