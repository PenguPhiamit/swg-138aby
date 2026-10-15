"""One bounded profession run on the TEST galaxy; P0 always precedes judgement.

Run through squad.py --group Aurek --rounds 1 --round-minutes 30 --no-fallback.
CLASS_CHECK_PHASE=P0 (default) or P1..P6; CLASS_CHECK_PROFESSIONS=one_tree_name, or
Group:tree_name pairs (several groups in one invocation, each with its own profession).
CLASS_CHECK_GROUP optionally restricts the group. One profession per invocation;
an external loop can slice a phase without sharing grants between professions.
CLASS_CHECK_TESTER optionally names a group member. Default: a member whose
starting profession is the one under test (their kit and inventory fit it),
else the group leader.
CLASS_CHECK_MINUTES defaults to 23, maximum 23, leaving time for restoration.

Verdicts per ability (Claude-class-check/test-plan.md, section 5):
WORKS, RAN, NOT_GRANTED, NO_EFFECT, BLOCKED. NOT_GRANTED and NO_EFFECT are FAIL
checks; RAN and BLOCKED are notes only. Every result also carries gate_passed:
the command was sent and no "missing ability" (error 2) came back. The server
checks the ability before anything else (ObjectControllerImplementation.cpp,
activateCommand), so a BLOCKED result with gate_passed true still tells us the
profession holds the ability.
"""
import json
import hashlib
import math
import os
import re
import zlib
import time
from datetime import datetime
from pathlib import Path

GROUP = 'Aurek'
OUTPUTS = Path(__file__).resolve().parents[3]
VERDICTS = ('WORKS', 'RAN', 'NOT_GRANTED', 'NO_EFFECT', 'BLOCKED')
MISSING_PERFORMANCE = ('@performance:dance_lack_skill_self',
                       '@performance:music_lack_skill_song_self',
                       '@performance:music_lack_skill_instrument')
SETUP_MESSAGES = ('no_attack_wrong_weapon', 'no_attack_ranged_single', 'no_attack_melee_single',
                  'target_out_of_range', 'los_fail',
                  'no_line_of_sight', 'not_with_armor', 'no_help_target',
                  'healing_response_60', 'healing_response_61', 'healing_response_63',
                  'healing_must_wait', 'not_enough_mind', 'music_no_instrument',
                  'effect_not_performing', 'insufficient_skill', 'already_performing',
                  'not_performing', 'target_range', 'out_of_range', 'pvp_no_help',
                  '_noroom', 'inventory_full', 'not_enough_',
                  # healers: nothing to treat, or the wrong treatment for the patient
                  'no_state_to_heal', 'healing_response_72', 'healing_response_74', 'healing_response_a4',
                  'cannot_resuscitate_kit', 'too_dead_to_resuscitate', 'must_be_grouped', 'jedi_must_consent',
                  'healing_response_78', 'healing_response_80', 'must_be_near_droid', 'must_be_in_hospital',
                  'no_attrib_to_buff', 'conceal_nokit', 'effect_not_performing_correct', 'healing_response_a5', 'healing_response_a7', 'target_self_disallowed')
# Passive Tatooine animals only (pvpBitmask ATTACKABLE in bin/scripts/mobile/tatooine, so
# they fight back only once attacked), weakest first. The aggressive ones (scyk level 12,
# kreetle, sevorrt) incapacitated the tester on its first approach (15 Oct).
EASY = ('dwarf_eopie', 'gorg', 'worrt', 'rill', 'gorg_glutton', 'eopie')
# Passive but too strong to fight (cu pa level 11 hits for 125): never prey, and not a danger either
# because they only fight back when attacked. Anything else that is not in EASY counts as a danger.
PASSIVE_STRONG = ('cu_pa', 'dewback', 'bantha', 'womp_rat')
RIVAL_DISTANCE = 40           # an animal this close to another player is taken
DANGER_DISTANCE = 90          # do not search closer than this to wildlife that is not on the passive list
SAFE_DISTANCE = 60            # no other (unlisted, possibly aggressive) wildlife this close to the prey
TOWN = (3528, -4804)          # Mos Eisley, where the bots start and the controls run
PLATEAU = (3830, -4520)       # sevorrt plateau north-east of town: wildlife spawns around players
SEARCH = ((150, 0), (0, 0), (-120, -80), (0, -140))   # (150, 150) is scyk country: it killed three testers
# Success messages the generated tables lack (the handlers send them outside the files the
# generator reads). Each is a handler's "it started" line, read from the source.
EXTRA_SUCCESS = {
    'dragIncapacitatedPlayer': ('@healing_response:healing_response_b5',),  # "Attempting to drag %TT to your location..."

    'forage': ('@skl_use:sys_forage_start',),          # ForageManagerImplementation.cpp:111
    'maskscent': ('@skl_use:sys_scentmask_start',),    # MaskscentCommand.h:47
    # performance commands: what the entertainer sees when they take effect (seen live, 15 Oct)
    'sysgroup': ('Squad Leader ',),                     # the group listing it prints
    'stopDance': ('@performance:dance_stop_self',),
    'stopMusic': ('@performance:music_prepare_stop_self',),
    **{'flourish+%d' % n: ('@performance:flourish_perform',) for n in range(1, 9)},
}
# Abilities that leave a state or posture behind; they run last so the other probes
# do not have to wait for the state to wear off.
PERSISTENT = ('berserk1', 'berserk2', 'takeCover', 'aim', 'centerOfBeing', 'maskscent',
              'tumbleToProne', 'tumbleToKneeling', 'tumbleToStanding')
# What the healers say to the healer when it worked (plain text built in the handlers: HealDamage,
# QuickHeal, HealWound ("You heal X for N health wound damage."), HealState, FirstAid, HealEnhance, Drag).
# A command that fails silently (GENERALERROR, no message) unless something came first. surpriseShot
# needs the cover state (SurpriseShotCommand.h: !hasState(COVER) -> GENERALERROR); without it the
# probe would report NO_EFFECT for an ability that works.
LOS_OFFSETS = ((3, 0), (0, 3), (-3, -3))   # where the ally is moved when the healer cannot see it
# The server refuses these outside a hospital, a campsite or near a surgical droid (HealEnhanceCommand.h:94,
# HealWoundCommand.h:116, HealDroidWoundCommand.h:71); registerWithLocation needs a medical or entertainment
# building. Any cell of a hospital counts, so tester and partner walk into one first (Claude, 15 Oct).
MEDICAL_FACILITY = ('healEnhance', 'healWound', 'healDroidWound', 'registerWithLocation')
BUILDINGS = ('building:medical_or_entertainment',)
PRE_COMMAND = {'surpriseShot': 'takeCover'}
MUSIC_EFFECTS = ('firejet', 'ventriloquism')   # effects that only a song, not a dance, can carry
HEAL_TEXT = re.compile(r'^(You heal |You remove the |You apply |You enhance |You re-apply |'
                       r'You cure |Attempting to drag|Commenced drag)')
# /agentgear afflict kind for each setup tag a healer's patient needs (AgentGearCommand.h, afflict).
AFFLICT = {'affliction:wounds': 'wounds', 'affliction:battle_fatigue': 'fatigue', 'affliction:bleeding': 'bleeding',
           'affliction:disease': 'disease', 'affliction:poison': 'poison', 'affliction:fire': 'fire',
           'affliction:state': 'dizzy', 'incapacitated_friendly': 'incap', 'wounded_friendly': 'damage'}
# Wounds and battle fatigue stay on the partner for hours (they heal slowly) and cut its maximum HAM, so
# the group's bots were too weak to test after two healer runs. Off unless CLASS_CHECK_WOUNDS=1.
if os.getenv('CLASS_CHECK_WOUNDS') != '1':
    AFFLICT.pop('affliction:wounds')
    AFFLICT.pop('affliction:battle_fatigue')
# The state name the body reports for kinds that set a state (AgentControl.cpp stateNames).
AFFLICTION_STATE = {'poison': 'poisoned', 'disease': 'diseased', 'fire': 'on fire', 'bleeding': 'bleeding',
                    'dizzy': 'dizzy', 'stunned': 'stunned', 'blinded': 'blinded', 'intimidated': 'intimidated'}
INVISIBLE = ('wounds', 'fatigue')   # the body's status shows no wounds or shock: only the healer's text can prove a cure
BERSERK_SECONDS = 21                # Berserk1Command.h: setBerserkedState(20); the body does not list the berserk state
MIN_HEAL_RISE = 40            # natural regeneration adds about 12 per 3 s; a heal adds far more


def texts_of(events):
    return [str(e.get('text', '')) for e in events if e.get('event') == 'system']


