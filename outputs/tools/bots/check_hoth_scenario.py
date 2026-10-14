"""Offline false-pass regressions for the Hoth scenario; no game access."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('hoth', Path(__file__).parent / 'scenarios/esk-hoth.py')
hoth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hoth)


class Group:
    def __init__(self, bot):
        self.bot, self.checks = bot, {}
    def __getitem__(self, key):
        return self.bot
    def check(self, label, ok, detail=''):
        self.checks[label] = bool(ok)
        return bool(ok)
    def note(self, text):
        pass
    def sleep(self, seconds):
        pass


class Bot:
    oid = 1
    inbox = []
    def __init__(self, planet='hoth', new_ticket=False, arrived=False):
        self.planet, self.new_ticket, self.arrived = planet, new_ticket, arrived
        self.purchased = False
        self.x, self.y = hoth.CORONET[2] if planet == 'corellia' else (0, -2000)
    def status(self):
        return dict(planet=self.planet, x=self.x, y=self.y, z=0, cell=0)
    def walk(self, x, y, *args, **kwargs):
        if self.arrived:
            self.x, self.y = x, y
        return {'arrived': self.arrived}
    def locate(self, *args):
        return [dict(oid=10, template='terminal_travel', distance=0, x=self.x, y=self.y)]
    def inventory(self):
        items = [dict(oid=99, name='old ticket')]
        if self.new_ticket and self.purchased:
            items.append(dict(oid=100, name='new ticket'))
        return {'items': items}
    def slash(self, *args, **kwargs):
        self.purchased = True
    def request(self, *args, **kwargs):
        return {'height': 0}
    def look(self, **kwargs):
        return []
    def select(self, *args, **kwargs):
        pass
    def sui_pages(self):
        return {'pages': []}
    def messages(self):
        return []


class HothTests(unittest.TestCase):
    def test_old_ticket_cannot_prove_purchase(self):
        group = Group(Bot(planet='corellia'))
        self.assertFalse(hoth.ride(group, group.bot, hoth.CORONET, hoth.HOTH))
        self.assertFalse(group.checks['corellia -> hoth: buy a ticket'])

    def test_loop_requires_arrivals(self):
        original = hoth.ride
        hoth.ride = lambda *args: True
        try:
            for arrived in (False, True):
                group = Group(Bot(arrived=arrived))
                hoth.run(group)
                self.assertEqual(group.checks['walk a loop on the snow'], arrived)
        finally:
            hoth.ride = original


if __name__ == '__main__':
    unittest.main()
