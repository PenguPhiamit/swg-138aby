"""Creation sweep (functional-test-plan section 2): one new character for every species and gender the server offers,
each created through the agent client, logged in and read back, then deleted. It also covers the Hutt's open C54
items (F2: its racial row and limits; F3: its creation text) and the name filter in game (canon names allowed, whole
words).

Standalone, as root, TEST galaxy only. The account choice and the cleanup use the test galaxy's database; the client
bodies themselves run as swgemu:
  wsl -d Debian -u root -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/scenarios/creation-sweep.py
      [--data-only] [--keep] [--parallel N] [--accounts a,b,...]
--data-only runs the data checks and prints the plan without touching the galaxy (any user, Windows too). --keep leaves
the new characters in place. `creation-sweep.py cleanup Bot-reports/Creation/<time>-creation-sweep-rows.json` deletes
what an earlier run left behind. The report goes to Bot-reports/Creation/ like a squad run: a group with no members, kept
out of groups.json. Through squad.py (`run creation-sweep.py --group <any>`) only the data checks run unless squad runs
as root; options then come from CREATION_SWEEP_DATA_ONLY, _KEEP, _PARALLEL and _ACCOUNTS.

What it checks:
  data     the creation tables as the server reads them (our local_planets.tre first, stock behind it): 12 species with
           both genders; the Hutt's racial row and limits are S7's (C54 F2); its description is S7's text, and each
           description's attribute block shows the species' real racial row (C54 F3; the Chiss and the Hutt apart
           from the ten stock texts); the Hutt skill labels; the server's and the client's local_planets.tre are the
           same file; every starting item in the creation tables has a server template.
  names    refusals in game, which make no character: Admin, Dev, Captain, a reserved surname, a Wookiee surname, a
           3-letter Hutt name, digits, a name in use. Acceptances ride on the creations: names holding stock's old
           substring traps (Rebecca, Victor, Devon...), canon surnames stock refused (Skywalker, Solo, Fett, Vader), a
           canon first name, and a Hutt with a kajidic surname (Hutt name rules, not the Wookiee ones: C54 F1).
  create   one character per species and gender, the six starting professions four times each, on accounts that made
           no character in the last hour (Core3 allows one per account per hour, checked in the database, so a restart
           doesn't reset it). Each logs in; status() must show the template it asked for (object CRC, shown name and
           the database row) and starting attributes equal to profession_mods + racial_mods, all nine, current equal
           to maximum. The Hutts' attributes minus the profession row must be S7's row.
  clean    each new character is deleted with the login server's own two statements (LoginPacketHandler.cpp,
           handleDeleteCharacterMessage; the agent client has no delete action): its row moves to deleted_characters,
           and the zone purges the object on its next delete pass. Those statements only see the characters table,
           and a new character stays in characters_dirty until the zone's next save (about every 10 minutes), so
           the cleanup waits for that save; no body is logged in meanwhile.
  console  core3.log ERROR lines during the run that concern creation; the known harmless lines are counted apart.
"""
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOTS_DIR = HERE.parent
OUTPUTS = BOTS_DIR.parents[1]
sys.path.insert(0, str(OUTPUTS / 'tools'))
sys.path.insert(0, str(BOTS_DIR))
from swgfmt import trn_iff as iff, swg_tables as st  # noqa: E402
from fresh_start import events, template_crc  # noqa: E402

GROUP = 'Creation'
FOCUS = 'Character creation sweep: every species and gender, the Hutt (C54 F2/F3), the name filter in game'
CLIENT = '/opt/swg/Core3-dev/MMOCoreORB/build/dev/src/client/core3client'
CREDS = Path('/opt/swg/agent/bots')
SERVER_TRE = Path('/opt/swg/tre/local_planets.tre')  # first in the test galaxy's archive list (test_galaxy.py)
CLIENT_TRE = OUTPUTS / 'SWG-client' / 'local_planets.tre'
TESTGALAXY_BIN = Path('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin')
CORE3_LOG = TESTGALAXY_BIN / 'log' / 'core3.log'
CONFIG_LOCAL = TESTGALAXY_BIN / 'conf' / 'config-local.lua'
ROOT = Path('/var/tmp/swg-creation-sweep')  # run folders: options files and body logs (never under /opt/swg)
DB, GALAXY, LOGIN_PORT, RUN_AS = 'swgemu_test', 2, '46453', 'swgemu'
CLEANUP_WAIT = 17 * 60  # the zone saves about 15.5 minutes after a start, then every 10 (core3.log, 17 Oct)
LOAD_GROUPS = BOTS_DIR / 'load-groups.json'  # default accounts: the plain load-test bots, which no squad uses

SPECIES = ['human', 'zabrak', 'twilek', 'rodian', 'trandoshan', 'moncal', 'wookiee', 'bothan', 'ithorian', 'sullustan',
           'chiss', 'hutt']
STOCK_SPECIES = SPECIES[:10]  # the Chiss and the Hutt come from our local_planets.tre
PROFESSIONS = ['combat_brawler', 'combat_marksman', 'crafting_artisan', 'outdoors_scout', 'science_medic',
               'social_entertainer']
ATTRIBUTES = ['health', 'strength', 'constitution', 'action', 'quickness', 'stamina', 'mind', 'focus', 'willpower']
TABLES = {'racial': 'datatables/creation/racial_mods.iff', 'limits': 'datatables/creation/attribute_limits.iff',
          'professions': 'datatables/creation/profession_mods.iff', 'species_text': 'string/en/player_species.stf',
          'skl_n': 'string/en/skl_n.stf', 'skl_d': 'string/en/skl_d.stf'}
CREATION_ITEMS = ['creation/default_pc_equipment.iff'] + [f'creation/profession_defaults_{p}.iff' for p in PROFESSIONS]

