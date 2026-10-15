"""asset_refs.refs(buf): the client-file paths a client file refers to (Fable T2, 14 Oct 2026), our own scanner for
tools/hoth/hoth_closure.py. Three kinds of reference, each lower-cased, backslashes read as '/':
  absolute paths  <folder>/<...>.<ext> for the client's asset folders and file types;
  relative children of an appearance (mesh/, lod/, skeleton/, collision/, component/) -> appearance/<...>;
  terrain families: a .trn's shader families (SFAM chunks of the SGRP group) list bare shader names -> shader/<name>.sht,
  and its flora/radial families list bare appearance file names -> appearance/<name>.<apt|prt|msh|sat>.
"""
import re

FOLDERS = 'appearance|shader|texture|terrain|object|sound|clientdata|effect|creation|datatables|snapshot|misc|footprint|interiorlayout|string'
TYPES = 'sht|apt|msh|mgn|sat|lmg|lod|pob|cmp|dds|tga|iff|prt|eft|trn|ws|snd|flr|lsb|cdf|ans|skt'
ABSOLUTE = re.compile(rb'(?:%s)/[a-z0-9_/\-\.]+\.(?:%s)' % (FOLDERS.encode(), TYPES.encode()), re.I)
CHILD = re.compile(rb'(?<![a-z0-9_/])(?:mesh|lod|skeleton|collision|component)/[a-z0-9_/\-\.]+\.(?:msh|mgn|lmg|lod|skt|cmp|apt|pob|flr)', re.I)
BARE_APPEARANCE = re.compile(rb'(?<![a-z0-9_/])[a-z0-9_]+\.(?:apt|prt|msh|sat)', re.I)
FAMILY_WORD = re.compile(rb'[a-z0-9_]{3,}')
NOT_SHADERS = ('abstract', 'terrain_surface', 'iff')


def _terrain_shaders(buf):
    """shader/<name>.sht for every shader name in the SFAM chunks under the terrain's SGRP form (bare names in the
    file; the first word of a chunk is the family's own name, 'terrain_surface' and 'iff' are the surface template)."""
    out = set()
    if not (buf.startswith(b'FORM') and buf[8:12] == b'PTAT'):
        return out
    pos, inside = 0, False
    while pos + 8 <= len(buf):
        tag, size = buf[pos:pos + 4], int.from_bytes(buf[pos + 4:pos + 8], 'big')
        if tag == b'FORM':
            inside = inside or buf[pos + 8:pos + 12] == b'SGRP'
            pos += 12                      # step into the form
            continue
        if tag == b'SFAM' and inside:
            for word in FAMILY_WORD.findall(buf[pos + 8:pos + 8 + size])[1:]:
                name = word.decode('latin-1').lower()
                if name not in NOT_SHADERS:
                    out.add('shader/%s.sht' % name)
        pos += 8 + size
    return out


def refs(buf):
    buf = buf.replace(b'\\', b'/')
    out = {m.group(0).decode('latin-1').lower() for m in ABSOLUTE.finditer(buf)}
    if buf.startswith(b'FORM') and buf[8:12] == b'PTAT':
        out |= _terrain_shaders(buf)
        out |= {'appearance/' + m.group(0).decode('latin-1').lower() for m in BARE_APPEARANCE.finditer(buf)}
    out |= {'appearance/' + m.group(0).decode('latin-1').lower() for m in CHILD.finditer(buf)}
    return sorted(out)
