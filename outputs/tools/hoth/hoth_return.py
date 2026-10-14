"""Bring Esk home from Hoth after a creature probe: walk to the outpost pad, then ride to Coronet. (Claude, 14 Oct.)

    squad.py run /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth/hoth_return.py

Waits for Esk to stand up first if incapacitated. Uses esk-hoth.py's ride() with the probe's newest-ticket-list filter.
"""
import importlib.util
from pathlib import Path

GROUP = 'Esk'
_spec = importlib.util.spec_from_file_location('hoth_probe', Path(__file__).resolve().parent / 'hoth_creature_probe.py')
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)


def run(g):
    esk = g['Esk']
    probe.newest_ticket_list(esk)
    for _ in range(12):
        ok, s = probe.alive(esk)
        if ok or s.get('planet') != 'hoth':
            break
        g.note(f"Esk is {s['posture']}; waiting")
        g.sleep(15)
    if not g.check('Esk on Hoth and upright', ok, f"{s.get('planet')} {s.get('posture')}"):
        return
    trip = esk.walk(*probe.PAD, tries=6)
    g.note(f'walk to the pad: {str(trip)[:120]}')
    probe.rides.ride(g, esk, probe.rides.HOTH, probe.rides.CORONET)