# Fable S7 README 5.2 (approved), checked here independently of the archive builder: the Hutt's racial row, and its
# limits as the stock non-human rows derive them (min = 300 + mod, fixed ranges, total = the minimums + 1,800).
HUTT_RACIAL = [100, 150, 300, 0, 0, 50, 0, 0, 300]
HUTT_RANGES = [700, 200, 100, 700, 150, 100, 700, 200, 200]
HUTT_LIMITS = [v for m, r in zip(HUTT_RACIAL, HUTT_RANGES) for v in (300 + m, 300 + m + r)] + [
    sum(300 + m for m in HUTT_RACIAL) + 1800]
HUTT_TEXT_START = 'Slow to move and quick to count, the Hutts of Nal Hutta'  # S7 5.1, our own prose
HUTT_SKILL = ('Hutt Special Features', 'Hutt Abilities')  # skl_n / skl_d species_hutt (C54 F3)

# Names stock refused because a filter entry matched anywhere in the name ("ec", "ct", "dev", "gm", "mod", and the
# profane "christ" and "ass"); since dev 0f045a47 entries match whole words only. First names are unique per galaxy
# (deleted ones too, until a restart), so each trap has a pool; past the pool a syllable is added, keeping the trap.
TRAPS = [('"ec" inside a name', ['Rebecca', 'Declan', 'Cecily', 'Becca', 'Rhecan']),
         ('"ct" inside a name', ['Victor', 'Octavia', 'Hector', 'Victoria', 'Actaeon']),
         ('"dev" inside a name', ['Devon', 'Devlin', 'Devin', 'Devora', 'Devan']),
         ('"gm" inside a name', ['Sigmund', 'Dagmar', 'Sigmar', 'Ragmar', 'Agmon']),
         ('"mod" inside a name', ['Modesto', 'Amodeo', 'Modine', 'Modrin', 'Modan']),
         ('"christ" inside a name', ['Christopher', 'Christa', 'Christian', 'Christine', 'Christof']),
         ('"ass" inside a name', ['Cassandra', 'Cassius', 'Bassam', 'Lassen', 'Jassa'])]
CANON_SURNAMES = ['Skywalker', 'Solo', 'Fett', 'Vader']  # stock refused each (filed as profane); surnames repeat freely
CANON_FIRST = ['Lando', 'Leia', 'Carl', 'Yoda']  # stock refused each; a first name works once per galaxy
HUTT_SURNAMES = ['Desilijic', 'Besadii', 'Anjiliac']  # kajidics: Hutt rules allow a surname, Wookiee rules don't
SHORT_HUTT = ['Zor', 'Gub', 'Mog', 'Ruk', 'Jil', 'Pom', 'Nar', 'Dov']  # 3 letters: valid elsewhere, under Hutt's 4
REFUSALS = [  # (label, template, name pattern, failure code expected); {f}/{s} are fresh made-up names
    ('Admin', 'human_male', 'Admin {s}', 'name_declined_developer'),
    ('Dev as a whole word', 'human_female', 'Dev {s}', 'name_declined_developer'),
    ('Captain', 'zabrak_male', 'Captain {s}', 'name_declined_reserved'),
    ('Bank as a surname', 'twilek_female', '{f} Bank', 'name_declined_reserved'),
    ('a Wookiee surname', 'wookiee_male', '{f} {s}', 'name_declined_racially_inappropriate'),
    ('a 3-letter Hutt name', 'hutt_male', '{short}', 'name_declined_racially_inappropriate'),
    ('digits', 'rodian_male', '{f}9 {s}', 'name_declined_racially_inappropriate'),
    ('a name in use', 'human_male', '{taken} {s}', 'name_declined_in_use'),
]
SYLLABLES = ['ka', 'ren', 'tor', 'vel', 'an', 'dra', 'mi', 'sol', 'ith', 'or', 'bel', 'zan', 'lo', 'nar', 'te', 'vin',
             'ash', 'ul', 'ry', 'ko', 'mar', 'is', 'da', 'quel', 'tho', 'ser', 'ga', 'lin', 'ves', 'ro']
RESERVED = {'admin', 'admins', 'administrator', 'moderator', 'developer', 'staff', 'swgemu', 'swganh', 'human', 'wookiee',
            'wookie', 'zabrak', 'bothan', 'rodian', 'trandoshan', 'ithorian', 'kryat', 'bank', 'city', 'guild', 'citizens',
            'self', 'lord', 'medic', 'doctor', 'major', 'general', 'captain', 'officer', 'private', 'marshal', 'player',
            'system', 'emperor', 'loot'}
# core3.log ERROR lines that are not creation faults: the agent body's NetStatus packet, and the logout straight after
# a JSON creation (fresh-start-test.md, "Server errors").
CONSOLE_NOISE = ('handleNetStatusRequest', 'decreaseOnlineCharCount')
CONSOLE_CREATION = ('PlayerCreation', 'CreateCharacter', 'createCharacter', 'racial', 'NameManager', 'Create Error')


# ---- the creation data, as the server reads it ----

def read_table(rel):
    """(bytes, source): our local_planets.tre is first in the server's archive list; everything else is stock client
    data, read from the client's own archives (the same files the server lists)."""
    for archive in (SERVER_TRE, CLIENT_TRE):
        if archive.exists():
            data = iff.open_tre_entry(str(archive), rel)
            if data is not None:
                return data, archive.name
            break
    data = iff.client_file(rel)
    return data, iff.client_index().get(rel.lower()) if data is not None else None


def load_tables(read=read_table):
    found, sources = {}, {}
    for key, rel in TABLES.items():
        data, sources[key] = read(rel)
        if data is None:
            raise LookupError(f'{rel} is in no archive')
        found[key] = st.read_stf(data) if rel.endswith('.stf') else st.read_dtii(data)
    return tables_from(found, sources)


def tables_from(found, sources=None):
    """Plain dicts from decoded tables (read_dtii / read_stf results)."""
    racial = {}
    for row in found['racial']['rows']:
        for template in row[:2]:
            if template:
                racial[template] = list(row[2:11])
    limits, pairs = {}, []
    for row in found['limits']['rows']:  # the server's species list is this table's rows (loadRacialCreationData)
        male, female = row[0], row[1]
        pairs.append(((male or female).rsplit('_', 1)[0], male, female))
        for template in (male, female):
            if template:
                limits[template] = list(row[2:21])
    professions = {row[0]: list(row[1:10]) for row in found['professions']['rows']}
    text = {key: dict(st.stf_items(found[key])) for key in ('species_text', 'skl_n', 'skl_d')}
    return dict(racial=racial, limits=limits, pairs=pairs, professions=professions, sources=sources or {}, **text)


