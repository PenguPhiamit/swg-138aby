"""Extract the SWG material from the owner's "Star Wars Galaxies x SW5E" core rulebook (revision 3.0, 7 Oct 2026).

    python -I tools/owner_content/extract_swg_sw5e.py

Input: Content-catalogue/owner-SWG-SW5E/SWG_SW5E_Core_Expanded_v3.txt (pdftotext -layout of the owner's PDF).
Output: Content-catalogue/owner-SWG-SW5E/swg-optional-content.json, one record per item, each with its page.

Owner's instruction (14 Oct 2026): "grab all the SWG stuff i made and add it all as optional content. (DO NOT
IMPLEMENT THE SW5e stuff)". So this keeps the SWG layer (planet dossiers, resources and crafting, schematics,
professions, factions, NPC lives, markets, bestiary behaviour) and drops the SW5E layer: classes, ability scores,
d20 checks and DCs, AC/HP/CR stat blocks, damage dice, SW5E species packages and the tabletop GM protocol. Where a
record mixes both, the SW5E part is removed and the record says so in "sw5e_removed".
Read-only apart from the JSON. Standard library only.
"""
import json, os, re

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
SRC = os.path.join(H, 'outputs', 'Content-catalogue', 'owner-SWG-SW5E', 'SWG_SW5E_Core_Expanded_v3.txt')
OUT = os.path.join(H, 'outputs', 'Content-catalogue', 'owner-SWG-SW5E', 'swg-optional-content.json')

# Zones this server can host today, and MTG terrain we hold for later planets (C14 / catalogue).
OUR_ZONES = {'Tatooine': 'tatooine', 'Naboo': 'naboo', 'Corellia': 'corellia', 'Talus': 'talus', 'Rori': 'rori',
             'Dantooine': 'dantooine', 'Lok': 'lok', 'Yavin 4': 'yavin4', 'Endor': 'endor', 'Dathomir': 'dathomir'}
MTG_TERRAIN = {'Coruscant': 'coruscant', 'Zeltros': 'zeltros (MTG resource download, not yet installed)',
               'Mandalore': 'mandalore', 'Nal Hutta': 'hutta', 'Kashyyyk': 'kashyyyk', 'Korriban': 'moraband',
               'Hoth': 'hoth'}
DC = re.compile(r'\s*\bDC\s*\d+[^.;]*')


def load_pages():
    """Return [(page_number, lines)] with running headers removed."""
    text = open(SRC, encoding='utf-8').read()
    pages = []
    for raw in text.split('\f'):
        lines = raw.split('\n')
        lines = [l for l in lines if not l.startswith('CORE RULEBOOK')]
        number = None
        for l in reversed(lines):
            m = re.search(r'\s(\d{1,3})\s*$', l)
            if l.strip():
                number = int(m.group(1)) if m else None
                if m:
                    lines.remove(l)
                break
        pages.append((number, lines))
    return pages


def flat(pages, first, last):
    """Lines from page first..last inclusive, each tagged with its page."""
    out = []
    for number, lines in pages:
        if number is not None and first <= number <= last:
            out += [(number, l) for l in lines]
    return out


def prose(lines):
    return re.sub(r'\s+', ' ', ' '.join(l.strip() for _, l in lines)).strip()


def split_on(tagged, starts):
    """Split tagged lines into blocks; a block starts at a line whose stripped text is in starts."""
    blocks, cur = [], None
    for page, line in tagged:
        if line.strip() in starts:
            cur = {'name': line.strip(), 'page': page, 'lines': []}
            blocks.append(cur)
        elif cur is not None:
            cur['lines'].append((page, line))
    return blocks


def between(text, start, end_markers):
    i = text.find(start)
    if i < 0:
        return ''
    i += len(start)
    ends = [text.find(e, i) for e in end_markers]
    ends = [e for e in ends if e >= 0]
    return text[i:min(ends) if ends else len(text)].strip()


