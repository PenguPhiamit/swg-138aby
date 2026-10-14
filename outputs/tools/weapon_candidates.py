"""Original read-only practical shortlist; does not import or deploy game assets."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLIENT = ROOT/'outputs/SWG-client'
OUT = ROOT/'outputs/Documentation-support/storyteller'
TOOLS = ROOT/'work/research/Miphstoe_BellumGero-Live/MMOCoreORB/tools/newplanets'


def module(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS/(name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    tre, iff = module('tre_inventory'), module('iff_tool')
    records = json.loads((OUT/'client-inventory.json').read_text(encoding='utf-8'))
    picks = [r for r in records['all_weapon_paths'] if any(k in r['path'] for k in (
        'flame', 'som_lava_cannon', 'nightsister_npc_version', 'luke_2h_test', 'ranged_donotuse'))]
    index = {}
    for archive in tre.walk_tres(str(CLIENT)):
        # Only the top-level archives in the inventory scope.
        if Path(archive).parent != CLIENT:
            continue
        for entry in tre.read_tre(archive):
            index[entry['name'].lower()] = (Path(archive), entry)

    def read(name):
        archive, entry = index[name]
        with archive.open('rb') as stream:
            stream.seek(entry['offset'])
            blob = stream.read(entry['comp_size'] if entry['comp'] else entry['size'])
        return tre._inflate(blob, entry['comp'], entry['size'])

    rows = []
    for pick in picks:
        name = pick['path']
        pending, seen, missing = [name], set(), []
        while pending:
            path = pending.pop()
            if path in seen:
                continue
            seen.add(path)
            if path not in index:
                missing.append(path)
                continue
            if path.endswith(('.dds', '.tga', '.wav', '.mp3', '.snd')):
                continue
            pending.extend(iff.refs(read(path)))
        server = name.replace('/shared_', '/')
        lua_rel = Path(server.removesuffix('.iff')+'.lua')
        lua_sources = []
        for repo in ('Miphstoe_BellumGero-Live', 'Thrax989_SWGFlurry', 'mod-the-galaxy'):
            base = ROOT/'work/research'/repo/'MMOCoreORB/bin/scripts'
            for relative in (lua_rel, Path('object/custom_content')/Path(*lua_rel.parts[1:])):
                path = base/relative
                if path.is_file():
                    text = path.read_text(encoding='utf-8', errors='replace')
                    values = {key: match.group(1).strip() for key in
                              ('damageType', 'minDamage', 'maxDamage', 'attackSpeed', 'attackType')
                              if (match := re.search(r'^\s*'+key+r'\s*=\s*([^,\n]+)', text, re.M))}
                    lua_sources.append(dict(path=str(path.relative_to(ROOT)),
                                            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                            local_values=values))
        rows.append(dict(client_template=name, server_template_candidate=server,
                         archives=pick['archives'], client_sha256=hashlib.sha256(read(name)).hexdigest(),
                         referenced_paths=len(seen), missing_refs=sorted(missing), lua_sources=lua_sources,
                         status='local client presence verified; current server registration and gameplay untested',
                         historical_storyteller_identity='unverified'))
    (OUT/'usable-candidates.json').write_text(json.dumps(rows, indent=2)+'\n',encoding='utf-8')
    print(json.dumps([dict(path=r['server_template_candidate'], lua=len(r['lua_sources']),
                           missing=r['missing_refs']) for r in rows],indent=2))


if __name__ == '__main__':
    main()
