"""Forn escort: the dungeon crew plays alongside the owner (owner, 15 Oct: "the dungeon crew was meant to run with me").
tools/bots/escort.py does the work: follow in formation (into buildings too), fight the player's target with real
rotations, defend the player and each other, Mirren heals the lowest, orders by chat (follow, stay, attack, passive,
heal, status, dismiss), and a play-data log of the combat around the player (Bot-reports/play/).

Who: ESCORT_OWNER, else the group's "escort_owner" in groups.json. How long: ESCORT_MINUTES (default 120); give
squad.py --round-minutes a few minutes more. Before setting off: templates and gear as in forn-crew.py, and everyone
restored. The crew waits up to 15 minutes for the player to log in.
"""
import importlib.util
import json
import os
from pathlib import Path

import escort

GROUP = 'Forn'
HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('forn_crew', HERE / 'forn-crew.py')
crew = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(crew)


def run(g):
    spec = json.loads((HERE.parent / 'groups.json').read_text(encoding='utf-8'))['groups'][GROUP]
    owner = os.environ.get('ESCORT_OWNER') or spec.get('escort_owner', '')
    minutes = float(os.environ.get('ESCORT_MINUTES', 120))
    if not g.check('a player to escort is named', owner, owner or 'set ESCORT_OWNER or escort_owner in groups.json'):
        return
    crew.ready(g)
    for bot in g.bots:
        bot.slash('agentGear', 'afflict restore', wait=0)
        bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
    for _ in range(60):
        if escort.who(owner):
            break
        for bot in g.bots:
            bot.doing(f'waiting for {owner} to log in')
        g.leader.idle(15)
    if not g.check(f'{owner} is online', escort.who(owner), 'waited 15 minutes'):
        return
    summary = escort.escort(g, owner, crew.ROLES, minutes)
    g.check(f'the crew saw {owner}', summary['owner_seen'])
    g.note(f"escort: {summary['minutes']} min; orders {summary['orders']}; play data {summary['play_data']}")
    for first, c in summary['counts'].items():
        rec = summary['crew'][first]
        g.note(f"{first}: fights {c['fights']}, follow moves {c['follows']}, orders heard {c['orders']}, "
               f"sent {sum(rec['sent'].values())}, refused {sum(rec['refused'].values())}, heals {rec['heals']}, "
               f"lowest health {rec['lowest_health']}; top refusals {list(rec['refused'])[:3]}")