def planets(pages):
    tagged = flat(pages, 18, 41)
    names = []
    for i, (_, l) in enumerate(tagged[:-1]):
        nxt = next((t for _, t in tagged[i + 1:] if t.strip()), '')
        if l.strip() and nxt.strip().startswith('Lore anchor'):
            names.append(l.strip())
    out = []
    for b in split_on(tagged, set(names)):
        text = prose(b['lines'])
        rows = []
        for _, l in b['lines']:
            m = re.match(r'^\s(\S.*?\S)\s{2,}(L|H|U|I|C-opt|AH)\s{2,}(\S.*\S)\s*$', l)
            if m and m.group(1) != 'Resource / stock':
                rows.append({'resource': m.group(1), 'evidence': m.group(2), 'crafting_role': m.group(3)})
        hooks = re.findall(r'- Hook \d \[H\]\. (.*?)(?= - Hook \d| Run it\.|$)', text)
        anchor = re.match(r'Lore anchor \[([^\]]+)\]\. (.*?) Era check\.', text)
        out.append({
            'id': 'planet-' + re.sub(r'[^a-z0-9]+', '-', b['name'].lower()).strip('-'), 'name': b['name'], 'page': b['page'],
            'lore_sources': anchor.group(1).replace(' ', '').split(',') if anchor else [],
            'lore_anchor': anchor.group(2) if anchor else '',
            'era_check': between(text, 'Era check.', [' Resource / stock']),
            'resources': rows,
            'culture_scene': between(text, 'Explore the culture [H].', ['Travel and access']),
            'travel_and_access': between(text, 'Travel and access [H].', ['- Hook 1']),
            'hooks': [h.strip() for h in hooks],
            'in_game': ('existing zone ' + OUR_ZONES[b['name']]) if b['name'] in OUR_ZONES else
                       ('terrain held: ' + MTG_TERRAIN[b['name']]) if b['name'] in MTG_TERRAIN else 'no terrain yet',
            'status': 'optional, not enabled'})
    return out


def schematics(pages):
    text = prose(flat(pages, 47, 49))
    out = []
    for m in re.finditer(r'(A\d\d) \| (.*?) Qualification\. (.*?) Inputs\. (.*?) DC / time / output working value\. (\d+) / '
                         r'(.*?) / (\d+) cr\. Experimental line\. (.*?) Result\. (.*?)(?= A\d\d \||Three reverse-engineering|$)', text):
        result = m.group(9).strip()
        removed = []
        for pat, why in ((r'Base 1d8 energy.*?; no extra attack\.', 'SW5E weapon statistics'),
                         (r'AC 12\+DEX, light proficiency;', 'SW5E armour class and proficiency')):
            if re.search(pat, result):
                result = re.sub(pat, '', result).strip()
                removed.append(why)
        out.append({'id': m.group(1), 'name': m.group(2), 'page': '47-49', 'qualification': m.group(3),
                    'inputs': m.group(4).rstrip('.'), 'time': m.group(6), 'working_value_cr': int(m.group(7)),
                    'experimental_line': m.group(8), 'result': result,
                    'sw5e_removed': ['assembly DC ' + m.group(5)] + removed, 'status': 'optional, not enabled'})
    return out


def table_rows(lines, header_re=r'^\s*Discipline\s+I\s+II\s+III\s+IV\s*$'):
    """Parse the four-rank discipline tables using the header's column positions."""
    rows, cols, cur = [], None, None
    for _, l in lines:
        if re.match(header_re, l):
            cols = [re.search(r'\s' + r + r'(\s|$)', l).start() + 1 for r in ('I', 'II', 'III', 'IV')]
            cur = None
            continue
        if cols is None or not l.strip():
            continue
        if not l.startswith(' ') or l.strip().startswith(('Master capability', 'Type:')):
            cols = None
            continue
        cells = [l[:cols[0]], l[cols[0]:cols[1]], l[cols[1]:cols[2]], l[cols[2]:cols[3]], l[cols[3]:]]
        cells = [c.strip() for c in cells]
        if cells[0]:
            cur = {'discipline': cells[0], 'ranks': cells[1:]}
            rows.append(cur)
        elif cur:
            cur['ranks'] = [(a + ' ' + b).strip() for a, b in zip(cur['ranks'], cells[1:])]
            if not any(cells[1:]):
                continue
    return rows