def gate_passed(events):
    """The ability gate let the command through: it was sent and error 2 never came back."""
    if not any(e.get('reply') == 'command' and e.get('ok') for e in events):
        return False
    return not any(e.get('event') == 'command_failed' and e.get('error') == 2 for e in events)


def revoked(events):
    """The server refused the command because the ability is not held: error 2, or the per-name
    performance gate (a dance or song the character may not perform)."""
    return any(e.get('event') == 'command_failed' and e.get('error') == 2 for e in events) or any(
        key in text for key in MISSING_PERFORMANCE for text in texts_of(events))


def classify(entry, events, before=None, after=None, patient_before=None,
             patient_after=None, setup_verified=False, blocked=''):
    """Pure section-5 verdict; callers retain raw evidence independently.

    Attack spam must match this ability, not a stray autoattack. Unlabelled
    messages never become success evidence. HAM that only rose is natural
    regeneration and proves nothing. A silent opaque buff is RAN; a verified
    observable operation (or stub) with no result is NO_EFFECT.
    """
    if blocked:
        return 'BLOCKED', blocked
    texts = texts_of(events)
    failures = [e for e in events if e.get('event') == 'command_failed']
    if any(e.get('error') == 2 for e in failures) or any(
            key in text for key in MISSING_PERFORMANCE for text in texts):
        return 'NOT_GRANTED', 'missing ability / per-name performance gate after grant'
    if entry['test_kind'] == 'performance' and any(
            k in text for k in ('@performance:music_start_self', '@performance:dance_start_self') for text in texts):
        # The stop commands sent during setup answer late ("not performing"); the start message wins.
        return 'WORKS', 'performance start message'
    if any(k in text for k in EXTRA_SUCCESS.get(entry.get('ability'), ()) for text in texts):
        # forage says it started and then, with a full inventory, that there is no room for the find
        return 'WORKS', 'handler start message'
    invalid = {s.lower() for s in (entry.get('command_table') or {}).get('invalid_states', [])}
    states = (before or {}).get('states', [])
    if isinstance(states, list) and invalid.intersection(str(s).lower() for s in states):
        return 'BLOCKED', 'pre-command state rejected by command table: ' + ', '.join(states)
    if failures:
        return 'BLOCKED', 'command setup rejection: ' + json.dumps(failures)
    if any(e.get('reply') == 'error' or e.get('ok') is False for e in events):
        return 'BLOCKED', 'body request failed'
    if any(key in text for key in SETUP_MESSAGES for text in texts):
        return 'BLOCKED', 'setup message: ' + '; '.join(texts)
    message_keys = [m['key'] for m in entry.get('messages', [])]
    # The generated role guess mistakes the tumble results (tum_prone, tum_kneel,
    # tum_standing) for failures; they are the normal outcome.
    tumble = [k for k in message_keys if k.startswith('@cbt_spam:tum_')]
    failed_keys = [m['key'] for m in entry.get('messages', [])
                   if m.get('role_guess') == 'failure' and m['key'] not in tumble]
    if any(k in text for k in failed_keys for text in texts):
        return 'BLOCKED', 'handler failure (setup/roll): ' + '; '.join(texts)
    before, after = before or {}, after or {}
    pb, pa = patient_before or {}, patient_after or {}
    kind = entry['test_kind']
    success_keys = ([m['key'] for m in entry.get('messages', []) if m.get('role_guess') == 'success']
                    + tumble + list(EXTRA_SUCCESS.get(entry.get('ability'), ())))
    if kind == 'attack':
        keys = entry.get('combat_spam_keys') or []
        if any(e.get('event') == 'combat' and e.get('attacker_name') == 'me'
               and e.get('what') in keys and
               (not str(e.get('what')).endswith('_hit') or e.get('amount', 0) > 0)
               for e in events):
            return 'WORKS', 'matching outgoing combat hit/miss/evade/counter/block'
    elif kind == 'self':
        if any(k in text for k in success_keys for text in texts):
            return 'WORKS', 'handler success message'
        if any(e.get('event') == 'combat' and e.get('attacker_name') == 'me'
               and e.get('what') in success_keys for e in events):
            return 'WORKS', 'own combat spam for this command'
        if 'sui' in entry.get('setup_tags', []) and any(e.get('event') == 'sui_page' for e in events):
            return 'WORKS', 'window opened (setup tag sui)'
        if before.get('posture') and after.get('posture') and before['posture'] != after['posture']:
            return 'WORKS', 'own posture changed: %s -> %s' % (before['posture'], after['posture'])
        if isinstance(before.get('states'), list) and isinstance(after.get('states'), list):
            new = set(after['states']) - set(before['states']) - {'combat', 'peace'}
            if new:
                return 'WORKS', 'new own state: ' + ', '.join(sorted(new))
        elif before.get('states') is not None and after.get('states') is not None \
                and before['states'] != after['states']:
            return 'WORKS', 'own states changed'
        # Only a drop is evidence (a command's cost); a rise is regeneration. Damage
        # taken from a creature or being in combat would also lower it, so exclude both.
        hurt = any(e.get('event') == 'combat' and e.get('defender_name') == 'me' for e in events)
        in_combat = 'combat' in (before.get('states') or []) if isinstance(before.get('states'), list) else False
        drops = [pool for pool, old in (before.get('ham') or {}).items()
                 if old - (after.get('ham') or {}).get(pool, old) >= 3]
        if drops and not hurt and not in_combat:
            return 'WORKS', 'own HAM cost paid: ' + ', '.join(drops)
    elif kind in ('heal_other', 'target_friendly'):
        if entry.get('slash') == 'diagnose':
            # the window is the only evidence: the patient's HAM rising by itself proves nothing here
            if any(e.get('event') == 'sui_page' for e in events):
                return 'WORKS', 'diagnosis window opened'
        elif any(HEAL_TEXT.match(text) for text in texts):
            return 'WORKS', 'handler success message: ' + next(t for t in texts if HEAL_TEXT.match(t))
        elif any(pa.get(key, {}).get(pool, 0) - old >= MIN_HEAL_RISE
                 for key in ('ham', 'max_ham') for pool, old in pb.get(key, {}).items()):
            return 'WORKS', 'patient HAM/max HAM rose by %d or more' % MIN_HEAL_RISE
        if any(k in text for k in success_keys for text in texts):
            return 'WORKS', 'handler success message'
        lost = [st for st in (pb.get('states') or []) if st not in (pa.get('states') or []) and st not in ('combat', 'peace')]
        if lost:
            return 'WORKS', 'patient lost state: ' + ', '.join(lost)
        if pb.get('posture') in ('incapacitated', 'dead') and pa.get('posture') not in (None, 'incapacitated', 'dead'):
            return 'WORKS', 'patient got up: %s -> %s' % (pb['posture'], pa['posture'])
    elif kind == 'performance':
        # effects (spotlight, dazzle, smokebomb, firejet, ...) answer @performance:effect_perform_<name>
        keys = ['@performance:music_start_self', '@performance:dance_start_self',
                '@performance:effect_perform_'] + success_keys
        if any(k in text for k in keys for text in texts):
            return 'WORKS', 'performance message'
    elif kind == 'item':
        if any(e.get('event') in ('survey_results', 'survey_resources') for e in events):
            return 'WORKS', 'survey tool result'
        if entry.get('instrument_probe') and any('@performance:music_start_self' in t for t in texts):
            return 'WORKS', 'equipped instrument accepted by song gate'
    if not setup_verified:
        return 'BLOCKED', 'setup could not be verified'
    if any(e.get('event') in ('sui_page', 'posture', 'combat_started', 'combat_ended') for e in events):
        return 'RAN', 'response/state event observed; kind-specific success not proven'
    stub = (entry.get('handler') or {}).get('status') == 'template_stub'
    observable = (not entry.get('invisible_effect') and kind in ('attack', 'heal_other', 'target_friendly', 'item') or
                  bool(success_keys) or
                  (kind == 'performance' and entry.get('slash') in ('startDance', 'startMusic')))
    if not texts and (stub or observable):
        return 'NO_EFFECT', 'verified setup; no error, message or observable result in wait'
    return 'RAN', 'no failure; kind-specific success not observed'


def emit(g, result):
    verdict, ability = result['verdict'], result['ability']
    detail = result['reason']
    if verdict == 'BLOCKED':
        held = result.get('held')
        g.note(f'BLOCKED: {ability}: {detail}' + (' [ability held]' if held else ' [ability gate passed]' if
                                                   held is None and result.get('gate_passed') else ''))
    elif verdict == 'RAN':
        g.note(f'RAN: {ability}: {detail}')
    else:
        g.check(f'{verdict}: {ability}', verdict == 'WORKS', detail)