def expected_attributes(tables, template, profession):
    """PlayerCreationManager: the profession_mods row, then addRacialMods adds the racial row (all nine)."""
    prof, race = tables['professions'].get(profession), tables['racial'].get(template)
    if prof is None or race is None:
        return None
    return [p + r for p, r in zip(prof, race)]


def attribute_block(text):
    """The nine +N values in a creation description's ATTRIBUTES block, or None."""
    if not text or 'ATTRIBUTES' not in text:
        return None
    found = {k.lower(): int(v) for k, v in re.findall(r'\\>024(\w+):\s*\\>128\+?(-?\d+)', text.split('ATTRIBUTES', 1)[1])}
    return [found[a] for a in ATTRIBUTES] if all(a in found for a in ATTRIBUTES) else None


def data_checks(tables):
    """[(label, ok, detail)] for the creation data: the species list and C54 F2/F3."""
    out = []
    species = [p[0] for p in tables['pairs']]
    missing, extra = [s for s in SPECIES if s not in species], [s for s in species if s not in SPECIES]
    no_gender = [f'{s} {g}' for s, m, f in tables['pairs'] for g, t in (('male', m), ('female', f)) if not t]
    out.append(('data: the creation tables list the 12 species', not missing and not extra,
                f'{len(species)} rows; missing {missing or "none"}; extra {extra or "none"}; '
                f'genders without a template: {no_gender or "none"}'))
    racial = [tables['racial'].get(t) for t in ('hutt_male', 'hutt_female')]
    out.append(('data: Hutt racial row is S7 5.2 (C54 F2)', racial == [HUTT_RACIAL, HUTT_RACIAL],
                f'male {racial[0]}, female {racial[1]}; approved {HUTT_RACIAL}'))
    limits = [tables['limits'].get(t) for t in ('hutt_male', 'hutt_female')]
    out.append(('data: Hutt attribute limits follow S7 (C54 F2)', limits == [HUTT_LIMITS, HUTT_LIMITS],
                f'male {limits[0]}; expected {HUTT_LIMITS}'))
    text = tables['species_text'].get('desc_hutt', '')
    prose = text.split('ATTRIBUTES', 1)[0].strip()
    problems = ([] if prose.startswith(HUTT_TEXT_START) else ['not the S7 prose']) + (
        ['more than one paragraph (imported lore?)'] if '\n' in prose else []) + (
        [] if attribute_block(text) == HUTT_RACIAL else [f'attributes shown {attribute_block(text)}'])
    out.append(('data: Hutt creation text is S7 5.1 with the approved attributes (C54 F3)', not problems,
                '; '.join(problems) or f'{len(prose)} characters of prose, attributes {HUTT_RACIAL}'))
    for label, stock in (("data: our species' creation texts show their racial rows (C54 F3)", False),
                         ('data: stock creation texts show their racial rows (SOE text)', True)):
        wrong, plain, matched = [], [], 0
        for name, male, female in tables['pairs']:
            if (name in STOCK_SPECIES) != stock:
                continue
            shown, row = attribute_block(tables['species_text'].get(f'desc_{name}')), tables['racial'].get(male or female)
            if shown is None:
                plain.append(name)
            elif shown != row:
                wrong.append(f'{name} shows {shown}, row {row}')
            else:
                matched += 1
        out.append((label, not wrong, '; '.join(wrong) or f'{matched} match' +
                    (f'; no attribute block: {plain}' if plain else '')))
    labels = (tables['skl_n'].get('species_hutt'), tables['skl_d'].get('species_hutt'))
    out.append(('data: Hutt skill labels (C54 F3)', labels == HUTT_SKILL, f'{labels}'))
    return out


def starting_items(data):
    """[(player template, item template)] from a creation table of PTMP blocks (default_pc_equipment,
    profession_defaults_*), item paths as the server names them (no shared_)."""
    out = []
    for block in (c for c in iff.parse(data)[0].children[0].children if c.is_form and c.form == 'PTMP'):
        who = block.children[0].data.rstrip(b'\0').decode('latin-1').rsplit('/', 1)[-1]
        for chunk in block.children[1:]:
            found = re.search(rb'object/[a-z0-9_/]+\.iff', chunk.data)
            if found:
                out.append((who.replace('shared_', '').replace('.iff', ''), found.group(0).decode().replace('shared_', '')))
    return out


def starting_item_check(read=read_table, scripts=TESTGALAXY_BIN / 'scripts'):
    """Every item the creation tables hand out has a server template (else the server logs 'unknown template key'
    and the character goes without it)."""
    label = 'data: every starting item has a server template'
    if not scripts.exists():
        return label, None, 'the server scripts are not visible from here'
    missing, count = [], 0
    for rel in CREATION_ITEMS:
        for who, item in starting_items(read(rel)[0]):
            count += 1
            if not (scripts / item.replace('.iff', '.lua')).exists():
                missing.append(f"{Path(rel).stem.replace('profession_defaults_', '')} {who}: {item}")
    return label, not missing, '; '.join(missing) or f'{count} items in {len(CREATION_ITEMS)} tables'


def archive_check():
    """(label, ok or None when it can't be checked here, detail)."""
    label = "data: server and client local_planets.tre are the same file"
    if not SERVER_TRE.exists() or not CLIENT_TRE.exists():
        return label, None, 'one of the two archives is not visible from here'
    sums = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (SERVER_TRE, CLIENT_TRE)]
    return label, sums[0] == sums[1], f'server {sums[0][:8]}, client {sums[1][:8]}'


# ---- the plan: who is created, on which account, with which name ----