def professions(pages):
    tagged = flat(pages, 51, 67)
    names = [l.strip() for i, (_, l) in enumerate(tagged[:-1])
             if l.strip() and tagged[i + 1][1].strip().startswith('Type:')]
    out = []
    for b in split_on(tagged, set(names)):
        text = prose(b['lines'])
        head = re.match(r'Type: (.*?)\. Entry: (.*?)\. Tools: (.*?)\.', text)
        master = between(text, 'Master capability.', ['\u0000'])
        sw5e_sentences = [s for s in re.split(r'(?<=\.) ', master)
                          if re.search(r'SW5E|Extra Attack|damage die|AC |hit dice|feat|ability score|casting|stuns', s)]
        master_swg = ' '.join(s for s in re.split(r'(?<=\.) ', master) if s not in sw5e_sentences)
        if 'with a DC 20 relevant tool check and a real sample' in master_swg:  # Artisan
            sw5e_sentences.append('a DC 20 tool check (Artisan master reverse engineering)')
            master_swg = master_swg.replace('with a DC 20 relevant tool check and a real sample', 'from a real sample')
        if DC.search(master_swg):
            sw5e_sentences.append('a DC in: ' + master_swg)
            master_swg = DC.sub('', master_swg)
        out.append({'id': 'prof-' + re.sub(r'[^a-z0-9]+', '-', b['name'].lower()).strip('-'), 'name': b['name'],
                    'page': b['page'], 'type': head.group(1) if head else '', 'entry': head.group(2) if head else '',
                    'tools': head.group(3) if head else '', 'paths': table_rows(b['lines']),
                    'master_capability': master_swg, 'sw5e_removed': sw5e_sentences,
                    # Pikeman, Swordsman and Shipwright (JTL) are pre-CU professions with Core3 trainers.
                    'new_profession': b['name'] in {'Botanist', 'Pharmacist', 'Toxicologist', 'Cyberneticist',
                                                    'Archaeologist'},
                    'status': 'optional, not enabled'})
    return out


def npcs(pages):
    tagged = flat(pages, 84, 91)
    names = [l.strip() for i, (_, l) in enumerate(tagged[:-1])
             if l.strip() and re.match(r'^[A-Z][\w\'-]+.*; .*-style', tagged[i + 1][1].strip())]
    out = []
    for b in split_on(tagged, set(names)):
        text = prose(b['lines']).split(' A bounded simulation turn')[0]
        m = re.match(r'(.*?); (\w[\w\' -]*?)-style (.*?); experience level (\d+)\. Home scene: (.*?)\. Goal: (.*?)\. '
                     r'Loyalty: (.*?)\. Finite assets: (.*?)\. A leased asset is not an owned ship or unlimited facility\. '
                     r'Pressure: (.*?) Knowledge: (.*?) First scene \[H\]\. (.*?) Decision pattern \[H\]\. (.*?) '
                     r'Possible connection \[H\]\. (.*)', text)
        if not m:
            out.append({'name': b['name'], 'page': b['page'], 'parse_error': text[:200]})
            continue
        out.append({'id': 'npc-' + re.sub(r'[^a-z0-9]+', '-', b['name'].lower()).strip('-'), 'name': b['name'],
                    'page': b['page'], 'species': m.group(1), 'role': m.group(3), 'home_scene': m.group(5),
                    'goal': m.group(6), 'loyalty': m.group(7), 'assets': m.group(8), 'pressure': m.group(9),
                    'knowledge': m.group(10), 'first_scene': m.group(11), 'decision_pattern': m.group(12),
                    'connection': m.group(13),
                    'sw5e_removed': [f'SW5E class style "{m.group(2)}" and experience level {m.group(4)}'],
                    'in_game': next(('existing zone ' + z for p, z in OUR_ZONES.items() if p in m.group(5)), 'home world not in game yet'),
                    'status': 'optional, not enabled'})
    return out