def save(g, report):
    report['counts'] = {v: sum(r['verdict'] == v for r in report['results']) for v in VERDICTS}
    report['gate_passed'] = sum(bool(r.get('gate_passed')) for r in report['results'])
    report['tries'] = len(report['results'])
    folder = OUTPUTS / 'Bot-reports' / g.name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / ('class-check-' + report['profession'] + '.json')
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    temp.replace(path)
    if report.get('finished'):
        stamp = report['started'].replace('-', '').replace(':', '').replace('T', '-').split('.')[0]
        snapshot = folder / (stamp + '-class-check-' + report['profession'] + '.json')
        snapshot.write_bytes(path.read_bytes())


def gear(bot, kit):
    # Intentionally bypass Bot.gear's carried-armour shortcut, after the grant.
    bot.slash('agentGear', kit, wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear] '), 8)
    try:
        return json.loads(answer['text'][12:])
    except (TypeError, KeyError, ValueError):
        return {'error': 'no valid kit answer'}


def kits_for(abilities, cmds):
    """Every /agentgear kit a run needs, basic first. Item kits come from the generated entries
    ('kits': carbine, polearm, twohand, medicine2, instruments, ...); the older three from the tags."""
    tried = [cmds[a] for a in abilities if cmds[a]['readiness'] in ('ready', 'needs_staging', 'needs_new_kit')]
    tags = {tag for e in tried for tag in e['setup_tags']}
    # basic (weapon, armor, stimpacks) only matters for fighting and stimpack healing; each call piles
    # a dozen more items into the inventory, which filled up in repeated runs.
    kits = ['basic'] if any(t.startswith('weapon:') or t in ('hostile_target', 'item:stimpack') for t in tags) else []
    if any(tag.startswith('item:instrument') or tag in ('item:stimpack', 'item:enhance_pack') for tag in tags):
        kits.append('support')
    if 'item:survey_tool' in tags:
        kits.append('survey')
    for e in tried:
        kits += [k for k in e.get('kits') or [] if k not in kits]
    return list(dict.fromkeys(kits))


# The one item a single-weapon kit leaves behind: when the tester still carries it, the kit is not asked
# for again. (Multi-item kits cannot be told apart by name, and a half-delivered kit must be asked again.)
KIT_MARKER = {'carbine': 'carbine_cdef', 'polearm': 'lance_staff_wood_s1', 'twohand': 'axe_heavy_duty'}

# Names are client STF keys, not the kit reply's template-path list.
MEDICINE = {'curePoison': 'cure_poison', 'cureDisease': 'cure_disease',
            'extinguishFire': 'fire_blanket', 'healEnhance': 'enhance',
            'revivePlayer': 'revive', 'healState': 'medic_dizzy',  # @medicine_name:medic_dizzy_a, not medpack_
            'applyPoison': 'poison_health', 'applyDisease': 'disease_health'}
ITEM_NAMES = {'stimpack': 'stimpack', 'wound_pack': 'wound',
              'enhance_pack': 'enhance', 'revive_pack': 'revive'}


def required_items(entry):
    if entry['ability'] in MEDICINE:
        return [MEDICINE[entry['ability']]]
    return [ITEM_NAMES[t[5:]] for t in entry.get('setup_tags', [])
            if t.startswith('item:') and t[5:] in ITEM_NAMES]


def make_room(bot, issued, keep, reserve=40):
    """Bank or drop only observed new kit OIDs; never infer ownership from names.

    Keep one copy of each required item, and all gear present before the run.
    Spare copies (the second and later item of the same name in the inventory) may be banked, never dropped:
    on 15 Oct Jesh carried 59 items from earlier runs (three bone armour sets, seven stimpacks), so the
    35-item medicine kit did not fit and healState was BLOCKED for a missing dizzy pack (Claude).
    """
    evidence = []
    items = bot.inventory().get('items', [])
    protected = {matches[0]['oid'] for token in keep
                 if (matches := matching(items, token))}
    inventory = next((i['oid'] for i in items if str(i.get('name', '')).endswith(':inventory')
                      and i.get('parent') == bot.oid), None)
    seen, spare = set(), set()
    for item in items:
        if inventory is not None and item.get('parent') == inventory:
            if item.get('name') in seen:
                spare.add(item['oid'])
            seen.add(item.get('name'))
    bank = next((i for i in items if str(i.get('name', '')).endswith(':bank')
                 and i.get('parent') == bot.oid), None)
    bank_ready = False
    def occupancy():
        current = bot.inventory().get('items', [])
        stored = {bank['oid']} if bank else set()
        for _ in range(32):
            more = {i['oid'] for i in current if i.get('parent') in stored} - stored
            if not more:
                break
            stored.update(more)
        return sum(i.get('oid') not in stored for i in current)
    for item in items:
        if occupancy() <= 80 - reserve:
            break
        oid = item.get('oid')
        if (oid not in issued and oid not in spare or oid in protected or item.get('parent') == bot.oid
                or bank and item.get('parent') == bank['oid']):
            continue
        if bank:
            if not bank_ready:
                terminals = bot.locate('terminal_bank', radius=800)
                if terminals:
                    trip = bot.go(terminals[0])
                    evidence.append(dict(bank_trip=trip))
                    bank_ready = bool(trip.get('arrived'))
            if bank_ready:
                events = bot.slash('transferItemMisc', f"{bank['oid']} -1 0 0 0", target=oid, wait=1)
                moved = any(i.get('oid') == oid and i.get('parent') == bank['oid']
                            for i in bot.inventory().get('items', []))
                evidence.append(dict(oid=oid, name=item.get('name'), bank=bank['oid'], moved=moved, events=events))
                if moved:
                    continue
        if oid not in issued:  # a spare copy from an earlier run: banked or kept, never dropped
            continue
        menu = bot.radial(oid)
        drop = next((r for r in menu.get('items', []) if r.get('name') == 'item_drop'), None)
        if drop is None:
            evidence.append(dict(oid=oid, blocked='no drop radial'))
            continue
        events = bot.select(oid, drop['radial_id'])
        gone = not any(i.get('oid') == oid for i in bot.inventory().get('items', []))
        evidence.append(dict(oid=oid, name=item.get('name'), dropped=gone, events=events))
    return evidence


def provision(bot, kits, entries, report):
    kits = list(kits)
    if 'medicine2' in kits and 'support' in kits:
        # The fire blanket is last in medicine2. Give the treatment kit the
        # available slots before support's duplicate armour and enhancements.
        kits.remove('medicine2')
        kits.insert(kits.index('support'), 'medicine2')
    issued = set()
    keep = {token for e in entries for token in required_items(e)}
    report['issued_items'] = []
    report['inventory_room'] = []
    answers = {}
    for kit in kits:
        # Reuse the medicines already carried; a kit is not an instruction to
        # fill every free slot with duplicate packs on every run.
        relevant = [e for e in entries if (kit == 'medicine2' and kit in (e.get('kits') or []))
                    or (kit == 'support' and any(t in e.get('setup_tags', [])
                                                for t in ('item:enhance_pack', 'item:stimpack')))]
        needed = {token for e in relevant for token in required_items(e)}
        if needed and all(carried(bot, token) for token in needed):
            answers[kit] = {'skipped': 'required medicines already carried', 'items': sorted(needed)}
            continue
        report['inventory_room'] += make_room(bot, issued, keep)
        before = {i['oid'] for i in bot.inventory().get('items', [])}
        answers[kit] = ({'skipped': 'already carried ' + KIT_MARKER[kit]}
                        if kit in KIT_MARKER and carried(bot, KIT_MARKER[kit]) else gear(bot, kit))
        new = [i for i in bot.inventory().get('items', []) if i['oid'] not in before]
        issued.update(i['oid'] for i in new)
        report['issued_items'] += new
    return answers


def short_name(obj):
    return str(obj.get('name', ''))


def species(obj):
    """The creature key after '@mob/creature_names:' ('' for anything else)."""
    name = short_name(obj)
    return name.split(':', 1)[1] if name.startswith('@mob/creature_names:') else ''


def alive(obj):
    # Exact species only: 'mountain_worrt' (250 damage a hit) is not a worrt.
    return species(obj) in EASY and obj.get('posture') == 'upright'


def hazard(obj):
    """Wildlife that might attack unprovoked: not prey and not known to be passive."""
    return wildlife(obj) and species(obj) not in EASY and species(obj) not in PASSIVE_STRONG


def wildlife(obj):
    """Any live ordinary creature (not a player, droid or named NPC), passive or not."""
    return short_name(obj).startswith('@mob/creature_names:') and obj.get('posture') == 'upright'