def made_word(rng, taken, low=4, high=12):
    while True:
        word = ''.join(rng.choice(SYLLABLES) for _ in range(rng.randint(2, 3))).capitalize()
        if low <= len(word) <= high and word.lower() not in taken and word.lower() not in RESERVED:
            return word


def fits(case, species):
    kind = case[0]
    if kind == 'hutt surname':
        return species == 'hutt'
    if kind == 'canon surname':
        return species not in ('hutt', 'wookiee')
    return species != 'hutt'  # the traps and the canon first name stay off the Hutts' own rules


def name_for(case, species, taken, rng):
    """(full name, the name case it carries or None)."""
    surname = None if species == 'wookiee' else made_word(rng, taken)
    if case is None:
        return ' '.join(filter(None, [made_word(rng, taken), surname])), None
    kind, value = case
    if kind == 'hutt surname':
        return f'{made_word(rng, taken)} {rng.choice(HUTT_SURNAMES)}', 'a Hutt kajidic surname (Hutt name rules, C54 F1)'
    if kind == 'canon surname':
        return f'{made_word(rng, taken)} {value}', f'canon surname {value}'
    if kind == 'canon first':
        first = next(n for n in CANON_FIRST if n.lower() not in taken)
        return ' '.join(filter(None, [first, surname])), 'canon first name'
    label, pool = value
    first = next((n for n in pool if n.lower() not in taken), None)
    while first is None or first.lower() in taken:
        first = (pool[0] + rng.choice(SYLLABLES))[:15]
    return ' '.join(filter(None, [first, surname])), label


def plan_characters(pairs, accounts, taken, rng):
    """One character per species and gender with a template; professions in turn (each four times for 24); the name
    cases placed on the first characters they fit. Returns (characters, cases left unplaced)."""
    chars = [{'species': s, 'gender': g, 'template': t} for s, male, female in pairs
             for g, t in (('male', male), ('female', female)) if t]
    if len(accounts) < len(chars):
        raise ValueError(f'{len(chars)} characters need as many free accounts; {len(accounts)} given')
    taken = set(taken)
    cases = [('hutt surname', None)] + [('trap', t) for t in TRAPS] + [('canon surname', s) for s in CANON_SURNAMES]
    if any(n.lower() not in taken for n in CANON_FIRST):
        cases.append(('canon first', None))
    for i, (char, account) in enumerate(zip(chars, accounts)):
        case = next((c for c in cases if fits(c, char['species'])), None)
        if case:
            cases.remove(case)
        char.update(profession=PROFESSIONS[i % len(PROFESSIONS)], account=account)
        char['name'], char['case'] = name_for(case, char['species'], taken, rng)
        taken.add(char['name'].split()[0].lower())
    return chars, cases


def plan_refusals(accounts, taken, in_use, rng):
    """The refused-name attempts, one account each (accounts make their own character only afterwards)."""
    taken, out = set(taken), []
    short = next((n for n in SHORT_HUTT if n.lower() not in taken), None)
    for (label, template, pattern, expect), account in zip(REFUSALS, accounts):
        if ('{taken}' in pattern and not in_use) or ('{short}' in pattern and not short):
            continue
        name = pattern.format(f=made_word(rng, taken), s=made_word(rng, taken), short=short, taken=in_use)
        taken.add(name.split()[0].lower())
        out.append({'label': label, 'template': template, 'name': name, 'expect': expect, 'account': account,
                    'profession': 'outdoors_scout'})
    return out


def choose_accounts(rows, now, needed, max_chars):
    """Accounts in the given order with no creation in the last 65 minutes and room for a character.
    rows: (username, account_id, characters, newest creation as a unix time)."""
    return [r for r in rows if now - int(float(r[3])) > 65 * 60 and int(r[2]) < max_chars - 1][:needed]


def minutes_to_wait(rows, now):
    """Minutes until the next account that made a character in the last 65 minutes is free again."""
    waits = [65 * 60 - (now - int(float(r[3]))) for r in rows if now - int(float(r[3])) <= 65 * 60]
    return min(waits) // 60 + 1 if waits else 0


# ---- reading a body's results ----

def creation_result(text):
    """What the create action's client log says: {'created': True, 'oid'} or {'created': False, 'code', 'message'}."""
    found = re.search(r'Character creation SUCCESS - OID: (\d+)', text)
    if found:
        return {'created': True, 'oid': int(found.group(1))}
    found = re.search(r'Error code: (\S+)', text)  # ClientCreateCharacterFailed: the name checks
    if found:
        return {'created': False, 'code': found.group(1)}
    found = re.search(r'Zone ERROR: (.*?) - ([^\r\n]*)', text)  # ErrorMessage: the hour limit, the character limit
    if found:
        return {'created': False, 'code': 'error_message', 'message': f'{found.group(1)}: {found.group(2).strip()}'}
    found = re.search(r'Character creation (timeout|error[^\r\n]*|- unknown response)', text)
    return {'created': False, 'code': 'no_reply', 'message': found.group(0) if found else 'no creation reply in the log'}


def attribute_problems(status, expected):
    me = status.get('me') or {}
    current, maximum = me.get('attributes'), me.get('max_attributes')
    if not isinstance(maximum, dict):
        return ['status() has no attributes (a body built before the nine-attribute status?)']
    if expected is None:
        return ['no expected attributes (profession or racial row missing)']
    problems = []
    for name, want in zip(ATTRIBUTES, expected):
        if maximum.get(name) != want:
            problems.append(f'{name} max {maximum.get(name)}, expected {want}')
        if isinstance(current, dict) and current.get(name) != maximum.get(name):
            problems.append(f'{name} {current.get(name)} of {maximum.get(name)}')
    return problems


def attributes_seen(row):
    maximum = ((row.get('status') or {}).get('me') or {}).get('max_attributes') or {}
    return [maximum.get(a) for a in ATTRIBUTES]


