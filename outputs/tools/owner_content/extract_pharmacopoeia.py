"""Owner's Galactic Pharmacopoeia v2 -> structured catalogue, matched to real SWG professions. (Claude, 14 Oct 2026.)

    python -I tools/owner_content/extract_pharmacopoeia.py

Input: Content-catalogue/owner-SWG-SW5E/Galactic_Pharmacopoeia_Expanded_v2.bbox.html (pdftotext -bbox-layout of the
owner's PDF; word coordinates keep the table columns straight across page breaks).
Output: Content-catalogue/owner-SWG-SW5E/pharmacopoeia.json.

Owner, 14 Oct 2026: the book is a reference for new professions, mats and consumables; "Match everything to the
correct SWG profession style, we will need to develope those a bit make them actually useful but that can wait".
So each substance gets the real SWG crafter that would make it (profession, line and, where SWG already has the
item, the real schematic and skill box, read from the client's tables), and each resource node gets the real
resource class where one exists. Effects are not designed yet. Left out on purpose: the "IRL Analogue" column (not
SWG material). The book's tabletop mechanics are kept only as reference text and are not implemented.
"""
import collections, html, json, os, re, sys

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
DIR = os.path.join(H, 'outputs', 'Content-catalogue', 'owner-SWG-SW5E')
SRC = os.path.join(DIR, 'Galactic_Pharmacopoeia_Expanded_v2.bbox.html')  # pdftotext -bbox-layout of the PDF
OUT = os.path.join(DIR, 'pharmacopoeia.json')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SUB_COLS = ['SW Name', 'IRL Analogue', 'Origin / Lore', 'Effects', 'Mechanics', 'Legality', 'Price', 'Risk', 'Status']
RES_COLS = ['Resource', 'Type', 'Quality', 'Survey DC', 'Planet/Source', 'Notes', 'Primary Use']


def visual_lines(path):
    """[(page, [(xMin, word), ...])] from pdftotext -bbox-layout, one entry per visual line (words within 2 pt of
    the same top edge), in reading order. Word x positions are page coordinates, so a table's columns stay put
    across page breaks (the -layout text shifted them)."""
    words = []
    page = 0
    for line in open(path, encoding='utf-8'):
        if '<page ' in line:
            page += 1
        m = re.search(r'<word xMin="([\d.]+)" yMin="([\d.]+)"[^>]*>(.*?)</word>', line)
        if m:
            words.append((page, float(m[2]), float(m[1]), html.unescape(m[3])))
    words.sort()
    out, cur, top = [], None, None
    for pg, y, x, w in words:
        if cur is None or pg != cur[0] or abs(y - top) > 2:
            cur, top = (pg, []), y
            out.append(cur)
        cur[1].append((x, w))
    return [(pg, sorted(ws)) for pg, ws in out]


def text_of(ws):
    return ' '.join(w for _, w in ws)


def parse_table(lines, header_names, starts_row):
    """Rows of a table: column x positions come from the header line; starts_row(cells) says whether a visual line
    begins a new row (cells: {column index: [words]})."""
    rows, xs, cur = [], None, None
    for _, ws in lines:
        line = text_of(ws)
        if line.startswith(header_names[0]) and header_names[1] in line:
            xs = []
            for h in header_names:  # x of the first word of each header name
                first = h.split()[0]
                xs.append(next(x for x, w in ws if w == first and (not xs or x > xs[-1])))
            continue
        if xs is None:
            continue
        cells = collections.defaultdict(list)
        for x, w in ws:
            col = max([i for i, cx in enumerate(xs) if cx <= x + 3] or [0])
            cells[col].append(w)
        if starts_row(cells):
            cur = collections.defaultdict(list)
            rows.append(cur)
        if cur is None:
            continue
        for col, texts in cells.items():
            cur[col].extend(texts)
    clean = lambda parts: re.sub(r'\s+', ' ', ' '.join(parts)).replace('- ', '-').strip()
    return [{header_names[c]: clean(v) for c, v in r.items()} for r in rows]


def sections(lines, pattern, stop=None):
    """[(title, lines)] split on visual lines whose text matches pattern; stops at a line matching stop."""
    out, cur = [], None
    for pg, ws in lines:
        line = text_of(ws)
        if stop and re.match(stop, line):
            break
        m = re.match(pattern, line)
        if m:
            cur = (line, [])
            out.append(cur)
        elif cur:
            cur[1].append((pg, ws))
    return out