def prey(bot, radius=150):
    """The weakest passive animal in sight that has no other wildlife (possibly aggressive)
    within SAFE_DISTANCE; walking up to such an animal is what got the tester killed."""
    seen = bot.look(radius, 'CREO', 400)
    others = [o for o in seen if hazard(o)]
    # Another squad group may be hunting here at the same time (groups run in parallel): an animal
    # with a player close by belongs to them.
    rivals = [o for o in seen if not short_name(o).startswith('@') and o.get('oid') != bot.oid
              and 'helper R2 unit' not in short_name(o) and o.get('posture') == 'upright']

    def crowded(o):
        return any(math.hypot(o.get('x', 0) - p.get('x', 1e9), o.get('y', 0) - p.get('y', 1e9)) < SAFE_DISTANCE
                   for p in others)

    def contested(o):
        return any(math.hypot(o.get('x', 0) - p.get('x', 1e9), o.get('y', 0) - p.get('y', 1e9)) < RIVAL_DISTANCE
                   for p in rivals)

    objects = [o for o in seen if alive(o) and not crowded(o) and not contested(o)]
    objects.sort(key=lambda o: (EASY.index(species(o)), o.get('distance', 999)))
    return objects[0] if objects else None


def search_start(group_name):
    """Where in SEARCH a group starts, so groups hunting at the same time spread out."""
    return zlib.crc32(group_name.encode()) % len(SEARCH)


def stage_wildlife(bot, start=0):
    """Walk to the sevorrt plateau and look for passive wildlife there.

    The server's object search (locate) only sees the static decoration creatures
    of the world snapshot, never live spawns, so it cannot find prey (15 Oct).
    Live creatures spawn around players, as aurek-hunt.py found: walk, then look. Search points
    within DANGER_DISTANCE of aggressive or strong wildlife already seen are skipped (two testers
    were killed walking up to a scyk), and a tester that goes down stops the search.
    """
    tried, danger = [], []
    for dx, dy in SEARCH[start:] + SEARCH[:start]:
        x, y = PLATEAU[0] + dx, PLATEAU[1] + dy
        if any(math.hypot(x - t['x'], y - t['y']) < DANGER_DISTANCE for t in danger):
            tried.append(dict(at=[x, y], skipped='aggressive or strong wildlife close to this point'))
            continue
        move = bot.walk(x, y)
        tried.append(dict(at=[x, y], arrived=bool(move.get('arrived')), seconds=move.get('seconds')))
        if bot.status().get('me', {}).get('posture') in ('incapacitated', 'dead'):
            return dict(blocked='the tester went down while searching', tried=tried)
        for pause in (0, 10, 10):
            if pause:
                bot.idle(pause)
            found = prey(bot)
            if found:
                return dict(found=found, tried=tried)
            danger += [dict(x=o.get('x', 0), y=o.get('y', 0)) for o in bot.look(150, 'CREO', 400)
                       if hazard(o)]
    return dict(blocked='no ordinary small wildlife within 150 m of any plateau search point', tried=tried)


def call(bot, entry, target=0, wait=None):
    ability = entry['ability']
    args = entry.get('args') or (ability.split('+', 1)[1] if '+' in ability else '')
    command = entry.get('slash')
    if command == 'startDance' and not args:
        args = 'basic'
    if command == 'startMusic' and not args:
        args = 'starwars1'
    seconds = wait if wait is not None else max(3, 2 * (entry.get('command_table') or {}).get('default_time', 1.5))
    return bot.slash(command, args, target=target, wait=min(12, seconds))


def clear_ok(bot):
    cleared = bot.clear_professions()
    listed = bot.profession('list')
    return not cleared.get('error') and not cleared.get('failed') and not listed.get('error'), cleared, listed


def controls(g, bot, ally, cmds):
    ok, cleared, listed = clear_ok(bot)
    data = {'clear': cleared, 'list': listed, 'probes': []}
    if not ok:
        g.note('BLOCKED: P0 clear/list failed')
        return False, data
    # Ability rejection occurs before target validation, so any live creature (or none)
    # serves the negative probe; positive attacks use wildlife only.
    target = prey(bot) or bot.find('', radius=100, type='CREO', where=lambda o:
                                  o.get('posture') == 'upright' and
                                  (str(o.get('name', '')).startswith('@mob/creature_names:')
                                   or 'helper R2 unit' in str(o.get('name', ''))))
    if target is None:
        g.note('P0 negative attack control uses target 0: no live creature in range (the ability check precedes the target check)')
    ally.status()
    all_ok = True
    for ability, oid in [('unarmedHit1', target['oid'] if target else 0), ('healDamage', ally.oid)]:
        events = call(bot, cmds[ability], oid)
        passed = any(e.get('event') == 'command_failed' and e.get('error') == 2 for e in events)
        # Bots of other groups stand in the same square and their combat spam reaches this body too:
        # only an attack by this bot counts.
        passed = passed and not any(e.get('event') == 'combat' and e.get('attacker_name') == 'me' for e in events)
        g.check('P0 rejects ' + ability + ' after clear', passed, events)
        data['probes'].append(dict(ability=ability, passed=passed, events=events))
        all_ok = all_ok and passed
    events = bot.slash('stopDance', wait=3)
    passed = any('@performance:dance_not_performing' in str(e.get('text', '')) for e in events)
    g.check('P0 positive message control', passed, events)
    data['probes'].append(dict(ability='stopDance', passed=passed, events=events))
    data['passed'] = all_ok and passed
    return data['passed'], data


# Weapon tag -> stock templates to look for, best first. The species certs let every character
# use pistol, carbine and rifle cdef, knife_stone, axe_heavy_duty and lance_staff_wood_s1
# (matrix.md, "Weapon classes"); the brawler starting items hold the last three.
# 'unarmed' means no weapon in hand (unequip).
WEAPONS = {'ranged': ('rifle_cdef', 'pistol_cdef'), 'rifle': ('rifle_cdef',), 'pistol': ('pistol_cdef',),
           'carbine': ('carbine_cdef',), '1h melee': ('knife_dagger', 'knife_stone'),
           'melee_or_unarmed': ('knife_dagger', 'knife_stone'), '2h melee': ('axe_heavy_duty',),
           'polearm': ('lance_staff_wood_s1',), 'unarmed': (),
           # item kits (dev 60ed8971): heavy and lightsaber templates
           'special heavy (flame/acid/lightning beam)': ('heavy_acid_beam', 'heavy_lightning_beam', 'rifle_flame_thrower'),
           '1h lightsaber': ('sword_lightsaber_one_handed',), '2h lightsaber': ('sword_lightsaber_two_handed',),
           'polearm lightsaber': ('sword_lightsaber_polearm',),
           'lightsaber': ('sword_lightsaber_one_handed', 'sword_lightsaber_two_handed', 'sword_lightsaber_polearm')}


def tokens_of(tokens):
    return (tokens,) if isinstance(tokens, str) else tuple(tokens)


def squash(text):
    """Lower case without underscores: ability 'flutedroopy' must find the template 'flute_droopy'."""
    return re.sub(r'[^a-z0-9]', '', str(text).lower())


# Instrument tags (item:instrument:<ability>) whose template is spelled differently.
INSTRUMENT_ALIASES = {'omnibox': ('omnibox', 'ommnibox')}


def matching(items, tokens):
    """Items whose name contains a token (underscores ignored), in token order."""
    return [i for t in tokens_of(tokens) for i in items if squash(t) in squash(i.get('name'))]


def carried(bot, tokens):
    found = matching(bot.inventory().get('items', []), tokens)
    return found[0] if found else None


def weapon_route(bot, tag):
    """True when the tester can get this weapon tag into its hands: carries a stock weapon of
    the class, or (unarmed) can put its weapon away."""
    tokens = WEAPONS.get(tag[7:])
    return tokens is not None and (tag == 'weapon:unarmed' or bool(carried(bot, tokens)))


def equip(bot, tokens, swap_out=False):
    """Put the first carried item matching tokens into the hands and confirm its parent is the
    character. swap_out: put whatever is in hand away first. Instruments and weapons share the hold
    slot and the server's own swap fails for an instrument ("could not add Instrument ...
    containmentType: 4", seen 15 Oct on Dova)."""
    tokens = tokens_of(tokens)
    items = bot.inventory().get('items', [])
    matches = matching(items, tokens)
    if not matches:
        return False, {'error': 'missing ' + '/'.join(tokens)}
    bot.status()
    # An item already in hand needs no transfer.
    held = next((i for i in matches if i.get('parent') == bot.oid), None)
    if held:
        return True, {'item': held, 'already_equipped': True}
    item = matches[0]
    away = unequip(bot)[1] if swap_out else None
    events = bot.slash('transferItemWeapon', f'{bot.oid} 4 0 0 0', target=item['oid'], wait=1)
    items = bot.inventory().get('items', [])
    found = next((i for i in items if i.get('oid') == item['oid']), {})
    # Container is exposed by the body; the follow-up command also reports wrong weapon.
    return found.get('parent') == bot.oid, {'item': found, 'events': events, 'put_away_first': away}


