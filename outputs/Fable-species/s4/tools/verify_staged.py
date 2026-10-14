"""Re-read every staged client file with our readers and compare with the stock copy: rows/blocks/keys added, exact
round trip of each output, every referenced hair/wearable in the merged CRC table. Our own code (Fable, 14 Oct 2026).

    python -I verify_staged.py <stage_dir> <species...>
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-planet-test', 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-ossus', 'tools'))
import acst  # noqa: E402
import swg_tables as st  # noqa: E402
from trn_iff import build, client_file, open_tre_entry, parse  # noqa: E402


def main(argv):
    stage, species = argv[0], [s.lower() for s in argv[1:]]
    merged = set(n for _, n in st.read_cstb(open_tre_entry(os.path.join(OUTPUTS, 'Local-content', 'local_planets.tre'), 'misc/object_template_crc_string_table.iff'))['entries'])
    rep = {}
    for d, _, files in os.walk(stage):
        for fn in files:
            p = os.path.join(d, fn)
            rel = os.path.relpath(p, stage).replace(os.sep, '/')
            data = open(p, 'rb').read()
            stock = client_file(rel)
            r = {'bytes': len(data), 'stock_bytes': len(stock) if stock else None}
            if rel.endswith('.stf'):
                a, b = st.read_stf(data), st.read_stf(stock)
                r.update(round_trip=st.write_stf(a) == data, keys=len(a['keys']), keys_added=len(a['keys']) - len(b['keys']),
                         stock_keys_kept=dict(st.stf_items(b)).items() <= dict(st.stf_items(a)).items(),
                         new_keys=[k for k, _ in st.stf_items(a) if k not in dict(st.stf_items(b))])
            elif rel.endswith('.inc'):
                t = data.decode('latin-1'); s = stock.decode('latin-1')
                r.update(species_blocks=sorted(set(re.findall(r"Name='([a-z_]+)'\s+skill='species_", t))), stock_text_kept=all(line in t for line in s.splitlines()),
                         crlf_only=('\n' not in t.replace('\r\n', '')))
            elif 'asset_customization_manager' in rel:
                a = acst.read_acst(data); r.update(round_trip=acst.write_acst(a) == data, cidx=len(a['cidx']))
            else:
                root = parse(data)[0]
                if root.form == 'DTII':
                    a, b = st.read_dtii(data), st.read_dtii(stock)
                    r.update(round_trip=st.write_dtii(a) == data, rows=len(a['rows']), rows_added=len(a['rows']) - len(b['rows']),
                             stock_rows_kept=all(row in a['rows'] for row in b['rows']), types_same_as_stock=a['types'] == b['types'])
                    # client templates (shared_*) must be in the merged CRC table; server template columns (hair_assets_skill_mods
                    # SERVER_TEMPLATE / SERVER_PLAYER_TEMPLATE) are checked against Core3-dev by s3/tools/dev_check.sh instead
                    refs = [c for row in a['rows'][len(b['rows']):] for c in row if isinstance(c, str) and c.startswith('object/') and c.endswith('.iff') and '/shared_' in c] if rel != 'datatables/skill/skills.iff' else []
                    r['refs_missing_in_merged_crc'] = sorted(set(c for c in refs if c not in merged))
                else:
                    tree = parse(data); r.update(round_trip=build(tree) == data, form=root.form, blocks=len(root.children[0].children),
                                                 blocks_added=len(root.children[0].children) - len(parse(stock)[0].children[0].children))
                    refs = sorted(set(m.group(0).decode('latin-1') for c in root.children[0].children[len(parse(stock)[0].children[0].children):] for m in re.finditer(rb'object/[A-Za-z0-9_/\.]+\.iff', build([c]))))
                    r['refs_missing_in_merged_crc'] = [x for x in refs if x not in merged]
            rep[rel] = r
    ok = all(v.get('round_trip', True) and not v.get('refs_missing_in_merged_crc') and v.get('stock_rows_kept', True) and v.get('stock_keys_kept', True) and v.get('stock_text_kept', True) for v in rep.values())
    rep['_verdict'] = 'PASS' if ok else 'CHECK'
    print(json.dumps(rep, indent=1)[:6000])
    with open(os.path.join(HERE, '..', 'out', 'verify-staged-report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, indent=1)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
