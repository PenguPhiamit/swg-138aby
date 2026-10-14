"""Read-only weapon identity metadata; never equates client art with live stats.

Reuses the reviewed Bellum TRE/IFF readers through weapon_candidates. Reads
every local weapon version and direct Storyteller template/clientdata refs.
Writes metadata only; does not import assets or execute game scripts.
"""
import hashlib
import json
import re
import struct
from collections import defaultdict
from pathlib import Path

import weapon_candidates as wc


def stf_names(blob):
    """Read only the existing STF key/value layout, with bounds checks."""
    if len(blob) < 13:
        raise ValueError('short STF header')
    _, _, _, count = struct.unpack_from('<IBII', blob)
    offset, values = 13, {}
    for _ in range(count):
        oid, _, length = struct.unpack_from('<III', blob, offset)
        offset += 12
        end = offset + length * 2
        if end > len(blob):
            raise ValueError('STF value exceeds buffer')
        values[oid] = blob[offset:end].decode('utf-16le')
        offset = end
    result = {}
    for _ in range(count):
        oid, length = struct.unpack_from('<II', blob, offset)
        offset += 8
        end = offset + length
        if end > len(blob):
            raise ValueError('STF key exceeds buffer')
        key = blob[offset:end].decode('latin-1')
        result[key] = values[oid]
        offset = end
    if offset != len(blob):
        raise ValueError('unparsed STF tail')
    return result


def fields(iff, blob):
    result = {}
    def walk(nodes):
        for tag, _, _, _, data in nodes:
            if tag == 'FORM':
                walk(data)
            elif tag == 'XXXX':
                field, _, payload = data.partition(b'\0')
                field = field.decode('ascii', errors='replace')
                if field in ('objectName', 'appearanceFilename', 'weaponEffect'):
                    # Preserve the raw value; printable tokens are only a convenience.
                    result[field] = dict(raw_hex=payload.hex(), tokens=[
                        x.decode('ascii') for x in re.findall(rb'[ -~]{2,}', payload)])
    walk(iff.parse(blob))
    return result


def main():
    tre, iff = wc.module('tre_inventory'), wc.module('iff_tool')
    index, errors = defaultdict(list), []
    for archive in sorted(wc.CLIENT.glob('*.tre')):
        for entry in tre.read_tre(str(archive)):
            index[entry['name'].lower()].append((archive, entry))

    def read(copy):
        archive, entry = copy
        with archive.open('rb') as handle:
            handle.seek(entry['offset'])
            blob = tre._inflate(handle.read(entry['comp_size'] if entry['comp'] else entry['size']),
                                entry['comp'], entry['size'])
        if len(blob) != entry['size']:
            raise ValueError('decoded TRE length mismatch')
        return blob

    name_cache = {}
    def names(table, key):
        path = 'string/en/' + table + '.stf'
        if path not in name_cache:
            options = []
            for copy in index.get(path, []):
                try:
                    blob = read(copy)
                    options.append((copy[0].name, hashlib.sha256(blob).hexdigest(), stf_names(blob)))
                except Exception as exc:
                    errors.append(dict(path=path, archive=copy[0].name, error=str(exc)))
            name_cache[path] = options
        return [dict(table=path, archive=archive, sha256=digest, key=key, text=values[key])
                for archive, digest, values in name_cache[path] if key in values]

    weapons = []
    for path, copies in sorted(index.items()):
        if not path.startswith('object/weapon/'):
            continue
        versions = []
        for copy in copies:
            if not path.endswith('.iff'):
                continue
            try:
                blob = read(copy)
                record = dict(archive=copy[0].name, bytes=len(blob),
                              sha256=hashlib.sha256(blob).hexdigest(), fields=fields(iff, blob),
                              explicit_references=iff.refs(blob))
                tokens = record['fields'].get('objectName', {}).get('tokens', [])
                record['name_resolutions'] = names(*tokens) if len(tokens) == 2 else []
                versions.append(record)
            except Exception as exc:
                errors.append(dict(path=path, archive=copy[0].name, error=str(exc)))
        weapons.append(dict(path=path, versions=versions))

    context = []
    for path, copies in sorted(index.items()):
        if not re.search(r'story_?teller', path) or not path.endswith(('.iff', '.cdf')):
            continue
        for copy in copies:
            try:
                blob = read(copy)
                refs = iff.refs(blob)
                context.append(dict(path=path, archive=copy[0].name,
                                    sha256=hashlib.sha256(blob).hexdigest(),
                                    weapon_references=[r for r in refs if r.startswith('object/weapon/')],
                                    other_object_references=[r for r in refs if r.startswith('object/')
                                                             and not r.startswith('object/weapon/')]))
            except Exception as exc:
                errors.append(dict(path=path, archive=copy[0].name, error=str(exc)))
    summary = dict(weapon_paths=len(weapons), weapon_versions=sum(len(r['versions']) for r in weapons),
                   storyteller_context_versions=len(context),
                   direct_storyteller_weapon_links=sum(bool(r['weapon_references']) for r in context),
                   paths_with_multiple_payload_hashes=sum(len({v['sha256'] for v in r['versions']}) > 1
                                                          for r in weapons),
                   errors=len(errors))
    output = dict(scope='All 76 local top-level client TRE archives, including inactive/unconfigured '
                        'archives. No runtime precedence assumed. Client metadata, not SOE live statistics.',
                  provenance={str(wc.TOOLS.joinpath(x).relative_to(wc.ROOT)):
                              hashlib.sha256((wc.TOOLS/x).read_bytes()).hexdigest()
                              for x in ('tre_inventory.py', 'iff_tool.py')},
                  summary=summary, weapons=weapons, storyteller_context=context, errors=errors)
    (wc.OUT/'identity-metadata.json').write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