def unequip(bot):
    """Put the weapon in hand back into the inventory (transferItemMisc, containment -1,
    TransferItemMiscCommand.h:351 clears the weapon): the body is then unarmed."""
    bot.status()

    def in_hand(items):
        # unknown_weapon is the bare hand; an instrument is a TANO named @obj_n:obj_<name>
        return [i for i in items if i.get('parent') == bot.oid and 'unknown_weapon' not in str(i.get('name'))
                and (i.get('type') == 'WEAO' or str(i.get('name')).startswith('@obj_n:obj_'))]

    items = bot.inventory().get('items', [])
    hands = in_hand(items)
    if not hands:
        return True, {'already_unarmed': True}
    box = next((i for i in items if i.get('name') == '@item_n:inventory' and i.get('parent') == bot.oid), None)
    if not box:
        return False, {'error': 'inventory container not found'}
    events = []
    for item in hands:
        events += bot.slash('transferItemMisc', f"{box['oid']} -1 0 0 0", target=item['oid'], wait=1)
    left = in_hand(bot.inventory().get('items', []))
    return not left, {'put_away': [i.get('name') for i in hands], 'still_in_hand': left, 'events': events}


def close_enough(bot, obj, distance=3, tries=4):
    """Walk up to obj (a few bounded legs, re-reading its position each time).
    The creature is up to 150 m away and may wander, so one 20 s leg is not enough."""
    current = obj
    for _ in range(tries):
        if current.get('distance', 999) <= distance:
            return current
        bot.go(current, timeout=30)
        current = next((o for o in bot.look(150, 'CREO', 400) if o['oid'] == obj['oid']), None)
        if current is None or current.get('posture') != 'upright':
            return None
    return current if current.get('distance', 999) <= distance else None


def survey_tool(bot):
    """Exercise the real survey ability gate separately from the slash stub."""
    tool = next((i for i in bot.inventory().get('items', [])
                 if 'survey_tool_mineral' in str(i.get('name'))), None)
    if not tool:
        return dict(verdict='BLOCKED', reason='mineral survey tool missing', events=[])
    events = bot.select(tool['oid'], 20, wait=3)
    if not any(e.get('event') == 'survey_resources' for e in events) \
            and not any('insufficient_skill' in t for t in texts_of(events)):
        # A newly granted surveyor first chooses a range. Only answer the range
        # page opened by this tool; never an unrelated helper or clone page.
        pages = bot.sui_pages().get('pages', [])
        ranges = [p for p in pages if 'survey' in json.dumps(p).lower()
                  and 'range' in json.dumps(p).lower() and 'dataList' in json.dumps(p)]
        if ranges:
            bot.sui_respond(ranges[-1]['page_id'], 0, ['0'], wait=1)
            events += bot.select(tool['oid'], 20, wait=3)
    # The tool itself checks hasAbility("survey") (SurveyToolImplementation.cpp:45) and answers
    # insufficient_skill: for this probe that message means the ability is not granted.
    if any('@error_message:insufficient_skill' in t for t in texts_of(events)):
        return dict(verdict='NOT_GRANTED', reason='survey tool refused: ability survey missing', events=events, tool=tool)
    verdict, reason = classify(dict(test_kind='item', messages=[]), events, setup_verified=True)
    return dict(verdict=verdict, reason=reason, events=events, tool=tool)


def afflict(bot, kind, target=0):
    """/agentgear afflict <kind> on the bot itself (target 0) or on an agent-account target. The reply
    carries the patient's states bitmask, wounds, ham, shock and posture."""
    bot.slash('agentGear', 'afflict ' + kind, target=target, wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear] '), 8)
    try:
        return json.loads(answer['text'][len('[agentgear] '):])
    except (TypeError, KeyError, ValueError):
        return {'error': 'no valid afflict answer'}


