"""C45 source contracts and recipe-lifecycle MODEL; no C++ build or game control.
Run in WSL: python3 check_f1_fix.py --root /opt/swg/Core3-gpt
"""
import argparse
import itertools
from pathlib import Path
import unittest

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--root', type=Path, required=True)
ARGS, REST = PARSER.parse_known_args()
ROOT = ARGS.root / 'MMOCoreORB'


class Mission:
    def __init__(self, recipe, kind='crafting'):
        self.recipe = recipe
        self.kind = kind


class RecipeModel:
    """Models the existing pooled grant plus the new last-consumer cleanup."""
    def __init__(self, recipes):
        self.active = [Mission(r) for r in recipes]
        self.uses = {}

    def pickup(self, mission):
        self.uses[mission.recipe] = self.uses.get(mission.recipe, 0) + 1

    def assemble(self, mission):
        assert self.uses.get(mission.recipe, 0) > 0
        self.uses[mission.recipe] -= 1
        if self.uses[mission.recipe] == 0:
            del self.uses[mission.recipe]

    def end(self, mission, outcome):
        assert outcome in ('abort', 'complete')
        # This predicate is independently checked against the source below.
        shared = any(other is not mission and other.kind == 'crafting'
                     and other.recipe == mission.recipe for other in self.active
                     if other is not None)
        if not shared:
            self.uses.pop(mission.recipe, None)
        self.active.remove(mission)

    def relog(self):
        # SchematicList serializes the rewarded map; reloading rebuilds visibility.
        self.uses = dict(self.uses)


class SourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = (ROOT / 'src/server/zone/objects/mission/CraftingMissionObjectiveImplementation.cpp').read_text()
        cls.helper = cls.cpp.split('static void removeUnusedMissionSchematic', 1)[1].split(
            'void CraftingMissionObjectiveImplementation::updateMissionStatus', 1)[0]

    def test_full_scan_under_player_lock(self):
        h = self.helper
        self.assertLess(h.index('Locker playerLock(player)'), h.index('getContainerObjectsSize()'))
        self.assertIn('i < datapad->getContainerObjectsSize(); ++i', h)
        self.assertIn('object == nullptr || !object->isMissionObject()', h)
        self.assertIn('if (datapad == nullptr)', h)

    def test_matching_consumer_returns_before_removal(self):
        expected = ('if (otherMission != mission && otherMission->getTypeCRC() == MissionTypes::CRAFTING && '
                    'otherMission->getTemplateString1() == mission->getTemplateString1()) { return; }')
        h = ' '.join(self.helper.split())
        self.assertIn(expected, h)
        self.assertLess(h.index(expected), h.index('ghost->removeRewardedSchematic(schematic, true)'))
        # No pickup-status restriction: not-yet-picked-up active missions also protect it.
        self.assertNotIn('getObjectiveStatus', h)

    def test_both_end_paths_cleanup_before_base(self):
        for outcome in ('abort', 'complete'):
            body = self.cpp.split(f'void CraftingMissionObjectiveImplementation::{outcome}()', 1)[1].split('}', 1)[0]
            self.assertLess(body.index('removeUnusedMissionSchematic(mission, player)'),
                            body.index(f'DeliverMissionObjectiveImplementation::{outcome}()'))
        idl = (ROOT / 'src/server/zone/objects/mission/CraftingMissionObjective.idl').read_text()
        self.assertIn('public abstract native void complete();', idl)

    def test_positive_use_count_is_reloaded(self):
        player = (ROOT / 'src/server/zone/objects/player/PlayerObjectImplementation.cpp').read_text()
        body = player.split('void PlayerObjectImplementation::removeSchematics(', 1)[1].split(
            'void PlayerObjectImplementation::doDigest(', 1)[0]
        self.assertIn('schematicList.addRewardedSchematics(asPlayerObject())', body)
        schematics = (ROOT / 'src/server/zone/objects/player/variables/SchematicList.cpp').read_text()
        reload_body = schematics.split('void SchematicList::addRewardedSchematics(', 1)[1].split(
            'bool SchematicList::addRewardedSchematic(', 1)[0]
        self.assertIn('ghost->addSchematics(schematics, true)', reload_body)

    def test_six_total_and_single_bounty_unchanged(self):
        manager = (ROOT / 'src/server/zone/managers/mission/MissionManagerImplementation.cpp').read_text()
        self.assertIn('getInt("Core3.MissionManager.MaxActiveMissions", 6)', manager)
        self.assertIn('missionCount >= maxActiveMissions || (hasBountyMission && mission->getTypeCRC() == MissionTypes::BOUNTY)', manager)


