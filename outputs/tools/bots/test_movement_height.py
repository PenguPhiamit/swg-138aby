"""C40 offline protocol/escort checks; python -I test_movement_height.py."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import squad
import escort


class Heights(unittest.TestCase):
    def setUp(self):
        self.bot = object.__new__(squad.Bot)
        self.bot.request = Mock(return_value={'ok': True, 'arrived': True})

    def test_outdoor_move_and_plan_omit_height(self):
        for name in ('move', 'path'):
            getattr(self.bot, name)(3536, -4796)
            self.bot.request.assert_called_with(name, 105, x=3536, y=-4796, timeout=90)

    def test_explicit_height_survives_in_each_frame(self):
        for name in ('move', 'path'):
            for z in (0, -12.5, 9.5):
                for cell in (None, 123):
                    getattr(self.bot, name)(1, 2, z, cell, timeout=20)
                    args = dict(x=1, y=2, z=z, timeout=20)
                    if cell:
                        args['cell'] = cell
                    self.bot.request.assert_called_with(name, 35, **args)

    def test_retries_keep_the_dungeon_floor(self):
        self.bot.request.side_effect = [dict(ok=False, error='timeout', x=1, y=2), dict(ok=True, arrived=True)]
        self.bot.walk(3, 4, -12.5, 123)
        self.assertEqual(self.bot.request.call_count, 2)
        for call in self.bot.request.call_args_list:
            self.assertEqual(call.kwargs, dict(x=3, y=4, z=-12.5, cell=123, timeout=95))

    def test_escort_trail_keeps_all_floor_heights(self):
        for z in (-12.5, 0, 9.5):
            escort.walk_trail(self.bot, dict(x=1, y=2, z=z, cell=123), 20)
            self.bot.request.assert_called_with('move', 35, x=1, y=2, z=z, cell=123, timeout=20)

    def test_escort_unknown_floor_does_not_walk_to_zero(self):
        answer = escort.walk_trail(self.bot, dict(x=1, y=2, cell=123), 20)
        self.assertFalse(answer['ok'])
        self.bot.request.assert_not_called()

    def test_go_uses_local_height_indoors_and_omits_it_outdoors(self):
        for cell in (0, 123):
            self.bot.status = Mock(return_value={'cell': cell})
            self.bot.go(dict(x=1, y=2, z=-12.5))
            args = dict(x=1, y=2, timeout=90)
            if cell:
                args.update(z=-12.5, cell=cell)
            self.bot.request.assert_called_with('move', 105, **args)


if __name__ == '__main__':
    unittest.main()