def judge(row, tables):
    """Problems with one created character ([] = pass)."""
    if not row.get('created'):
        return [f"not created: {row.get('code')} {row.get('message', '')}".strip()]
    if not row.get('login_s'):
        return [f"created (oid {row.get('oid')}) but no login: {row.get('login_error', '')}".strip()]
    problems = []
    want = template_crc(f"object/creature/player/shared_{row['template']}.iff")
    if row.get('crc') != want:
        problems.append(f"object CRC {row.get('crc')}, expected {want}")
    if row.get('shown_name') != row['name']:
        problems.append(f"shown name {row.get('shown_name')!r}")
    if 'db_template' in row and row['db_template'] is None:
        problems.append('no database row (characters or characters_dirty)')
    elif 'db_template' in row and row['db_template'] != f"object/creature/player/{row['template']}.iff":
        problems.append(f"database template {row['db_template']!r}")
    expected = expected_attributes(tables, row['template'], row['profession']) if tables else None
    return problems + attribute_problems(row.get('status') or {}, expected)


def hutt_s7_problems(row, tables):
    """The approved S7 row in game: attributes minus the profession row."""
    prof = tables['professions'].get(row['profession']) if tables else None
    seen = attributes_seen(row)
    if prof is None or None in seen:
        return ['no attributes or profession row to compare']
    racial = [s - p for s, p in zip(seen, prof)]
    return [] if racial == HUTT_RACIAL else [f'racial part {racial}, S7 {HUTT_RACIAL}']


def console_findings(lines, names, oids):
    """(creation-related ERROR lines, harmless known lines, other ERROR lines) from core3.log lines. An ERROR is ours
    when it names a creation step, one of our characters or OIDs, or follows one of those on the same server thread
    (e.g. a starting item that fails to create right after "Player <oid> logged in")."""
    ours, noise, other = [], 0, 0
    marks = list(CONSOLE_CREATION) + [n for n in names if n] + [str(o) for o in oids]
    last = {}  # server thread -> whether its previous line was about us
    for line in lines:
        thread = re.search(r'\) Thread (\d+) - ', line)
        thread = thread.group(1) if thread else None
        about_us = any(m in line for m in marks)
        if 'ERROR' in line:
            if any(n in line for n in CONSOLE_NOISE):
                noise += 1
                about_us = False
            elif about_us or last.get(thread):
                ours.append(line[:260])
                about_us = True
            else:
                other += 1
        if thread:
            last[thread] = about_us
    return ours, noise, other


def cleanup_where(oid, account_id, galaxy=GALAXY):
    """The WHERE clause of LoginPacketHandler::handleDeleteCharacterMessage, for one character."""
    return f'character_oid = {int(oid)} AND account_id = {int(account_id)} AND galaxy_id = {int(galaxy)}'


def cleanup_statements(oid, account_id, galaxy=GALAXY):
    where = cleanup_where(oid, account_id, galaxy)
    return [f'INSERT INTO deleted_characters SELECT *, 0 as db_deleted FROM characters WHERE {where};',
            f'DELETE FROM characters WHERE {where};']


# ---- the live part: database, bodies ----

def sql(query):
    return subprocess.run(['mariadb', '-Nse', query, DB], check=True, capture_output=True, text=True).stdout


def sql_rows(query):
    return [line.split('\t') for line in sql(query).splitlines() if line.strip()]


def account_rows(names):
    """(username, account_id, characters, newest creation) per account. A new character sits in characters_dirty
    until the zone's next save moves it into characters (ObjectManager::onCommitData), so all three tables count."""
    names = [n for n in names if re.fullmatch(r'[a-z0-9_]+', n)]
    if not names:
        return [], 0
    newest = ', '.join(f'COALESCE((SELECT UNIX_TIMESTAMP(max(t.creation_date)) FROM {table} t WHERE t.account_id = '
                       f'a.account_id AND t.galaxy_id = {GALAXY}), 0)'
                       for table in ('characters', 'characters_dirty', 'deleted_characters'))
    rows = sql_rows(
        'SELECT a.username, a.account_id, '
        f'(SELECT count(*) FROM (SELECT character_oid, account_id, galaxy_id FROM characters UNION SELECT '
        f'character_oid, account_id, galaxy_id FROM characters_dirty) c WHERE c.account_id = a.account_id AND '
        f'c.galaxy_id = {GALAXY}), GREATEST({newest}) '
        'FROM accounts a WHERE a.username IN (' + ', '.join(f"'{n}'" for n in names) + ')')
    order = {n: i for i, n in enumerate(names)}
    now = int(float(sql('SELECT UNIX_TIMESTAMP()').strip()))
    return sorted(rows, key=lambda r: order.get(r[0], 1e9)), now


def db_rows(oids):
    """{oid: (account_id, firstname, template, table)}: the characters row, or characters_dirty before the save."""
    if not oids:
        return {}
    listed, out = ','.join(str(int(o)) for o in oids), {}
    for table in ('characters_dirty', 'characters'):  # characters wins during the moment a save holds both
        for r in sql_rows(f'SELECT character_oid, account_id, firstname, template FROM {table} '
                          f'WHERE character_oid IN ({listed})'):
            out[int(r[0])] = (int(r[1]), r[2], r[3], table)
    return out


def delete_characters(created, ids, wait_s=CLEANUP_WAIT, rows=db_rows, run=sql, sleep=time.sleep):
    """Deletes this run's characters with the login server's two statements. Those only see the characters table, so
    a character is deletable once the zone's save has moved it there from characters_dirty (as for a player, who
    can't delete a new character before then either); this waits up to wait_s for that. Returns [(oid, state)]."""
    pending, states = {r['oid']: r for r in created}, {}
    deadline = time.time() + wait_s
    while pending:
        found = rows(list(pending))
        for oid, row in list(pending.items()):
            info = found.get(oid)
            if not info or info[0] != ids.get(row['account']) or info[1].lower() != row['name'].split()[0].lower():
                states[oid] = f'skipped: row {info} does not match the run'
            elif info[3] != 'characters':
                continue
            else:
                for statement in cleanup_statements(oid, info[0]):
                    run(statement)
                where = cleanup_where(oid, info[0])
                moved = int(run(f'SELECT count(*) FROM deleted_characters WHERE {where}').strip())
                left = int(run(f'SELECT count(*) FROM characters WHERE {where}').strip())
                states[oid] = 'deleted' if moved == 1 and left == 0 else f'moved {moved}, left {left}'
            del pending[oid]
        if not pending or time.time() >= deadline:
            break
        sleep(15)
    for oid in pending:
        states[oid] = f'still in characters_dirty after {wait_s} s: no save ran'
    return [(r['oid'], states[r['oid']]) for r in created]


