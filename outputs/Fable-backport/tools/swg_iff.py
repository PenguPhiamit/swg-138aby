"""Read SOE object-template IFFs (the client's shared_*.iff) the way Core3's TemplateManager does, read-only.

Layout (from reading the files; checked against Core3-dev's deprecated objects.lua comments):
  FORM <type>            type = STOT (tangible), SSOT (static), SBOT (building), SCOT (creature), SIOT (intangible),
    FORM DERV > XXXX     SWOT (weapon), SDSC (draft schematic), SRCT (resource container), SSHP (ship), ...
      "base path\\0"     parent template (object/.../shared_x.iff); parameters not set here inherit from it
    FORM 000N            parameter block(s)
      XXXX "name\\0" + value
Values: byte type 0x00 = not set (inherit); 0x01 = simple value, followed by
  integer:   byte delta marker (0x20 ' ' none, '+' or '-') then int32 LE
  string:    cstring
  string id: (byte 0x01 + cstring table) (byte 0x01 + cstring key)
"""
import os, struct, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'owner_content'))
import swg_client_data as scd  # noqa: E402

# IFF top form tag -> the Lua class Core3-dev uses (templateType in bin/scripts/object/Shared*Template.lua)
TYPE_NAMES = {
    'STOT': 'SharedTangibleObjectTemplate', 'STAT': 'SharedStaticObjectTemplate',
    'SBOT': 'SharedBuildingObjectTemplate', 'SCOT': 'SharedCreatureObjectTemplate',
    'SITN': 'SharedIntangibleObjectTemplate', 'SIOT': 'SharedInstallationObjectTemplate',
    'SWOT': 'SharedWeaponObjectTemplate', 'SDSC': 'SharedDraftSchematicObjectTemplate',
    'RCCT': 'SharedResourceContainerObjectTemplate', 'SSHP': 'SharedShipObjectTemplate',
    'SPLY': 'SharedPlayerObjectTemplate', 'SFOT': 'SharedFactoryObjectTemplate',
    'SMSO': 'SharedMissionObjectTemplate', 'SCNC': 'SharedConstructionContractObjectTemplate',
    'SCOU': 'SharedCountingObjectTemplate', 'SGRP': 'SharedGroupObjectTemplate',
    'SGLD': 'SharedGuildObjectTemplate', 'SJED': 'SharedJediManagerTemplate',
    'SMSC': 'SharedManufactureSchematicObjectTemplate', 'SUNI': 'SharedUniverseObjectTemplate',
    'STOK': 'SharedTokenObjectTemplate', 'SWAY': 'SharedWaypointObjectTemplate',
    'CCLT': 'SharedCellObjectTemplate', 'SBMK': 'SharedBattlefieldMarkerObjectTemplate',
    'SPQO': 'SharedPlayerQuestObjectTemplate (not in Core3)',
}

_cache = {}


def raw_template(path):
    """{'form', 'derv': [base paths], 'params': {name: raw bytes}} or None when the client lacks the file."""
    key = path.lower()
    if key in _cache:
        return _cache[key]
    data = scd.client_file(path)
    if data is None:
        _cache[key] = None
        return None
    if len(data) < 12 or data[:4] != b'FORM':
        _cache[key] = {'form': None, 'derv': [], 'params': {}, 'size': len(data), 'not_iff': True}
        return _cache[key]
    top = list(scd.iff_chunks(data))[0]
    out = {'form': top[1], 'derv': [], 'params': {}, 'size': len(data)}

    def walk(s, e, in_derv):
        for tag, f, a, b in scd.iff_chunks(data, s, e):
            if tag == 'FORM':
                walk(a, b, in_derv or f == 'DERV')
            elif tag == 'XXXX':
                j = data.index(b'\0', a)
                name = data[a:j].decode('latin-1')
                if in_derv:
                    if name not in out['derv']:
                        out['derv'].append(name)
                else:
                    out['params'][name] = data[j + 1:b]
    walk(top[2], top[3], False)
    _cache[key] = out
    return out


def _int(raw):
    if len(raw) >= 6 and raw[0] == 1:
        return struct.unpack_from('<i', raw, 2)[0]
    return None


def _str(raw):
    if raw and raw[0] == 1:
        return raw[1:raw.index(b'\0', 1)].decode('latin-1')
    return None


def _string_id(raw):
    if len(raw) > 2 and raw[0] == 1:
        i = 1
        parts = []
        for _ in range(2):
            if raw[i] != 1:
                parts.append('')
                i += 1
                continue
            j = raw.index(b'\0', i + 1)
            parts.append(raw[i + 1:j].decode('latin-1'))
            i = j + 1
        return parts[0], parts[1]
    return None


def resolved(path, depth=0):
    """Effective values through the DERV chain: form, chain, gameObjectType, objectName, appearance, etc."""
    t = raw_template(path)
    if t is None:
        return None
    chain = [path]
    res = {'form': t['form'], 'chain': chain, 'gameObjectType': None, 'objectName': None,
           'detailedDescription': None, 'appearanceFilename': None, 'clientDataFile': None,
           'portalLayoutFilename': None, 'structureFootprintFileName': None, 'slotDescriptorFilename': None,
           'arrangementDescriptorFilename': None, 'containerType': None, 'containerVolumeLimit': None,
           'client_size': t['size']}
    layers = [t]
    base = t['derv'][0] if t['derv'] else None
    while base and depth < 12:
        bt = raw_template(base)
        if bt is None:
            res.setdefault('missing_base', base)
            break
        chain.append(base)
        layers.append(bt)
        base = bt['derv'][0] if bt['derv'] else None
        depth += 1
    for layer in layers:  # child first; first set value wins
        p = layer['params']
        for k in ('gameObjectType', 'containerType', 'containerVolumeLimit'):
            if res[k] is None and k in p:
                res[k] = _int(p[k])
        for k in ('appearanceFilename', 'clientDataFile', 'portalLayoutFilename', 'structureFootprintFileName',
                  'slotDescriptorFilename', 'arrangementDescriptorFilename'):
            if res[k] is None and k in p:
                res[k] = _str(p[k])
        for k in ('objectName', 'detailedDescription'):
            if res[k] is None and k in p:
                res[k] = _string_id(p[k])
    return res


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print(arg, resolved(arg))