# --- real SWG matches (client skills.iff / schematic_group.iff, checked 14 Oct) -----------------------------------
SPICE = 'Smuggler, Spices line (XP Spice Crafting)'
REAL_ITEMS = {  # book name (lower, prefix) -> (real schematic, granting skill box, profession line)
    'neutron pixie': ('spice_neutron_pixey', 'combat_smuggler_spice_04', SPICE),
    'muon gold': ('spice_muon_gold', 'combat_smuggler_spice_04', SPICE),
    'booster blue': ('spice_booster_blue', 'combat_smuggler_spice_04', SPICE),
    'giggledust': ('spice_giggledust', 'combat_smuggler_spice_01', SPICE),
    'gunjack': ('spice_gunjack', 'combat_smuggler_spice_03', SPICE),
    'yarrock': ('spice_yarrock', 'combat_smuggler_spice_01', SPICE + '; the book files it under medicine, real SWG has it as a spice'),
    'stim pack': ('med_stimpack_a … med_stimpack_e', 'science_medic_novice (A), science_medic_crafting_02 (B), science_medic_crafting_04 (C), '
                  'science_medic_master (D), science_doctor_support_03 (E)', 'Medic, Organic Chemistry line; E is Doctor'),
    'antidote': ('medpack_cure_poison_a/b/c (+ area)', 'science_doctor_novice, science_doctor_support_02, science_doctor_support_04', 'Doctor'),
    'synthskin': ('medpack_wound_* (health/action/attributes)', 'science_medic_crafting_01 onward, Doctor support line', 'Medic, then Doctor'),
    'calming salve': ('med_stimpack_state_intimidated_a', 'science_doctor_support_01', 'Doctor (cures the intimidated state)'),
    'stimcaf': ('drink_caf', 'crafting_artisan_domestic_02', 'Artisan, Domestic Arts line (then Chef)'),
    'corellian whiskey': ('drink_corellian_brandy / drink_corellian_ale (nearest)', 'crafting_chef_drink_02 / _01', 'Chef, Mixology line'),
    'military medpac': ('med_stimpack_range_* / med_stimpack_area_*', 'science_combatmedic_novice onward', 'Combat Medic, Combat Medicine Crafting'),
    'emergency medpac': ('med_stimpack_a (nearest)', 'science_medic_novice', 'Medic'),
}
FORCE_WORDS = re.compile(r'\bForce\b|\bSith\b|\bJedi\b|Je.daii|Nightsister|Malachor|dark side|Frangawl|Jedha|kyber', re.I)


def swg_match(section, sub):
    name = sub['SW Name'].lower()
    for key, (item, box, line) in REAL_ITEMS.items():
        if name.startswith(key):
            return dict(crafter=line, real_item=item, real_skill_box=box, fit='exists in SWG')
    lore = ' '.join([sub.get('Origin / Lore', ''), sub.get('Effects', ''), sub.get('SW Name', '')])
    if name.startswith('neuro-sync'):  # the book: "Droid Engineer/Pharmacist synthesis"; its Force line is flavour
        return dict(crafter='Pharmacist (new, F87); a black-market spice in SWG terms', fit='new profession')
    if name.startswith('andris'):
        return dict(crafter=SPICE, fit='new spice in a real line')
    if section.startswith('5.') or (section.startswith('1.') and FORCE_WORDS.search(lore)):
        return dict(crafter='not player-crafted: Force or story content (quest reward or loot)', fit='story')
    if section.startswith(('1.', '2.')):
        return dict(crafter=SPICE, fit='new spice in a real line')
    if section.startswith('3.'):
        if 'herb' in name or 'root' in name:
            return dict(crafter='Botanist (new, F87) grows it; Pharmacist (new) prepares it', fit='new profession')
        return dict(crafter='Pharmacist (new, F87); nearest real crafters are Medic and Doctor', fit='new profession')
    if section.startswith('4.'):
        if re.search(r'questioner|skirtopanol|interrogation|truth', lore, re.I):
            return dict(crafter='story item (interrogation); Toxicologist (new) could analyse it', fit='story')
        if FORCE_WORDS.search(lore):
            return dict(crafter='not player-crafted: Force or story content', fit='story')
        if 'venom' in name:
            return dict(crafter='Toxicologist (new, F87) from creature venom; nearest real: Combat Medic poison packs', fit='new profession')
        return dict(crafter='Combat Medic, Combat Medicine Crafting (real poison/disease packs: medpack_poison_*, medpack_disease_*); '
                            'antidote by Toxicologist (new)', fit='real line')
    if section.startswith('6.'):
        if 'root' in name:
            return dict(crafter='Botanist (new, F87) grows it; Pharmacist (new) prepares it', fit='new profession')
        return dict(crafter='Pharmacist (new, F87): species-specific support; nearest real items are Doctor enhancers '
                            '(medpack_enhance_*)', fit='new profession')
    return dict(crafter='?', fit='?')


