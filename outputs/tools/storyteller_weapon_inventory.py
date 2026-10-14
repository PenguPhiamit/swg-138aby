"""Read-only inventory of local client TRE metadata and small template references.

Uses previously reviewed Bellum Gero TRE reader (AGPL-3.0). Never extracts assets
to disk, executes game scripts, or reads excluded research source trees.
"""
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLIENT = ROOT / 'outputs/SWG-client'
OUT = ROOT / 'outputs/Documentation-support/storyteller'
READER = ROOT / 'work/research/Miphstoe_BellumGero-Live/MMOCoreORB/tools/newplanets/tre_inventory.py'
spec = importlib.util.spec_from_file_location('reviewed_tre_reader', READER)
tre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tre)
REF = re.compile(rb'object/weapon/[a-zA-Z0-9_/.-]+\.iff')
MARK = re.compile(r'story_?teller|(?:^|[/_])(?:npc|dev|developer|test|gm|god)(?:[/_.]|$)', re.I)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    versions, archive_rows, errors = {}, [], []
    priorities = tre.cfg_priorities(str(CLIENT))
    for archive in sorted(CLIENT.glob('*.tre')):
        try:
            entries = tre.read_tre(str(archive))
        except Exception as exc:
            errors.append({'archive': archive.name, 'error': str(exc)})
            continue
        archive_rows.append(dict(name=archive.name, bytes=archive.stat().st_size,
                                 entries=len(entries), cfg_priority=priorities.get(archive.name.lower())))
        for entry in entries:
            name = entry['name'].lower()
            versions.setdefault(name, []).append((archive, entry))
    candidates, context, weapon_refs, content_matches = [], [], [], []
    weapon_versions_inspected = 0
    for name, copies in sorted(versions.items()):
        is_context = 'storyteller' in name or 'story_teller' in name
        any_weapon = name.startswith('object/weapon/')
        is_weapon = name.startswith('object/weapon/') and MARK.search(name)
        if not (is_context or any_weapon):
            continue
        row = {'path': name, 'archives': [a.name for a, _ in copies]}
        if is_context:
            context.append(row)
        if is_weapon:
            candidates.append(row)
        # Read every small IFF version: no unconfigured archive is treated as active.
        for archive, entry in copies:
            if not name.endswith('.iff') or entry['size'] > 2_000_000:
                continue
            try:
                with archive.open('rb') as stream:
                    stream.seek(entry['offset'])
                    raw = stream.read(entry['comp_size'] if entry['comp'] else entry['size'])
                data = tre._inflate(raw, entry['comp'], entry['size'])
                if len(data) != entry['size']:
                    raise ValueError('decoded length differs from TRE record')
                if any_weapon:
                    weapon_versions_inspected += 1
                    if re.search(rb'story_?teller', data, re.I):
                        content_matches.append(dict(path=name, archive=archive.name,
                                                    sha256=hashlib.sha256(data).hexdigest()))
                refs = sorted({m.group().decode('ascii') for m in REF.finditer(data)})
                if is_weapon or refs:
                    weapon_refs.append(dict(path=name, archive=archive.name,
                                            sha256=hashlib.sha256(data).hexdigest(),
                                            weapon_refs=refs,
                                            strings=[s.decode('ascii') for s in re.findall(rb'[ -~]{5,}', data)
                                                     if b'/' not in s][:35]))
            except Exception as exc:
                errors.append(dict(path=name, archive=archive.name, error=str(exc)))
    source_hits, source_counts = [], {}
    needles = [Path(c['path']).name.removeprefix('shared_').removesuffix('.iff') for c in candidates]
    pattern = 'storyteller.*weapon|weapon.*storyteller|' + '|'.join(needles)
    for repo in ('Miphstoe_BellumGero-Live', 'Thrax989_SWGFlurry', 'mod-the-galaxy'):
        base = ROOT / 'work/research' / repo / 'MMOCoreORB/bin/scripts'
        listing = subprocess.run(['rg', '--files', str(base), '-g', '*.lua'], capture_output=True, text=True, encoding='utf-8')
        source_counts[repo] = len(listing.stdout.splitlines())
        matches = subprocess.run(['rg', '-l', '-i', pattern, str(base), '-g', '*.lua'], capture_output=True, text=True, encoding='utf-8')
        for line in matches.stdout.splitlines():
            path = Path(line)
            text = path.read_text(encoding='utf-8', errors='replace')
            relevant = []
            for number, line in enumerate(text.splitlines(), 1):
                low = line.lower()
                if ('storyteller' in low and 'weapon' in low) or any(
                    needle in low for needle in needles):
                    relevant.append({'line': number, 'text': line.strip()[:400]})
            if relevant:
                source_hits.append(dict(path=str(path.relative_to(ROOT)),
                                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(), hits=relevant))
    all_weapons = [dict(path=name, archives=[a.name for a, _ in copies])
                   for name, copies in sorted(versions.items()) if name.startswith('object/weapon/')]
    result = dict(scope='Top-level local SWG-client TREs, all versions including unconfigured archives; naming candidates and Storyteller context only. Not a complete official NGE server inventory.',
                  reader=str(READER.relative_to(ROOT)), reader_sha256=hashlib.sha256(READER.read_bytes()).hexdigest(),
                  archives=archive_rows, unique_paths=len(versions), named_weapon_candidates=candidates,
                  storyteller_context=context, inspected_templates=weapon_refs, errors=errors,
                  all_weapon_paths=all_weapons, source_lua_counts=source_counts, source_hits=source_hits)
    result['weapon_versions_inspected'] = weapon_versions_inspected
    result['weapon_content_storyteller_matches'] = content_matches
    (OUT/'client-inventory.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'archives':len(archive_rows), 'unique_paths':len(versions),
                      'named_weapon_candidates':candidates, 'storyteller_context_count':len(context),
                      'templates_with_details':len(weapon_refs), 'weapon_paths':len(all_weapons),
                      'source_lua_counts':source_counts, 'source_hit_files':len(source_hits), 'errors':errors}, indent=2))


if __name__ == '__main__':
    main()