def max_characters():
    try:
        found = re.search(r'MaxCharactersPerGalaxy\s*=\s*(\d+)', CONFIG_LOCAL.read_text())
        return int(found.group(1)) if found else 10
    except OSError:
        return 10


def default_accounts():
    spec = json.loads(LOAD_GROUPS.read_text(encoding='utf-8'))
    return [m['account'] for group in spec['groups'].values() for m in group['members']]


def galaxy_running():
    out = subprocess.run(['pgrep', '-x', 'core3'], capture_output=True, text=True).stdout.split()
    return any(Path(f'/proc/{p}/cwd').resolve() == TESTGALAXY_BIN for p in out if Path(f'/proc/{p}/cwd').exists())


def is_root():
    return os.name == 'posix' and os.geteuid() == 0


def as_swgemu():
    """Popen arguments that run a body as swgemu when we are root (bodies never run as root)."""
    return {'user': RUN_AS, 'group': RUN_AS, 'extra_groups': []} if is_root() else {}


def give_to_swgemu(*paths):
    if is_root():
        for path in paths:
            shutil.chown(path, RUN_AS, RUN_AS)


class Body:
    """One core3client for one account, in its own folder; a command waits for its own reply line."""

    def __init__(self, account, folder):
        self.account, self.dir = account, folder / account
        self.fifo, self.log = self.dir / 'in', self.dir / 'out.log'
        self.proc = self.holder = None
        self.offset = 0

    def env(self):
        acc = json.loads((CREDS / f'{self.account}.json').read_text())
        host = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
        env = dict(os.environ, CORE3_CLIENT_USERNAME=acc['username'], CORE3_CLIENT_PASSWORD=acc['password'],
                   CORE3_CLIENT_LOGINHOST=host, CORE3_CLIENT_LOGINPORT=LOGIN_PORT)
        if is_root():
            import pwd
            env['HOME'] = pwd.getpwnam(RUN_AS).pw_dir
        return env

    def launch(self, args):
        (self.dir / 'log').mkdir(parents=True, exist_ok=True)
        if not self.fifo.exists():
            os.mkfifo(self.fifo, 0o600)
        give_to_swgemu(self.dir.parent, self.dir, self.dir / 'log', self.fifo)
        self.holder = subprocess.Popen(f'exec sleep infinity > {self.fifo}', shell=True, start_new_session=True,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **as_swgemu())
        with open(self.fifo, 'rb') as stdin, open(self.log, 'wb') as out:
            self.proc = subprocess.Popen([CLIENT] + args, cwd=self.dir, env=self.env(), stdin=stdin, stdout=out,
                                         stderr=subprocess.STDOUT, start_new_session=True, **as_swgemu())
        self.offset = 0

    def text(self):
        return self.log.read_bytes().decode('utf-8', 'replace') if self.log.exists() else ''

    def new_rows(self):
        rows = []
        for raw in events(self.log, self.offset):
            try:
                rows.append(json.loads(raw))
            except ValueError:
                pass
        self.offset = self.log.stat().st_size
        return rows

    def ask(self, cmd, wait_s=10, **args):
        self.new_rows()
        try:  # non-blocking: a body that has exited has no reader, and a plain open() would hang
            fd = os.open(self.fifo, os.O_WRONLY | os.O_NONBLOCK)
        except OSError:
            return {'ok': False, 'error': 'body not running'}
        os.write(fd, (json.dumps(dict(args, cmd=cmd)) + '\n').encode())
        os.close(fd)
        deadline = time.time() + wait_s
        while time.time() < deadline:
            time.sleep(0.3)
            for row in self.new_rows():
                if row.get('reply') == cmd:
                    return row
        return {'ok': False, 'error': f'no reply in {wait_s} s'}

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.ask('quit', wait_s=1)
            try:
                self.proc.wait(5)
            except subprocess.TimeoutExpired:
                self.proc.terminate()
                try:
                    self.proc.wait(5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        if self.holder and self.holder.poll() is None:
            self.holder.terminate()
            self.holder.wait(5)

    def create(self, name, template, profession):
        """The client's JSON createCharacter action (skip tutorial); the client logs out once it has a reply."""
        self.dir.mkdir(parents=True, exist_ok=True)
        options = self.dir / 'options.json'
        options.write_text(json.dumps({'actions': [{'action': 'createCharacter', 'name': name, 'profession': profession,
                                                    'race': f'object/creature/player/{template}.iff',
                                                    'skipTutorial': True}]}))
        options.chmod(0o600)
        give_to_swgemu(options)
        began = time.time()
        self.launch(['--options-json', str(options)])
        try:
            self.proc.wait(120)
            exited = True
        except subprocess.TimeoutExpired:
            exited = False
        self.stop()
        text = self.text()
        (self.dir / f'create-{began:.0f}.log').write_text(text)  # refusals and the creation share a folder
        result = creation_result(text)
        result['create_s'] = round(time.time() - began, 1)
        if not exited and not result['created']:
            result['message'] = (result.get('message', '') + '; client still running after 120 s').lstrip('; ')
        return result

    def login(self, first, timeout=150):
        """Log the character in by first name; seconds until status() has its attributes, or None."""
        began = time.time()
        self.launch(['--character-firstname', first, '--agent-control'])
        while time.time() - began < timeout:
            time.sleep(1)
            if any('"ready"' in e for e in events(self.log)):
                break
            if self.proc.poll() is not None:
                return None
        else:
            return None
        while time.time() - began < timeout:  # baselines arrive just after "ready"
            status = self.ask('status')
            if ((status.get('me') or {}).get('max_attributes')):
                return round(time.time() - began, 1)
            time.sleep(1)
        return round(time.time() - began, 1)


def refuse_job(case, folder):
    body = Body(case['account'], folder)
    try:
        return dict(case, **body.create(case['name'], case['template'], case['profession']))
    except Exception as exc:  # recorded as a failure, never raised into the pool
        return dict(case, created=False, code='exception', message=repr(exc))
    finally:
        body.stop()


def create_job(char, folder):
    row, body = dict(char), Body(char['account'], folder)
    try:
        row.update(body.create(char['name'], char['template'], char['profession']))
        if not row['created']:
            return row
        row['login_s'] = body.login(char['name'].split()[0])
        if not row['login_s']:
            tail = [l.strip()[-160:] for l in body.text().splitlines() if 'ERROR' in l and 'getTemplate' not in l]
            row['login_error'] = ' / '.join(tail[-3:])
            return row
        status = body.ask('status')
        row['status'] = {k: status.get(k) for k in ('planet', 'x', 'y', 'cell', 'self', 'me', 'cash_credits',
                                                    'bank_credits')}
        own = body.ask('inspect', target=status.get('self'))
        row['crc'], row['shown_name'] = own.get('crc'), own.get('name')
        return row
    except Exception as exc:
        row['exception'] = repr(exc)
        return row
    finally:
        body.stop()


def options():
    env = os.environ
    return {'data_only': env.get('CREATION_SWEEP_DATA_ONLY') == '1', 'keep': env.get('CREATION_SWEEP_KEEP') == '1',
            'parallel': max(1, min(12, int(env.get('CREATION_SWEEP_PARALLEL', '8')))),
            'accounts': [a for a in env.get('CREATION_SWEEP_ACCOUNTS', '').split(',') if a]}


def plan_text(chars, refusals):
    lines = [f"  {c['template']:<18} {c['profession']:<19} {c['account']:<7} {c['name']}"
             + (f"   [{c['case']}]" if c['case'] else '') for c in chars]
    lines += [f"  refuse {r['template']:<11} {r['name']!r} -> {r['expect']}  ({r['label']}, {r['account']})"
              for r in refusals]
    return '\n'.join(lines)


def run(g):
    opts, stamp = options(), time.strftime('%Y%m%d-%H%M%S')
    record = {'stamp': stamp, 'options': opts}
    tables = None
    try:
        tables = load_tables()
        record['sources'] = tables['sources']
        for label, ok, detail in data_checks(tables):
            g.check(label, ok, detail)
    except Exception as exc:
        g.note(f'ERROR: creation tables unreadable: {exc!r}')
    for check in (archive_check, starting_item_check):
        try:
            label, ok, detail = check()
        except Exception as exc:
            g.note(f'ERROR: {check.__name__}: {exc!r}')
            continue
        if ok is None:
            g.note(f'{label}: not checked ({detail})')
        else:
            g.check(label, ok, detail)
    if tables is None:
        return
    if opts['data_only']:
        rng = random.Random(stamp)
        accounts = opts['accounts'] or [f'account{i:02}' for i in range(1, 25)]
        chars, unplaced = plan_characters(tables['pairs'], accounts, set(), rng)
        print('Plan (accounts and names are chosen again against the database in a live run):\n'
              + plan_text(chars, plan_refusals(accounts, set(), 'Existing', rng)))
        g.note('data only: no character created')
        return
    if not is_root() or not galaxy_running() or not Path(CLIENT).exists():
        g.note('BLOCKED: the live sweep runs standalone as root with the test galaxy up (root: '
               f'{is_root()}; galaxy: {galaxy_running() if os.name == "posix" else False}; client: {Path(CLIENT).exists()})')
        return
    g.checkpoint()

    # Accounts and names, from the database.
    rows, now = account_rows(opts['accounts'] or default_accounts())
    needed = sum(1 for _, m, f in tables['pairs'] for t in (m, f) if t)
    free = choose_accounts(rows, now, needed, max_characters())
    record['accounts'] = {r[0]: {'id': int(r[1]), 'characters': int(r[2])} for r in free}
    if len(free) < needed:
        g.note(f'BLOCKED: {len(free)} of {needed} accounts are free (one creation per account per hour); '
               f'the next is free in {minutes_to_wait(rows, now)} min')
        return
    taken = {r[0] for r in sql_rows('SELECT lower(firstname) FROM characters UNION SELECT lower(firstname) FROM '
                                    'characters_dirty UNION SELECT lower(firstname) FROM deleted_characters')}
    # The name in use is a sweep account's own bot character, never a player's.
    in_use = next(iter(r[0] for r in sql_rows(f'SELECT firstname FROM characters WHERE galaxy_id = {GALAXY} AND '
                                              f'account_id = {int(free[0][1])} ORDER BY character_oid LIMIT 1')), None)
    rng = random.Random(stamp)
    accounts = [r[0] for r in free]
    chars, unplaced = plan_characters(tables['pairs'], accounts, taken, rng)
    taken |= {c['name'].split()[0].lower() for c in chars}
    refusals = plan_refusals(accounts, taken, in_use, rng)
    record.update(plan=chars, unplaced=[c[0] for c in unplaced])
    for case in unplaced:
        g.note(f'name case not placed: {case[0]} {case[1] or ""}'.strip())
    log_from = CORE3_LOG.stat().st_size if CORE3_LOG.exists() else 0
    folder = ROOT / stamp
    folder.mkdir(parents=True, exist_ok=True)
    os.chmod(ROOT, 0o700)
    give_to_swgemu(ROOT, folder)
    began = time.time()

    # Refused names first (no character is made), then the creations, one job per account.
    with ThreadPoolExecutor(opts['parallel']) as pool:
        refused = list(pool.map(lambda c: refuse_job(c, folder), refusals))
    g.checkpoint()
    with ThreadPoolExecutor(opts['parallel']) as pool:
        made = list(pool.map(lambda c: create_job(c, folder), chars))
    record.update(refusals=refused, characters=made, sweep_s=round(time.time() - began))

    # The database rows of everything created (an unexpected acceptance included).
    created = [r for r in made + refused if r.get('created') and r.get('oid')]
    ids = {name: info['id'] for name, info in record['accounts'].items()}
    db = db_rows([r['oid'] for r in created])
    for row in created:
        row['db_template'] = db[row['oid']][2] if row['oid'] in db else None

    for row in refused:
        got = 'created' if row.get('created') else row.get('code')
        g.check(f"name filter refuses: {row['label']}", not row.get('created') and row.get('code') == row['expect'],
                f"{row['name']!r} as {row['template']}: {got} {row.get('message', '')}".strip())
    for row in made:
        problems = judge(row, tables)
        seen = '/'.join(str(v) for v in attributes_seen(row)) if row.get('status') else '-'
        g.check(f"create, log in, read back: {row['template']}", not problems,
                '; '.join(problems) if problems else
                f"{row['name']} ({row['account']}, {row['profession']}) {seen}, login {row['login_s']} s")
        if row['case']:
            g.check(f"name filter accepts: {row['case'].split(' (')[0]}", row.get('created'),
                    f"{row['name']!r} as {row['template']}: " +
                    ('created' if row.get('created') else f"{row.get('code')} {row.get('message', '')}".strip()))
        if row['species'] == 'hutt' and row.get('status'):
            problems = hutt_s7_problems(row, tables)
            g.check(f"Hutt S7 row in game: {row['template']}", not problems, '; '.join(problems) or
                    f"{seen} = {row['profession']} + {HUTT_RACIAL}")

    # Cleanup: the login server's own statements, only for characters this run made, row checked first; it waits
    # for the zone's save to move the new rows into characters (no bodies are logged in meanwhile).
    if created and not opts['keep']:
        waited = time.time()
        if getattr(g, 'control', None):
            g.control.publish('running', 'bodies done; cleanup waits for the zone save')
        deleted = delete_characters(created, ids)
        record['cleanup'] = deleted
        record['cleanup_wait_s'] = round(time.time() - waited)
        good = [oid for oid, state in deleted if state == 'deleted']
        g.check('cleanup: every new character moved to deleted_characters', len(good) == len(created),
                f"{len(good)} of {len(created)} after {record['cleanup_wait_s']} s waiting for the save; the zone "
                'purges them on its next delete pass' +
                ('; ' + '; '.join(f'{o}: {s}' for o, s in deleted if s != 'deleted') if len(good) < len(created) else ''))
    elif created:
        g.note(f'--keep: {len(created)} characters left in place: ' + ', '.join(r['name'] for r in created))

    # Console lines from the sweep.
    if CORE3_LOG.exists():
        with open(CORE3_LOG, 'rb') as stream:
            stream.seek(log_from)
            lines = stream.read().decode('utf-8', 'replace').splitlines()
        names = [r['name'].split()[0] for r in made + refused]
        ours, noise, other = console_findings(lines, names, [r['oid'] for r in created])
        record['console'] = {'creation_errors': ours, 'known_harmless': noise, 'other_errors': other}
        g.check('console: no creation errors in core3.log during the sweep', not ours,
                ' / '.join(ours[:3]) or f'{len(lines)} lines; known harmless {noise}; other ERROR lines {other} '
                '(not creation: other sessions share the log)')
    report = OUTPUTS / 'Bot-reports' / GROUP / f'{stamp}-creation-sweep-rows.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(record, indent=1, default=str), encoding='utf-8')
    g.note(f'rows: {report.name}; {sum(1 for r in made if r.get("created"))} of {len(made)} created in '
           f"{record['sweep_s']} s with {opts['parallel']} at a time")


def cleanup_command(path):
    """creation-sweep.py cleanup ROWS.json (root): delete what an earlier run left (e.g. it stopped before the save)."""
    path = Path(path)
    record = json.loads(path.read_text(encoding='utf-8'))
    created = [r for r in record.get('characters', []) + record.get('refusals', []) if r.get('created') and r.get('oid')]
    ids = {name: info['id'] for name, info in record['accounts'].items()}
    began = time.time()
    deleted = delete_characters(created, ids)
    record['cleanup_later'] = {'at': time.strftime('%Y-%m-%d %I:%M %p'), 'waited_s': round(time.time() - began),
                               'states': deleted}
    path.write_text(json.dumps(record, indent=1, default=str), encoding='utf-8')
    good = sum(state == 'deleted' for _, state in deleted)
    print(f'cleanup: {good} of {len(created)} moved to deleted_characters after {round(time.time() - began)} s')
    for oid, state in deleted:
        if state != 'deleted':
            print(f'  {oid}: {state}')


if __name__ == '__main__':
    argv = sys.argv[1:]
    if argv[:1] == ['cleanup']:
        sys.exit(cleanup_command(argv[1]))
    for flag, key in (('--data-only', 'CREATION_SWEEP_DATA_ONLY'), ('--keep', 'CREATION_SWEEP_KEEP')):
        if flag in argv:
            os.environ[key] = '1'
    for flag, key in (('--parallel', 'CREATION_SWEEP_PARALLEL'), ('--accounts', 'CREATION_SWEEP_ACCOUNTS')):
        if flag in argv:
            os.environ[key] = argv[argv.index(flag) + 1]
    import squad
    spec = squad.load_spec()
    spec['groups'][GROUP] = {'focus': FOCUS, 'members': []}
    results = {}
    squad.run_job(Path(__file__).resolve(), GROUP, spec, results)
    group, error, seconds, report = results[(Path(__file__).name, GROUP)]
    passed = sum(c['ok'] for c in group.checks)
    print(f'{GROUP}: {passed}/{len(group.checks)} checks passed in {seconds} s' + (f'; error: {error}' if error else ''))
    for check in group.checks:
        if not check['ok']:
            print(f"  FAIL {check['label']}: {check['detail']}")
    for note in group.notes:
        print(f'  note: {note}')
    print(f'report: {report}')