def resource_match(res, classes):
    """Real resource classes whose display name shares a distinctive word with the book's resource."""
    generic = {'raw', 'extract', 'resin', 'base', 'compound', 'precursor', 'crystal', 'crystals', 'dust', 'salve', 'serum',
               'medium', 'culture', 'paste', 'powder', 'reagent', 'spores', 'fungal', 'root', 'sap', 'oil', 'venom', 'gas',
               'essence', 'ore', 'shard', 'shards', 'stone', 'mineral', 'alkaloid', 'agent', 'leaf', 'leaves', 'bark', 'seed',
               'seeds', 'water', 'ash', 'ashes', 'gland', 'tissue', 'blood', 'bile', 'silk', 'coral', 'synthetic', 'the', 'of',
               'flower', 'flowers', 'dark', 'deposit', 'vein',
               # planet names match every per-planet class of that planet, which says nothing about the material
               'tatooine', 'naboo', 'corellia', 'corellian', 'talus', 'rori', 'dantooine', 'lok', 'yavin', 'endor',
               'dathomir', 'dathomirian', 'kashyyyk', 'mustafar', 'hoth'}
    words = [w for w in re.findall(r"[a-z']+", res['Resource'].lower()) if w not in generic and len(w) > 3]
    hits = [(enum, disp) for enum, disp in classes if any(re.search(r'\b' + re.escape(w) + r'\b', disp.lower()) for w in words)]
    return hits[:4]


def main():
    lines = visual_lines(SRC)
    status_col = SUB_COLS.index('Status')
    new_sub = lambda cells: bool(cells.get(0)) and bool(re.match(r'(Canon|Legends|New)\b', ' '.join(cells.get(status_col, []))))
    subs, counts = [], {}
    for title, body in sections(lines, r'^\d\. [A-Z].*\((\d+) Substances\)', stop=r'^PART II:'):
        rows = parse_table(body, SUB_COLS, new_sub)
        expected = int(re.search(r'\((\d+) Substances\)', title)[1])
        counts[title] = (len(rows), expected)
        for r in rows:
            entry = {
                'id': 'ph-' + re.sub(r'[^a-z0-9]+', '-', r.get('SW Name', '?').lower()).strip('-'),
                'name': r.get('SW Name', ''), 'section': title, 'origin_lore': r.get('Origin / Lore', ''),
                'effects_text': r.get('Effects', ''), 'legality': r.get('Legality', ''), 'price': r.get('Price', ''),
                'risk': r.get('Risk', ''), 'lore_status': r.get('Status', ''),
                'tabletop_mechanics_reference_only': r.get('Mechanics', ''),
                'swg': swg_match(title, r), 'status': 'optional, not enabled; effects not designed yet',
            }
            subs.append(entry)
    import swg_client_data as c
    tree = c.datatable(c.client_file('datatables/resource/resource_tree.iff'))
    classes = []
    for r in tree:
        disp = next((r['CLASS %d' % i] for i in range(8, 0, -1) if r['CLASS %d' % i]), '')
        classes.append((r['ENUM'], disp))
    type_col = RES_COLS.index('Type')
    new_res = lambda cells: bool(cells.get(0)) and bool(cells.get(type_col))
    resources = []
    for title, body in sections(lines, r'^Table \d+: .*\((\d+) entries\)', stop=r'^APPENDIX A'):
        rows = parse_table(body, RES_COLS, new_res)
        expected = int(re.search(r'\((\d+) entries\)', title)[1])
        counts[title] = (len(rows), expected)
        for r in rows:
            hits = resource_match(r, classes)
            resources.append({
                'id': 'phr-' + re.sub(r'[^a-z0-9]+', '-', r.get('Resource', '?').lower()).strip('-'),
                'name': r.get('Resource', ''), 'table': title, 'type': r.get('Type', ''), 'quality': r.get('Quality', ''),
                'source': r.get('Planet/Source', ''), 'notes': r.get('Notes', ''), 'primary_use': r.get('Primary Use', ''),
                'real_swg_class': [f'{e} ({d})' for e, d in hits] or None,
                'status': 'existing class' if hits else 'new mat (F88)',
            })
    json.dump({'source': {'file': 'Galactic_Pharmacopoeia_Expanded_v2.pdf',
                          'pdf_sha256': 'de56c5db41b8569e8592d613fd72771a45f50da031b36f2e7621d2adebf7d2aa',
                          'title': 'Galactic Pharmacopoeia & Research Chemicals, v2.0 (expanded)', 'author': 'the server owner'},
               'instruction': 'Owner, 14 Oct 2026: reference for new professions, mats and consumables; match everything '
                              'to the correct SWG profession style; making them useful comes later.',
               'left_out': ['IRL Analogue column', 'tabletop mechanics are reference only'],
               'substances': subs, 'resources': resources},
              open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    for t, (got, want) in counts.items():
        print(f'{"ok " if got == want else "BAD"} {got:3d}/{want:3d}  {t}')
    print(collections.Counter(s['swg']['fit'] for s in subs), collections.Counter(r['status'] for r in resources))


if __name__ == '__main__':
    main()