class LifecycleModel(unittest.TestCase):
    def test_original_three_mission_counterexample(self):
        # Baseline abort dropped the whole A entry even though C still needed A.
        original = RecipeModel(['A', 'B', 'A'])
        for m in original.active:
            original.pickup(m)
        original.uses.pop('A')
        self.assertNotIn('A', original.uses)  # Demonstrates old behavior, not gameplay.
        for ending_index in (0, 2):
            fixed = RecipeModel(['A', 'B', 'A'])
            for m in fixed.active:
                fixed.pickup(m)
            fixed.end(fixed.active[ending_index], 'abort')
            fixed.relog()
            self.assertGreater(fixed.uses['A'], 0)
            self.assertGreater(fixed.uses['B'], 0)

    def test_two_distinct_and_shared_missions(self):
        for recipes in (['A', 'B'], ['A', 'A']):
            for outcome in ('abort', 'complete'):
                model = RecipeModel(recipes)
                first, survivor = model.active
                for m in model.active:
                    model.pickup(m)
                if outcome == 'complete':
                    model.assemble(first)
                model.end(first, outcome)
                model.relog()
                self.assertGreater(model.uses[survivor.recipe], 0)
                model.assemble(survivor)
                model.end(survivor, 'complete')
                self.assertEqual(model.uses, {})

    def test_three_finish_then_abort_and_reverse(self):
        for first_outcome, second_outcome in (('complete', 'abort'), ('abort', 'complete')):
            model = RecipeModel(['A', 'B', 'A'])
            first, unrelated, survivor = model.active
            for m in model.active:
                model.pickup(m)
            if first_outcome == 'complete':
                model.assemble(first)
            model.end(first, first_outcome)
            model.relog()
            self.assertGreater(model.uses['A'], 0)
            if second_outcome == 'complete':
                model.assemble(survivor)
            model.end(survivor, second_outcome)
            self.assertNotIn('A', model.uses)
            self.assertEqual(model.uses['B'], 1)
            model.end(unrelated, 'abort')
            self.assertEqual(model.uses, {})

    def test_unpicked_and_already_assembled_survivor(self):
        for survivor_picked in (False, True):
            model = RecipeModel(['A', 'A'])
            ending, survivor = model.active
            model.pickup(ending)
            if survivor_picked:
                model.pickup(survivor)
                model.assemble(survivor)
            model.end(ending, 'abort')
            self.assertGreater(model.uses['A'], 0)
            if not survivor_picked:
                model.pickup(survivor)
                model.assemble(survivor)
            # Completion must remove the preserved aborted grant too.
            model.end(survivor, 'complete')
            self.assertEqual(model.uses, {})

    def test_six_crafting_missions_with_five_recipes(self):
        model = RecipeModel(['A', 'B', 'C', 'D', 'E', 'A'])
        missions = list(model.active)
        for m in missions:
            model.pickup(m)
        model.end(missions[0], 'abort')
        for m in missions[1:]:
            model.assemble(m)
            model.end(m, 'complete')
            model.relog()
        self.assertEqual(model.uses, {})

    def test_nonmission_and_other_type_do_not_hold_recipe(self):
        model = RecipeModel(['A'])
        mission = model.active[0]
        model.pickup(mission)
        model.active.extend([None, Mission('A', 'nonmission'), Mission('A', 'delivery'), Mission('B')])
        model.end(mission, 'abort')
        self.assertNotIn('A', model.uses)

    def test_all_one_to_six_consumer_assignments(self):
        cases = 0
        for count in range(1, 7):
            for recipes in itertools.product('AB', repeat=count):
                for ending_index in range(count):
                    for outcome in ('abort', 'complete'):
                        model = RecipeModel(recipes)
                        for m in model.active:
                            model.pickup(m)
                        ending = model.active[ending_index]
                        if outcome == 'complete':
                            model.assemble(ending)
                        model.end(ending, outcome)
                        model.relog()
                        for r in 'AB':
                            if any(m.recipe == r for m in model.active):
                                self.assertGreater(model.uses.get(r, 0), 0)
                            else:
                                self.assertNotIn(r, model.uses)
                        cases += 1
        print(f'Exhaustive model: {cases} single-ending cases, 1-6 active missions, two recipe labels')


if __name__ == '__main__':
    unittest.main(argv=['check_f1_fix.py', *REST], verbosity=2)
