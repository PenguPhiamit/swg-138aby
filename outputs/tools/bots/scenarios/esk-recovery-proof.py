"""C20 acceptance: strand only Esk by normal travel, then recover the mixed-location crew."""
import importlib.util
from pathlib import Path
from fallback_scenarios import recover_home

GROUP = 'Esk'


def run(g):
    spec = importlib.util.spec_from_file_location('esk_recovery_trip', Path(__file__).with_name('esk-hoth.py'))
    travel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(travel)
    bot = g.leader
    planet = bot.status().get('planet')
    if planet == 'tatooine':
        if not travel.ride(g, bot, travel.MOS_EISLEY, travel.CORONET):
            return
    if bot.status().get('planet') == 'corellia':
        if not travel.ride(g, bot, travel.CORONET, travel.HOTH):
            return
    if not g.check('acceptance starts recovery with Esk on Hoth', bot.status().get('planet') == 'hoth'):
        return
    g.check('mixed-location crew recovered home', recover_home(g))
    for member in g.bots:
        s = member.status()
        g.check(f'{member.first}: final planet Tatooine', s.get('planet') == 'tatooine', s.get('planet'))