def wait_clean(bot, limit=90):
    """Wait, bounded, until the bot carries none of the states afflict can set."""
    for _ in range(limit // 5 + 1):
        states = bot.status().get('me', {}).get('states') or []
        if not set(AFFLICTION_STATE.values()) & set(states):
            return True
        bot.idle(5)
    return False


def patient_problem(kinds, patient):
    """The treatment still has something to treat at the instant of the probe."""
    if 'dead' in kinds:
        return None if patient.get('posture') == 'dead' else 'not dead after the incapacitations (%s)' % patient.get('posture')
    if patient.get('posture') == 'dead':
        return 'dead after afflict'
    for kind in kinds:
        state = AFFLICTION_STATE.get(kind)
        if state and state not in (patient.get('states') or []):
            return 'afflict %s did not set the state %s (or it expired)' % (kind, state)
        if kind == 'incap' and patient.get('posture') != 'incapacitated':
            return 'afflict incap left it %s' % patient.get('posture')
        if kind == 'damage' and patient.get('ham', {}).get('health', 0) >= .8 * patient.get('max_ham', {}).get('health', 1):
            return 'afflict damage left it above 80% health'
    return None


def hospital_room(bot, ctx):
    """A cell and local spot inside the nearest hospital, from any object the server's search finds in it
    (as aurek-doctor-buffs.py does; in Mos Eisley that is cell 9655496). Cached per run. None if none is found."""
    if 'hospital_room' not in ctx:
        ctx['hospital_room'] = None
        hospitals = bot.locate('hospital', radius=2000)
        for text in ('object/mobile', 'object/tangible') if hospitals else ():
            found = [r for r in bot.locate(text, radius=40, x=hospitals[0]['x'], y=hospitals[0]['y'])
                     if r.get('cell') and r.get('local') and r.get('building') == hospitals[0].get('oid')]
            if found:
                ctx['hospital_room'] = found[0]
                break
    return ctx['hospital_room']


def walk_into(room, *bots):
    """Walk each bot to its own spot in the room's cell; True when all arrived."""
    local = room['local']
    trips = [b.walk(local['x'] + 1.0 + i, local['y'] + 1.0, local['z'], room['cell'], tries=3) for i, b in enumerate(bots)]
    return all(isinstance(t, dict) and t.get('arrived') for t in trips), trips


def kill(ally, setup, limit=75):
    """Revive needs a dead patient. The third incapacitation inside 10 minutes kills, as in combat
    (PlayerManagerImplementation.cpp:1156-1166, 1222-1223), so incapacitate the partner until it is dead.
    None when it is dead, else the reason."""
    posture = None
    for _ in range(4):
        answer = afflict(ally, 'incap')
        setup.setdefault('afflict', []).append(answer)
        if answer.get('error'):
            return 'afflict incap failed: ' + answer['error']
        for _ in range(limit // 3):
            posture = ally.status().get('me', {}).get('posture')
            if posture != 'incapacitated':
                break
            ally.idle(3)
        if posture == 'dead':
            return None
    return 'still %s after four incapacitations' % posture


def stage_partner(bot, ally, kinds, setup, room=None):
    """Bring the partner next to the tester and put the afflictions on it. None when it is ready,
    else the reason it is not (the caller then tries another partner). With a room, both go into it."""
    other, status = ally.status(), bot.status()
    if not status.get('planet') or other.get('planet') != status.get('planet'):
        return 'in another planet or scene unavailable'
    if room and not (status.get('cell') == room['cell'] == other.get('cell')):
        arrived, setup['hospital'] = walk_into(room, bot, ally)
        if not arrived:
            return 'could not walk into the hospital cell'
        other, status = ally.status(), bot.status()
    # setup can leave the crew in different hospital rooms. Walk both outside
    # before comparing local coordinates; never compare coordinates across cells.
    if (other.get('cell') or 0) != (status.get('cell') or 0):
        setup['gather_moves'] = [bot.walk(*TOWN), ally.walk(TOWN[0] + 1, TOWN[1])]
        other, status = ally.status(), bot.status()
    if (other.get('cell') or 0) != (status.get('cell') or 0):
        return 'in another scene after gathering'

    def apart(a, b):
        return math.hypot(a.get('x', 1e9) - b.get('x', -1e9), a.get('y', 1e9) - b.get('y', -1e9))

    if apart(other, status) > 2.5:  # the partner comes to the tester, who may stand by the wildlife
        setup['ally_move'] = ally.walk(status['x'] + 1, status['y'])
        other = ally.status()
    if apart(other, bot.status()) > 4:  # healState and healEnhance answer "too far" a little beyond that
        return 'out of healing range'
    seen = [any(o.get('oid') == partner.oid for o in viewer.look(16, 'CREO', 400))
            for viewer, partner in ((bot, ally), (ally, bot))]
    setup['mutual_visibility'] = seen
    if not all(seen):
        return 'tester and ally do not see each other after gathering'
    if not kinds:
        return None
    # An earlier affliction (a poison or fire that is still burning) would muddy this one.
    if not wait_clean(ally):
        return 'still carries an earlier affliction after 90 s'
    if not rest(ally, action=.3, health=.5, limit=60):
        return 'below 50% health before the afflict'
    for kind in kinds:
        if kind == 'dead':
            why = kill(ally, setup)
            if why:
                return why
            continue
        answer = afflict(ally, kind)
        setup.setdefault('afflict', []).append(answer)
        if answer.get('error'):
            return 'afflict %s failed: %s' % (kind, answer['error'])
    return patient_problem(kinds, ally.status().get('me', {}))


def needed_afflictions(tags):
    """Kinds to put on the patient for these setup tags, most specific first. A revive pack needs a dead
    patient ("Your target does not require resuscitation!" otherwise, RevivePlayerCommand.h:27)."""
    kinds = [AFFLICT[t] for t in tags if t.startswith('affliction:')]
    if not kinds and 'item:revive_pack' in tags:
        kinds = ['dead']
    if not kinds and 'incapacitated_friendly' in tags:
        kinds = ['incap']
    if not kinds and 'wounded_friendly' in tags:
        kinds = ['damage']
    return kinds


def stageable(missing):
    """True when everything a needs_staging entry lacks is something afflict can put on the ally, or a
    building the bots can walk into."""
    return bool(missing) and all(m in AFFLICT or m in BUILDINGS for m in missing)


def settle(bot, entry, limit=30, ctx=None):
    """Wait, bounded, until none of the command's invalid states is set. Returns own status."""
    invalid = {s.lower() for s in (entry.get('command_table') or {}).get('invalid_states', [])}
    me = {}
    # The body does not list the berserk state, so wait out the 20 s by the clock.
    left = (ctx or {}).get('berserk_until', 0) - time.monotonic()
    if 'berserk' in invalid and left > 0:
        bot.idle(left)
    for _ in range(limit // 3 + 1):
        me = bot.status().get('me', {})
        held = invalid.intersection(str(s).lower() for s in me.get('states', []) if isinstance(me.get('states'), list))
        if not held:
            return me
        if 'combat' in held:
            bot.slash('peace', wait=.5)
        bot.idle(3)
    return me


def rest(bot, action=.3, health=.5, limit=90, mind=.25):
    """Bounded wait until action, health and mind are back above their floors (healers spend mind).
    False if they never are. Below a floor, the bot first asks for /agentgear afflict restore (no wounds, shock,
    DOTs or states, full HAM): regen stops at max minus wounds, and on 15 Oct the tester Jesh carried 499 mind wounds
    of 500 from clonings and earlier staging, so every Doctor ability was BLOCKED. A server without the kind
    answers with an error and the bot waits on regen as before."""
    restored = False
    for _ in range(limit // 15 + 1):
        me = bot.status().get('me', {})
        ham, top = me.get('ham', {}), me.get('max_ham', {})
        if all(not top.get(pool) or ham.get(pool, 0) / top[pool] >= floor
               for pool, floor in (('action', action), ('health', health), ('mind', mind))):
            return True
        if not restored:
            restored = True
            if not afflict(bot, 'restore').get('error'):
                continue
        bot.idle(15)
    return False


def probe(g, bot, ally, entry, ctx=None):
    ctx = ctx if ctx is not None else {}
    result = dict(ability=entry['ability'], kind=entry['test_kind'],
                  readiness=entry['readiness'], attempts=[], setup={}, gate_passed=False)

    def blocked(reason):
        result.update(verdict='BLOCKED', reason=reason)
        return result

    # A kit gap that a carried stock weapon covers (species certs let every character use
    # pistol, carbine and rifle cdef) is not a gap: try it with that weapon.
    missing = entry.get('readiness_missing', [])
    covered = (entry['readiness'] == 'needs_new_kit' and missing and
               all(m.startswith('weapon:') and weapon_route(bot, m) for m in missing))
    staged = entry['readiness'] == 'needs_staging' and stageable(missing)
    if ctx.get('held') is not None:  # /agentgear profession list names every ability held
        result['held'] = entry['ability'] in ctx['held']
    if entry['readiness'] != 'ready' and not covered and not staged:
        return blocked(entry['readiness'] + ': ' + ', '.join(missing))
    if staged:
        result['setup']['staged_by_afflict'] = missing
    if covered:
        result['setup']['kit_gap_covered_by_weapon_already_carried'] = missing
    if not entry.get('slash') and not any(t.startswith('item:instrument') for t in entry['setup_tags']):
        return blocked('no callable ground command')
    bot.slash('peace', wait=.5)
    bot.slash('stand', wait=1)
    status = bot.status()
    me = status.get('me', {})
    if me.get('posture') in ('incapacitated', 'dead'):
        result['setup']['recover'] = bot.recover()
        status = bot.status()
        me = status.get('me', {})
        if not status.get('connected', True) or me.get('posture') in ('incapacitated', 'dead'):
            return blocked('tester disconnected/down')
    if ctx.get('rest_failed', 0) >= 2:
        return blocked('tester did not recover (action/health) twice running; the rest of the profession is skipped')
    if not rest(bot):
        ctx['rest_failed'] = ctx.get('rest_failed', 0) + 1
        return blocked('action below 30% or health below 50% after bounded regeneration')
    ctx['rest_failed'] = 0
    tags = entry['setup_tags']
    for token in required_items(entry):
        if not carried(bot, token):
            return blocked('missing kit item: ' + token)
    if 'outdoors' in tags and status.get('cell'):  # still in the hospital from an earlier ability
        result['setup']['walk_out'] = bot.walk(*TOWN)
        if bot.status().get('cell'):
            return blocked('requires outdoors')
    # Squad leader commands need the tester to lead a group, which the leader of the squad group does.
    leads = bot is g.leader and bool(me.get('group'))
    unverified = [t for t in tags if t in ('force_power', 'no_armor', 'pet', 'creature_target')
                  or (t == 'group_leader' and not leads)]
    if unverified:
        return blocked('special staging not verified: ' + ', '.join(tags))
    if 'group_leader' in tags:
        result['setup']['group'] = me.get('group')
    for tag in tags:
        if tag.startswith('weapon:'):
            tokens = WEAPONS.get(tag[7:])
            if tokens is None:
                return blocked('weapon equip route unavailable: ' + tag)
            ok, evidence = unequip(bot) if tag == 'weapon:unarmed' else equip(bot, tokens)
            result['setup']['weapon'] = evidence
            if not ok:
                return blocked('weapon %s not confirmed: %s' % ('unequip' if tag == 'weapon:unarmed' else 'equip',
                                                                '/'.join(tokens) or 'bare hands'))
    target = 0
    if 'hostile_target' in tags:
        obj = prey(bot)
        obj = close_enough(bot, obj) if obj else None
        if not obj and ctx.get('restages', 0) < 2:
            ctx['restages'] = ctx.get('restages', 0) + 1
            result['setup']['restaged'] = stage_wildlife(bot, ctx.get('search_start', 0))
            obj = prey(bot)
            obj = close_enough(bot, obj) if obj else None
        if not obj or obj.get('posture') != 'upright':
            return blocked('no live creature reachable within 3 m')
        target = obj['oid']
        result['setup']['target'] = obj
    friendly = any(t in tags for t in ('friendly_target', 'wounded_friendly', 'incapacitated_friendly'))
    room = None
    if entry['ability'] in MEDICAL_FACILITY or any(t in BUILDINGS for t in tags):
        room = hospital_room(bot, ctx)
        if room is None:
            return blocked('no hospital cell found within 2 km')
        if not friendly:
            arrived, result['setup']['hospital'] = walk_into(room, bot)
            if not arrived:
                return blocked('could not walk into the hospital cell')
    if friendly:
        allies = ctx.get('allies') or [ally]  # a different partner each time: wounds pile up on one
        kinds = needed_afflictions(tags)
        reasons = []
        staged = False
        for _ in range(len(allies)):
            ally = allies[ctx.get('ally_turn', 0) % len(allies)]
            ctx['ally_turn'] = ctx.get('ally_turn', 0) + 1
            why = stage_partner(bot, ally, kinds, result['setup'], room)
            if why is None:
                staged = True
                break
            reasons.append('%s: %s' % (ally.first, why))
            if not kinds:
                break  # nothing to afflict: another partner would not help
        if not staged:
            return blocked('; '.join(reasons)[:300])
        result['setup']['ally'] = ally.first
        if set(kinds) and set(kinds) <= set(INVISIBLE):
            result['setup']['invisible_effect'] = True
        target = ally.oid
    instrument = next((t for t in tags if t.startswith('item:instrument')), None)
    if instrument:
        token = instrument.split(':')[-1] if instrument.count(':') == 2 else 'slitherhorn'
        ok, evidence = equip(bot, INSTRUMENT_ALIASES.get(token, token), swap_out=True)
        result['setup']['instrument'] = evidence
        if not ok:
            return blocked('instrument equip not confirmed: ' + token)
    if 'item:stimpack' in tags and not any('stimpack' in str(i.get('name')) for i in bot.inventory().get('items', [])):
        return blocked('no stimpack in inventory')
    if 'item:survey_tool' in tags and not any('survey_tool' in str(i.get('name')) for i in bot.inventory().get('items', [])):
        return blocked('no survey tool in inventory')
    if entry['test_kind'] == 'performance' or instrument:
        bot.slash('stopDance', wait=1.5)
        bot.slash('stopMusic', wait=1.5)
        if entry['ability'] in MUSIC_EFFECTS and not instrument:
            ok, evidence = equip(bot, 'slitherhorn', swap_out=True)
            result['setup']['instrument'] = evidence
            if not ok:
                return blocked('instrument equip not confirmed: slitherhorn')
        if 'performing' in tags:
            command = 'startMusic' if entry.get('slash') == 'stopMusic' or entry['ability'] in MUSIC_EFFECTS else 'startDance'
            args = 'starwars1' if command == 'startMusic' else 'basic'
            setup_events = bot.slash(command, args, wait=3)
            result['setup']['performance'] = setup_events
            if not any('@performance:music_start_self' in str(e.get('text', '')) or
                       '@performance:dance_start_self' in str(e.get('text', '')) for e in setup_events):
                return blocked('prerequisite performance did not start')
    effective = dict(entry)
    if result['setup'].get('invisible_effect'):
        effective['invisible_effect'] = True
    if instrument and not entry.get('slash'):
        effective.update(slash='startMusic', args='starwars1', instrument_probe=True)
    tries = 3 if entry['ability'] in ('berserk1', 'berserk2', 'takeCover') else 1
    if entry['ability'] in PRE_COMMAND:
        result['setup']['pre_command'] = [PRE_COMMAND[entry['ability']], bot.slash(PRE_COMMAND[entry['ability']], wait=3.5)]
    attempt, repositioned = 0, 0
    while attempt < tries:
        attempt += 1
        settle(bot, effective, ctx=ctx)
        before = bot.status().get('me', {})
        if before.get('posture') in ('incapacitated', 'dead'):  # went down on the way to the target
            result['setup']['recover'] = bot.recover()
            return blocked('tester was %s before the command could be sent' % before['posture'])
        patient_before = ally.status().get('me', {}) if target == ally.oid else {}
        if patient_before:
            why = patient_problem(needed_afflictions(tags), patient_before)
            if why:
                result['setup']['patient_before'] = patient_before
                return blocked('patient no longer staged: ' + why)
        events = call(bot, effective, target, wait=12 if 'Forage' in entry['ability'] or entry['ability'] == 'forage' else None)
        after = bot.status().get('me', {})
        patient_after = ally.status().get('me', {}) if patient_before else {}
        verdict, reason = classify(effective, events, before, after, patient_before, patient_after, True)
        result['attempts'].append(dict(events=events, before=before, after=after,
                                       patient_before=patient_before, patient_after=patient_after,
                                       verdict=verdict, reason=reason))
        result['gate_passed'] = gate_passed(events)
        if (verdict == 'BLOCKED' and target == ally.oid and 'no_line_of_sight' in reason
                and repositioned < len(LOS_OFFSETS)):
            # Town geometry (a crate, a doorway, a crowd) can hide the ally; stand it somewhere else
            # and ask again. The afflictions are still on it.
            dx, dy = LOS_OFFSETS[repositioned]
            repositioned += 1
            here = bot.status()
            result['setup'].setdefault('los_moves', []).append(
                ally.walk(here.get('x', 0) + dx, here.get('y', 0) + dy).get('arrived'))
            attempt -= 1
            continue
        if verdict != 'BLOCKED' or not any('berserk_fail' in str(e) or 'cover_fail' in str(e) for e in events):
            break
        if attempt < tries:
            bot.idle(3)
    result.update(verdict=verdict, reason=reason)
    if entry['ability'] in ('berserk1', 'berserk2') and verdict != 'BLOCKED':
        ctx['berserk_until'] = time.monotonic() + BERSERK_SECONDS
    staged_kinds = needed_afflictions(tags)
    if target == ally.oid and any(k in ('incap', 'dead') for k in staged_kinds):
        result['setup']['patient_recover'] = ally.recover()
        if 'dead' in staged_kinds:  # a clone (when the revive failed) adds 100 wounds per pool
            result['setup']['patient_restore'] = afflict(ally, 'restore').get('wounds')
    if entry['ability'] == 'survey':
        result['tool_probe'] = survey_tool(bot)
        g.note('Survey real tool gate: ' + result['tool_probe']['verdict'] + ': ' + result['tool_probe']['reason'])
    return result


def restore(g, testers):
    """Bounded final clear of every bot that was a tester and the group's configured starting boxes,
    even on stop. The runner's deadline cannot cancel the restoration halfway through: give cleanup
    its own four-minute ceiling, leaving the original STOP untouched."""
    original = g.control
    if original is not None:
        from run_control import RunControl
        class CleanupControl(RunControl):
            def reason(self):
                return 'cleanup budget reached' if time.monotonic() >= self.deadline else None
        g.control = CleanupControl(original.folder, g.name, 'class-check cleanup', time.monotonic() + 240)
    data = {}
    try:
        testers = list(dict.fromkeys(testers))
        for tester in testers:
            for cmd in ('peace', 'stopDance', 'stopMusic', 'stand'):
                tester.slash(cmd, wait=.2)
            data.setdefault('clear', {})[tester.first] = tester.clear_professions()
        for b in g.bots:
            boxes = list(dict.fromkeys([b.member['profession'] + '_novice'] + g.training.get(b.first, [])))
            if boxes and b.running():
                b.slash('agentSkill', ' '.join(boxes), wait=0)
                answer = b.wait_for(lambda e: str(e.get('text', '')).startswith('[agentskill]'), 15)
                listed = b.profession('list')
                held = listed.get('skills', [])
                ok = not listed.get('error') and all(box in held for box in boxes)
                data[b.first] = dict(answer=answer, list=listed, verified=ok)
                g.check('restore starting boxes: ' + b.first, ok, boxes)
        for name, cleared in data.get('clear', {}).items():
            g.check('final profession clear answered: ' + name, not cleared.get('error') and not cleared.get('failed'), cleared)
    finally:
        g.control = original
    return data


def select(plan, phase, professions):
    if phase == 'P0':
        if professions:
            raise ValueError('P0 takes no profession')
        return None
    rows = [r for r in plan if r['phase'].split()[0] == phase and
            (not professions or r['profession'] in professions)]
    if len(rows) != 1 or (professions and set(professions) != {r['profession'] for r in rows}):
        raise ValueError('Select exactly one profession in the chosen phase per run')
    return rows[0]


def select_many(plan, phase, professions):
    """Rows for a group's queue, in the order given. Phase P0 takes none; phase RUN looks the
    names up in the whole run order; any other phase only accepts names of that phase."""
    if phase == 'P0':
        if professions:
            raise ValueError('P0 takes no profession')
        return []
    if not professions:
        raise ValueError('name the professions to run (CLASS_CHECK_PROFESSIONS)')
    by_name = {r['profession']: r for r in plan if phase == 'RUN' or r['phase'].split()[0] == phase}
    missing = [n for n in professions if n not in by_name]
    if missing:
        raise ValueError('not in phase %s: %s' % (phase, ', '.join(missing)))
    return [by_name[n] for n in dict.fromkeys(professions)]


def requested_for(group, raw):
    """CLASS_CHECK_PROFESSIONS is 'name' or 'Group:name[+name...]', comma separated. Several groups can
    run in one squad.py invocation, each with its own queue, run one after the other within the
    time slice: 'Aurek:science_medic+outdoors_ranger,Dorn:social_dancer'. Unprefixed names apply
    to every group."""
    names = []
    for item in (p.strip() for p in raw.split(',')):
        if not item:
            continue
        owner, _, queue = item.rpartition(':')
        if not owner or owner == group:
            names += [n.strip() for n in queue.split('+') if n.strip()]
    return names


def choose_tester(g, row, named='', needs_leader=False):
    """CLASS_CHECK_TESTER, else a member who started as this profession, else the group leader when
    the commands lead a squad, else the member with the emptiest inventory (every kit adds items
    and a full inventory blocks the next kit)."""
    if named:
        return g[named]
    if row:
        for bot in g.bots:
            if bot.member.get('profession') == row['profession']:
                return bot
    if needs_leader or len(g.bots) < 2:
        return g.leader

    def load(bot):
        try:
            return len(bot.inventory().get('items', []))
        except Exception:
            return 10 ** 6

    return min(g.bots, key=load)


def order(abilities):
    """Box order, except abilities that leave a state or posture behind go last."""
    return sorted(abilities, key=lambda a: a in PERSISTENT)


def leads(row, cmds):
    """True when the profession's commands need the tester to lead the group (squad leader)."""
    return any('group_leader' in cmds[a]['setup_tags'] for a in row['abilities'])


def other_member(g, tester):
    return next(b for b in g.bots[1:] + g.bots[:1] if b is not tester)


def run_one(g, row, tester, ally, profs, cmds, deadline, controls_data, first, report_extra):
    """One profession: clear (unless P0 just did), prove the previous profession is gone, grant,
    kit up, try every ability, write Bot-reports/<Group>/class-check-<profession>.json."""
    report = dict(schema=3, profession=row['profession'], phase=row['phase'].split()[0], group=g.name,
                  tester=tester.first, ally=ally.first, started=datetime.now().isoformat(), results=[],
                  source=profs.get('meta'), completed=False, controls=controls_data,
                  scenario_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  context=os.getenv('CLASS_CHECK_CONTEXT', ''), **report_extra)
    abilities = order(row['abilities'])
    ctx = {'allies': [b for b in g.bots if b is not tester]}
    try:
        if not first:
            for cmd in ('peace', 'stopDance', 'stopMusic', 'stand'):
                tester.slash(cmd, wait=.3)
            ok, report['clear'], listed = clear_ok(tester)
            if not ok:
                g.note('BLOCKED: %s: clear before the grant failed: %s' % (row['profession'], str(report['clear'])[:200]))
                report['interrupted'] = 'clear failed'
                return report
        save(g, report)
        previous = next((r for r in profs['proposed_run_order'] if r['step'] == row['step'] - 1), None)
        if previous and previous['abilities']:
            ability = previous['abilities'][0]
            entry = cmds[ability]
            if not entry.get('slash') or (entry.get('gate') or {}).get('ungated'):
                report['previous_control'] = {'ability': ability, 'blocked': 'no command-level ability gate'}
                g.note('BLOCKED: previous-run negative probe has no command-level gate: ' + ability)
            else:
                events = call(tester, entry)
                passed = revoked(events)
                report['previous_control'] = dict(ability=ability, passed=passed, events=events)
                if not g.check('%s: previous profession ability revoked: %s' % (row['profession'], ability), passed, events):
                    report['interrupted'] = 'previous profession ability not revoked'
                    return report
        if not row['grant'].startswith('/agentgear'):
            report['grant'] = {'error': 'grant route deferred: ' + row['grant']}
        else:
            report['grant'] = tester.profession(row['profession'])
        grant = report['grant']
        expected = [b['name'] for p in profs['professions'] if p['name'] == row['profession'] for b in p['boxes']]
        granted = not grant.get('error') and not grant.get('failed') and all(b in grant.get('skills', []) for b in expected)
        if granted:
            g.check(row['profession'] + ' full grant verified', True, len(expected))
            tags = {tag for ability in abilities for tag in cmds[ability]['setup_tags']}
            kits = kits_for(abilities, cmds)
            report['gear'] = provision(tester, kits, [cmds[a] for a in abilities], report)
            for kit, answer in report['gear'].items():
                if answer.get('failed') or answer.get('error'):
                    g.note('gear kit %s incomplete (full inventory?): %s; weapons already carried are used'
                           % (kit, str(answer.get('error') or answer.get('failed'))[:120]))
            # With /agentgear profession list the answer names every ability held (dev 60ed8971).
            listing = tester.profession('list')
            report['abilities_held'] = listing.get('abilities')
            if report['abilities_held'] is not None:
                ctx['held'] = set(report['abilities_held'])
            if 'hostile_target' in tags:
                ctx['search_start'] = search_start(g.name)
                report['staging'] = stage_wildlife(tester, ctx['search_start'])
        else:
            g.note('BLOCKED: %s: full profession grant not verified: %s' % (row['profession'], str(grant)[:250]))
        for ability in abilities:
            if not granted or time.monotonic() >= deadline:
                result = dict(ability=ability, verdict='BLOCKED', attempts=[], gate_passed=False,
                              reason='grant not verified' if not granted else 'scenario time slice exhausted')
            else:
                result = probe(g, tester, ally, cmds[ability], ctx)
            report['results'].append(result)
            emit(g, result)
            save(g, report)
        report['completed'] = True
    except Exception as exc:
        report['interrupted'] = type(exc).__name__ + ': ' + str(exc)
        done = {r['ability'] for r in report['results']}
        for ability in abilities:
            if ability not in done:
                result = dict(ability=ability, verdict='BLOCKED', attempts=[], gate_passed=False,
                              reason=report['interrupted'])
                report['results'].append(result)
                emit(g, result)
        raise
    finally:
        report['finished'] = datetime.now().isoformat()
        save(g, report)
    return report


def run(g):
    phase = os.getenv('CLASS_CHECK_PHASE', 'P0').upper()
    requested = requested_for(g.name, os.getenv('CLASS_CHECK_PROFESSIONS', ''))
    if os.getenv('CLASS_CHECK_GROUP', g.name) != g.name:
        raise ValueError('CLASS_CHECK_GROUP disagrees with runner --group')
    profs = json.loads((OUTPUTS / 'Claude-class-check/professions.json').read_text(encoding='utf-8'))
    commands = json.loads((OUTPUTS / 'Claude-class-check/commands.json').read_text(encoding='utf-8'))
    cmds = {e['ability']: e for e in commands['commands']}
    rows = select_many(profs['proposed_run_order'], phase, requested)
    named = os.getenv('CLASS_CHECK_TESTER', '')
    tester = choose_tester(g, rows[0] if rows else None, named, leads(rows[0], cmds) if rows else False)
    minutes = min(23, max(1, float(os.getenv('CLASS_CHECK_MINUTES', '23'))))
    deadline = time.monotonic() + minutes * 60
    if g.control is not None:
        g.control.deadline = min(g.control.deadline or deadline, deadline)
    reports, used = [], [tester]
    p0 = dict(schema=3, profession='P0', phase='P0', group=g.name, tester=tester.first,
              ally=other_member(g, tester).first, started=datetime.now().isoformat(), results=[], completed=False,
              source=profs.get('meta'), context=os.getenv('CLASS_CHECK_CONTEXT', ''),
              scenario_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              queue=[r['profession'] for r in rows])
    try:
        tester.slash('peace', wait=.5)
        tester.slash('stopDance', wait=.5)
        tester.slash('stopMusic', wait=.5)
        tester.slash('stand', wait=1)
        # Controls run in town before clear/grant, away from roaming attackers.
        here = tester.status()
        if math.hypot(here.get('x', 0) - TOWN[0], here.get('y', 0) - TOWN[1]) > 80:
            p0.setdefault('control_staging', []).append(tester.walk(*TOWN))
        ok, p0['controls'] = controls(g, tester, other_member(g, tester), cmds)
        save(g, p0)
        if not ok:
            g.note('BLOCKED: negative/positive P0 controls not proven; profession judgements withheld')
            return
        if not rows:
            p0['completed'] = True
            return
        for index, row in enumerate(rows):
            # leave the cleanup its own budget and do not start a profession with under two minutes left
            if time.monotonic() >= deadline - 120:
                g.note('NOT RUN (time slice): ' + ', '.join(r['profession'] for r in rows[index:]))
                break
            who = tester if index == 0 else choose_tester(g, row, named, leads(row, cmds))
            if who not in used:
                used.append(who)
            reports.append(run_one(g, row, who, other_member(g, who), profs, cmds, deadline,
                                   p0['controls'], index == 0 and who is tester,
                                   dict(control_staging=p0.get('control_staging'), queue_position=index + 1)))
    finally:
        try:
            cleanup = restore(g, used)
            for report in reports:
                report['cleanup'] = cleanup
                save(g, report)
        except Exception as exc:
            g.note('BLOCKED: class-check restoration incomplete: %s: %s' % (type(exc).__name__, exc))
        p0['finished'] = datetime.now().isoformat()
        save(g, p0)