def factions(pages):
    tagged = flat(pages, 73, 77)
    names = [l.strip() for i, (_, l) in enumerate(tagged[:-1])
             if l.strip() and tagged[i + 1][1].strip().startswith('Anchor')]
    out = []
    for b in split_on(tagged, set(names)):
        text = prose(b['lines']).split(' Faction turn ')[0]
        m = re.match(r'Anchor \[([^\]]+)\]\. (.*?) Local project \[H\]\. (.*?) Means: (.*?)\. Internal dispute: (.*?) '
                     r'Entry hook \[H\]\. (.*?) Local faces:', text)
        out.append({'id': 'faction-' + re.sub(r'[^a-z0-9]+', '-', b['name'].lower()).strip('-'), 'name': b['name'],
                    'page': b['page'], 'anchor_sources': m.group(1) if m else '', 'anchor': m.group(2) if m else '',
                    'local_project': m.group(3) if m else '', 'means': m.group(4) if m else '',
                    'internal_dispute': m.group(5) if m else '', 'entry_hook': m.group(6) if m else '',
                    'original': '[H]' in b['name'] or (m and m.group(1) == 'H'), 'status': 'optional, not enabled'})
    return out


def bestiary(pages):
    tagged = flat(pages, 95, 111)
    names = [l.strip() for i, (_, l) in enumerate(tagged[:-1])
             if l.strip() and tagged[i + 1][1].strip().startswith('Context [')]
    out = []
    for b in split_on(tagged, set(names)):
        text = prose(b['lines'])
        ctx = re.match(r'Context \[([^\]]+)\]\. (.*?) Role: (.*?)\. Size (\w+)\.', text)
        act = re.search(r'Distinct action \[H\]: (.*?)(?: All required saves|$)', text)
        husb = re.search(r'Husbandry / resources\. (.*?) Biological stock is finite', text)
        # Keep the behaviour's name as an idea; its wording is SW5E action economy (saves, recharge, strikes).
        idea = re.sub(r'^Proposed |\s*\[H\]', '', act.group(1).split(':')[0]).strip() if act else ''
        mechanics = act.group(1).strip() if act else ''
        out.append({'id': 'creature-' + re.sub(r'[^a-z0-9]+', '-', b['name'].lower()).strip('-'), 'name': b['name'],
                    'page': b['page'], 'source': ctx.group(1) if ctx else '', 'habitat': ctx.group(2) if ctx else '',
                    'role': ctx.group(3) if ctx else '', 'size': ctx.group(4) if ctx else '',
                    'special_behaviour_idea': idea, 'husbandry': husb.group(1) if husb else '',
                    'sw5e_removed': ['AC/HP/speed/CR/XP, ability scores, saves, attacks and damage dice',
                                     'special action wording: ' + mechanics],
                    'status': 'optional, not enabled'})
    return out


def main():
    pages = load_pages()
    data = {
        'source': {'title': 'Star Wars Galaxies x SW5E, Core Rulebook, expanded revision 3.0', 'date': '2026-10-07',
                   'author': 'the server owner', 'file': 'SWG_SW5E_Core_Expanded_v3.pdf',
                   'pdf_sha256': '5b6e1f701bafac96470ea701b2c29404fb58fd7a735d8f78656e9d01f10ce2ff',
                   'labels': {'L': 'supported Legends identity or history', 'C': 'supported Canon identity or history',
                              'H': 'proposed campaign rule or original content', 'AH': 'owner-approved campaign departure',
                              'U': 'unresolved, inactive until verified', 'I': 'imported, not locally extracted'}},
        'instruction': 'Owner, 14 Oct 2026: add all the SWG material as optional content; do not implement the SW5E rules.',
        'planets': planets(pages), 'schematics': schematics(pages), 'professions': professions(pages),
        'npcs': npcs(pages), 'factions': factions(pages), 'creatures': bestiary(pages)}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write('\n')
    for k in ('planets', 'schematics', 'professions', 'npcs', 'factions', 'creatures'):
        bad = [r.get('name') for r in data[k] if 'parse_error' in r]
        print(f'{k}: {len(data[k])}' + (f' (parse errors: {bad})' if bad else ''))


if __name__ == '__main__':
    main()
