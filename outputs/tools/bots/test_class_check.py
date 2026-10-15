"""Synthetic server-event tests; no credentials or live bot I/O."""
import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock

os.environ['CLASS_CHECK_WOUNDS'] = '1'   # the tests cover the wound staging too
spec = importlib.util.spec_from_file_location('class_check', Path(__file__).parent / 'scenarios/class-check.py')
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)


def system(text):
    return {'event': 'system', 'text': text}


def entry(kind='self', **kw):
    return dict(dict(test_kind=kind, ability='test', messages=[]), **kw)


class Verdicts(unittest.TestCase):
    def verdict(self, e, events=(), **kw):
        return cc.classify(e, list(events), setup_verified=True, **kw)[0]

    def test_missing_ability_wins_over_unrelated_success(self):
        events = [{'event': 'command_failed', 'error': 2}, system('@performance:dance_start_self')]
        self.assertEqual(self.verdict(entry('performance'), events), 'NOT_GRANTED')

    def test_per_name_performance_gate(self):
        for text in cc.MISSING_PERFORMANCE:
            self.assertEqual(self.verdict(entry('performance'), [system(text)]), 'NOT_GRANTED')

    def test_all_setup_errors_are_blocked(self):
        for error in (1, 3, 4, 5):
            self.assertEqual(self.verdict(entry('attack'), [{'event': 'command_failed', 'error': error}]), 'BLOCKED')
        for text in ('@cbt_spam:no_attack_wrong_weapon', '@cbt_spam:no_attack_ranged_single',
                     '@cbt_spam:no_attack_melee_single', '@healing_response:healing_response_60',
                     '@performance:music_no_instrument', '@jedi_spam:not_with_armor',
                     '@skl_use:sys_forage_noroom'):
            self.assertEqual(self.verdict(entry(), [system(text)]), 'BLOCKED')
        self.assertEqual(self.verdict(entry(command_table={'invalid_states': ['berserk']}),
                                     before={'states': ['berserk'], 'ham': {'action': 20}},
                                     after={'states': ['berserk'], 'ham': {'action': 30}}), 'BLOCKED')

    def test_attack_requires_matching_outgoing_spam(self):
        e = entry('attack', combat_spam_keys=['@cbt_spam:test_hit', '@cbt_spam:test_miss'])
        event = dict(event='combat', attacker_name='me', what='@cbt_spam:test_miss', amount=0)
        self.assertEqual(self.verdict(e, [event]), 'WORKS')
        self.assertEqual(self.verdict(e, [dict(event, what='@cbt_spam:attack_hit', amount=10)]), 'NO_EFFECT')
        self.assertEqual(self.verdict(e, [dict(event, attacker_name='other')]), 'NO_EFFECT')
        self.assertEqual(self.verdict(e, [dict(event, what='@cbt_spam:test_hit')]), 'NO_EFFECT')

    def test_self_success_or_state_ham_change(self):
        e = entry(); e['messages'] = [dict(key='@cbt_spam:berserk_success_single', role_guess='success')]
        self.assertEqual(self.verdict(e, [system('@cbt_spam:berserk_success_single')]), 'WORKS')
        self.assertEqual(self.verdict(entry(), before={'states': 0}, after={'states': 1}), 'WORKS')

    def test_heal_requires_real_rise_not_regeneration_or_unclassified_message(self):
        e = entry('heal_other')
        self.assertEqual(self.verdict(e, patient_before={'ham': {'health': 20}},
                                     patient_after={'ham': {'health': 80}}), 'WORKS')
        # a rise of 10 is what natural regeneration adds in a few seconds
        self.assertEqual(self.verdict(e, patient_before={'ham': {'health': 20}},
                                     patient_after={'ham': {'health': 30}}), 'NO_EFFECT')
        self.assertEqual(self.verdict(e, [system('You heal Jesh for 120 health damage.')]), 'WORKS')
        self.assertEqual(self.verdict(e, [system('@healing_response:healing_response_62')]), 'RAN')
        self.assertEqual(self.verdict(entry('target_friendly'), [{'event': 'sui_page'}]), 'RAN')
        self.assertEqual(self.verdict(entry('target_friendly', slash='diagnose'), [{'event': 'sui_page'}]), 'WORKS')

    def test_no_damage_to_heal_is_setup_not_a_verdict(self):
        for text in ('@healing_response:healing_response_61', '@healing_response:healing_response_63',
                     '@healing_response:healing_must_wait'):
            self.assertEqual(self.verdict(entry('heal_other'), [system(text)]), 'BLOCKED')

    def test_self_evidence_ignores_regeneration(self):
        base = {'states': ['peace'], 'posture': 'upright', 'ham': {'health': 800, 'action': 780, 'mind': 600}}
        regen = dict(base, ham={'health': 812, 'action': 792, 'mind': 600})
        paid = dict(base, ham={'health': 800, 'action': 730, 'mind': 600})
        self.assertEqual(self.verdict(entry(), before=base, after=regen), 'RAN')
        self.assertEqual(self.verdict(entry(), before=base, after=paid), 'WORKS')
        # damage taken, or being in combat, also lowers HAM and proves nothing
        hurt = [dict(event='combat', attacker_name='creature', defender_name='me', amount=30)]
        self.assertEqual(self.verdict(entry(), hurt, before=base, after=paid), 'RAN')
        fighting = dict(base, states=['combat'])
        self.assertEqual(self.verdict(entry(), before=fighting, after=dict(paid, states=['combat'])), 'RAN')

    def test_self_posture_new_state_and_extra_success(self):
        base = {'states': ['peace'], 'posture': 'upright', 'ham': {'action': 700}}
        self.assertEqual(self.verdict(entry(), before=base, after=dict(base, posture='prone')), 'WORKS')
        self.assertEqual(self.verdict(entry(), before=base, after=dict(base, states=['peace', 'berserk'])), 'WORKS')
        # combat and peace toggling is not an effect of the ability
        self.assertEqual(self.verdict(entry(), before=base, after=dict(base, states=['combat'])), 'RAN')
        forage = entry(ability='forage')
        self.assertEqual(self.verdict(forage, [system('@skl_use:sys_forage_start')]), 'WORKS')
        # "started", then "no room": the ability ran, only the find had nowhere to go
        self.assertEqual(self.verdict(forage, [system('@skl_use:sys_forage_start'),
                                              system('@skl_use:sys_forage_noroom')]), 'WORKS')
        self.assertEqual(self.verdict(forage, [system('@skl_use:sys_forage_noroom')]), 'BLOCKED')
        tumble = entry(ability='tumbleToStanding')
        tumble['messages'] = [dict(key='@cbt_spam:tum_standing', role_guess='failure')]
        spam = dict(event='combat', attacker_name='me', what='@cbt_spam:tum_standing')
        self.assertEqual(self.verdict(tumble, [spam]), 'WORKS')

    def test_gate_passed_needs_a_sent_command_and_no_error_two(self):
        sent = {'ok': True, 'reply': 'command', 'sent': 'x'}
        self.assertTrue(cc.gate_passed([sent, {'event': 'command_failed', 'error': 5}]))
        self.assertFalse(cc.gate_passed([sent, {'event': 'command_failed', 'error': 2}]))
        self.assertFalse(cc.gate_passed([]))
        self.assertFalse(cc.gate_passed([{'ok': False, 'reply': 'error'}]))

    def test_blocked_note_says_when_the_gate_passed(self):
        g = Mock()
        cc.emit(g, dict(ability='x', verdict='BLOCKED', reason='no creature', gate_passed=True))
        self.assertIn('gate passed', g.note.call_args[0][0])
        g.check.assert_not_called()

    def test_failing_verdicts_are_failed_checks(self):
        g = Mock()
        for verdict in ('NOT_GRANTED', 'NO_EFFECT'):
            cc.emit(g, dict(ability='x', verdict=verdict, reason='r'))
        self.assertEqual([c[0][1] for c in g.check.call_args_list], [False, False])
        cc.emit(g, dict(ability='y', verdict='WORKS', reason='r'))
        self.assertTrue(g.check.call_args[0][1])

    def test_survey_tool_gate_message_is_not_granted(self):
        bot = Mock()
        bot.inventory.return_value = {'items': [dict(oid=5, name='@item_n:survey_tool_mineral')]}
        bot.select.return_value = [system('@error_message:insufficient_skill')]
        self.assertEqual(cc.survey_tool(bot)['verdict'], 'NOT_GRANTED')
        bot.select.return_value = [{'event': 'survey_resources'}]
        self.assertEqual(cc.survey_tool(bot)['verdict'], 'WORKS')
        bot.inventory.return_value = {'items': []}
        self.assertEqual(cc.survey_tool(bot)['verdict'], 'BLOCKED')

    def test_performance_start_and_survey_evidence(self):
        self.assertEqual(self.verdict(entry('performance'), [system('@performance:dance_start_self')]), 'WORKS')
        self.assertEqual(self.verdict(entry('item'), [{'event': 'survey_resources'}]), 'WORKS')

    def test_ran_separate_from_no_effect_and_missing_setup(self):
        self.assertEqual(self.verdict(entry()), 'RAN')
        self.assertEqual(self.verdict(entry('item', handler={'status': 'template_stub'})), 'NO_EFFECT')
        self.assertEqual(self.verdict(entry('performance', slash='startDance')), 'NO_EFFECT')
        self.assertEqual(cc.classify(entry('attack'), [], setup_verified=False)[0], 'BLOCKED')

    def test_blocked_and_ran_never_fail_group(self):
        g = Mock()
        for v in ('BLOCKED', 'RAN'):
            cc.emit(g, dict(ability='x', verdict=v, reason='reason'))
        g.check.assert_not_called()
        self.assertEqual(g.note.call_count, 2)

    def test_selection_never_accidentally_runs_whole_phase(self):
        plan = [dict(phase='P1 starters', profession=n) for n in ('a', 'b')]
        self.assertIsNone(cc.select(plan, 'P0', []))
        self.assertEqual(cc.select(plan, 'P1', ['b'])['profession'], 'b')
        for names in ([], ['a', 'b'], ['missing']):
            with self.assertRaises(ValueError):
                cc.select(plan, 'P1', names)

    def test_named_npc_is_not_a_wildlife_target(self):
        self.assertFalse(cc.alive(dict(name='@mob/creature_names:spynet_operative', posture='upright')))
        self.assertTrue(cc.alive(dict(name='@mob/creature_names:worrt', posture='upright')))
        self.assertFalse(cc.alive(dict(name='@mob/creature_names:worrt', posture='dead')))

    def test_only_passive_animals_are_prey(self):
        for name in ('dwarf_eopie', 'eopie', 'worrt', 'rill'):
            self.assertTrue(cc.alive(dict(name='@mob/creature_names:' + name, posture='upright')), name)
        # aggressive (scyk, kreetle, sevorrt), strong (womp rat, dewback) and NPC names are never prey
        for name in ('scyk', 'kreetle', 'sevorrt', 'womp_rat', 'dewback', 'eopie_matriarch', 'giant_worrt',
                     'sand_trooper', 'commoner'):
            self.assertFalse(cc.alive(dict(name='@mob/creature_names:' + name, posture='upright')), name)

    def test_gorgs_are_prey_and_strong_passive_animals_are_neither_prey_nor_danger(self):
        for name in ('gorg', 'gorg_glutton'):
            self.assertTrue(cc.alive(dict(name='@mob/creature_names:' + name, posture='upright')), name)
        def wild(name):
            return dict(name='@mob/creature_names:' + name, posture='upright')
        self.assertFalse(cc.alive(wild('cu_pa')))
        self.assertFalse(cc.hazard(wild('cu_pa')))
        self.assertFalse(cc.hazard(wild('gorg_glutton')))
        self.assertTrue(cc.hazard(wild('scyk')))
        self.assertTrue(cc.hazard(wild('mutant_womprat')))   # unknown: treated as a danger
        self.assertFalse(cc.hazard(dict(name='Varo Kesh', posture='upright')))
        bot = Mock(oid=1)
        bot.look.return_value = [dict(wild('gorg_glutton'), distance=30, x=0, y=0, oid=2),
                                 dict(wild('cu_pa'), distance=40, x=20, y=0, oid=3)]
        self.assertEqual(cc.prey(bot)['oid'], 2)  # a nearby cu pa does not spoil it

    def test_prey_prefers_weak_then_near(self):
        bot = Mock()
        bot.look.return_value = [dict(name='@mob/creature_names:eopie', posture='upright', distance=5, x=0, y=0),
                                 dict(name='@mob/creature_names:worrt', posture='upright', distance=90, x=500, y=0),
                                 dict(name='@mob/creature_names:worrt', posture='upright', distance=40, x=900, y=0)]
        self.assertEqual(cc.prey(bot)['distance'], 40)
        bot.look.return_value = [dict(name='@mob/creature_names:eopie', posture='upright', distance=5, x=0, y=0),
                                 dict(name='@mob/creature_names:dwarf_eopie', posture='upright', distance=50, x=300, y=0)]
        self.assertIn('dwarf_eopie', cc.prey(bot)['name'])

    def test_prey_is_skipped_when_aggressive_wildlife_is_close(self):
        bot = Mock()
        near = dict(name='@mob/creature_names:scyk', posture='upright', distance=70, x=40, y=0)
        bot.look.return_value = [dict(name='@mob/creature_names:dwarf_eopie', posture='upright', distance=20, x=0, y=0),
                                 near]
        self.assertIsNone(cc.prey(bot))
        near['x'] = 200  # far enough
        self.assertIsNotNone(cc.prey(bot))
        near['x'], near['posture'] = 10, 'dead'  # a corpse is no danger
        self.assertIsNotNone(cc.prey(bot))

    def test_close_enough_walks_in_legs_and_gives_up_when_the_animal_is_gone(self):
        far = dict(oid=5, name='@mob/creature_names:rill', posture='upright', distance=116)
        bot = Mock()
        bot.look.side_effect = [[dict(far, distance=60)], [dict(far, distance=2)]]
        self.assertEqual(cc.close_enough(bot, far)['distance'], 2)
        self.assertEqual(bot.go.call_count, 2)
        bot.look.side_effect = [[]]
        self.assertIsNone(cc.close_enough(bot, far))
        bot.look.side_effect = [[dict(far, posture='dead')]]
        self.assertIsNone(cc.close_enough(bot, far))
        near = Mock()
        self.assertEqual(cc.close_enough(near, dict(far, distance=1))['distance'], 1)
        near.go.assert_not_called()

    def test_prey_near_another_players_is_left_to_them(self):
        bot = Mock(oid=1)
        eopie = dict(name='@mob/creature_names:dwarf_eopie', posture='upright', distance=20, x=0, y=0, oid=9)
        stranger = dict(name='Varo Kesh', posture='upright', distance=30, x=10, y=0, oid=77, type='CREO')
        bot.look.return_value = [eopie, stranger, dict(stranger, name='Aurek Dannor', oid=1)]
        self.assertIsNone(cc.prey(bot))
        stranger['x'] = 100
        self.assertEqual(cc.prey(bot)['oid'], 9)
        bot.look.return_value = [eopie, dict(stranger, x=5, name='R2-D2 (a helper R2 unit)')]
        self.assertEqual(cc.prey(bot)['oid'], 9)  # droids do not hunt

    def test_groups_start_their_search_at_different_points(self):
        starts = {cc.search_start(n) for n in ('Aurek', 'Besh', 'Cresh', 'Dorn', 'Esk')}
        self.assertGreater(len(starts), 2)
        bot = Mock()
        bot.walk.return_value = {'arrived': True, 'seconds': 1}
        bot.look.return_value = []
        cc.stage_wildlife(bot, 2)
        first = bot.walk.call_args_list[0][0]
        self.assertEqual(first, (cc.PLATEAU[0] + cc.SEARCH[2][0], cc.PLATEAU[1] + cc.SEARCH[2][1]))
        self.assertEqual(bot.walk.call_count, len(cc.SEARCH))

    def test_stage_wildlife_walks_to_the_plateau_and_stops_at_first_prey(self):
        bot = Mock()
        bot.walk.return_value = {'arrived': True, 'seconds': 10}
        bot.status.return_value = {'me': {'posture': 'upright'}}
        creature = dict(name='@mob/creature_names:dwarf_eopie', posture='upright', distance=20, oid=9, x=0, y=0)
        bot.look.side_effect = lambda *a, **k: [creature] if bot.walk.call_count >= 2 else []
        result = cc.stage_wildlife(bot)
        self.assertEqual(result['found']['oid'], 9)
        self.assertEqual(len(result['tried']), 2)
        self.assertEqual(bot.walk.call_args_list[0][0], (cc.PLATEAU[0] + cc.SEARCH[0][0], cc.PLATEAU[1] + cc.SEARCH[0][1]))
        bot.look.side_effect = None
        bot.look.return_value = []
        self.assertIn('blocked', cc.stage_wildlife(bot))

    def test_stage_wildlife_skips_points_near_aggressive_wildlife_and_stops_when_down(self):
        scyk = dict(name='@mob/creature_names:scyk', posture='upright', distance=50, oid=5, x=cc.PLATEAU[0] + 60, y=cc.PLATEAU[1])
        bot = Mock()
        bot.walk.return_value = {'arrived': True, 'seconds': 1}
        bot.status.return_value = {'me': {'posture': 'upright'}}
        bot.look.return_value = [scyk]
        result = cc.stage_wildlife(bot)
        skipped = [t for t in result['tried'] if t.get('skipped')]
        self.assertTrue(skipped)
        self.assertLess(bot.walk.call_count, len(cc.SEARCH))
        down = Mock()
        down.walk.return_value = {'arrived': False, 'seconds': 5}
        down.status.return_value = {'me': {'posture': 'incapacitated'}}
        self.assertIn('went down', cc.stage_wildlife(down)['blocked'])
        self.assertEqual(down.walk.call_count, 1)

    def test_persistent_state_abilities_run_last_in_box_order(self):
        self.assertEqual(cc.order(['berserk1', 'taunt', 'takeCover', 'headShot1', 'aim', 'bodyShot1']),
                         ['taunt', 'headShot1', 'bodyShot1', 'berserk1', 'takeCover', 'aim'])

    def test_tester_is_the_member_who_started_as_the_profession(self):
        bots = [Mock(member={'profession': p}) for p in ('combat_marksman', 'combat_brawler', 'science_medic')]
        g = MagicMock(bots=bots, leader=bots[0])
        g.__getitem__.side_effect = lambda name: bots[int(name)]
        self.assertIs(cc.choose_tester(g, {'profession': 'science_medic'}), bots[2])
        self.assertIs(cc.choose_tester(g, {'profession': 'crafting_artisan'}), bots[0])
        self.assertIs(cc.choose_tester(g, None), bots[0])
        self.assertIs(cc.choose_tester(g, {'profession': 'science_medic'}, '1'), bots[1])

    def test_kit_gap_is_blocked_unless_a_stock_weapon_is_carried(self):
        e = dict(ability='legShot1', test_kind='attack', readiness='needs_new_kit',
                 readiness_missing=['weapon:carbine'], setup_tags=['hostile_target', 'weapon:carbine'],
                 slash='legShot1', messages=[])
        bot = Mock()
        bot.inventory.return_value = {'items': []}
        result = cc.probe(Mock(), bot, Mock(), e)
        self.assertEqual(result['verdict'], 'BLOCKED')
        self.assertFalse(result['gate_passed'])
        self.assertIn('needs_new_kit', result['reason'])

    def test_cures_are_proven_by_the_patient_not_by_regeneration(self):
        e = entry('heal_other', ability='curePoison')
        sick = {'states': ['peace', 'poisoned'], 'posture': 'upright'}
        well = {'states': ['peace'], 'posture': 'upright'}
        self.assertEqual(self.verdict(e, patient_before=sick, patient_after=well), 'WORKS')
        self.assertEqual(self.verdict(e, patient_before=sick, patient_after=sick), 'NO_EFFECT')
        # a state that only toggled between combat and peace is not a cure
        self.assertEqual(self.verdict(e, patient_before={'states': ['combat']}, patient_after={'states': ['peace']}),
                         'NO_EFFECT')
        down = {'states': [], 'posture': 'incapacitated'}
        self.assertEqual(self.verdict(entry('heal_other', ability='revivePlayer'), patient_before=down,
                                      patient_after={'states': [], 'posture': 'upright'}), 'WORKS')
        for text in ('You heal Jesh for 40 health wound damage.', 'You remove the dizzy state from Jesh.',
                     'You apply first aid to Jesh.', 'You enhance Jesh\'s health.'):
            self.assertEqual(self.verdict(e, [system(text)]), 'WORKS', text)
        drag = entry('target_friendly', ability='dragIncapacitatedPlayer')
        self.assertEqual(self.verdict(drag, [system('@healing_response:healing_response_b5')]), 'WORKS')

    def test_wound_cures_the_body_cannot_see_are_ran_not_no_effect(self):
        e = entry('heal_other', ability='tendWound', invisible_effect=True)
        self.assertEqual(self.verdict(e), 'RAN')
        self.assertEqual(self.verdict(e, [system('You heal Jesh for 30 health wound damage.')]), 'WORKS')
        self.assertEqual(self.verdict(entry('heal_other', ability='tendWound')), 'NO_EFFECT')

    def test_nothing_to_treat_is_setup(self):
        for text in ('@healing:no_state_to_heal', '@healing_response:healing_response_74',
                     '@healing_response:healing_response_a4', '@healing_response:cannot_resuscitate_kit',
                     '@healing_response:must_be_grouped', '@healing_response:healing_response_78'):
            self.assertEqual(self.verdict(entry('heal_other'), [system(text)]), 'BLOCKED', text)

    def test_kits_come_from_the_entries_and_basic_is_first(self):
        cmds = {'a': dict(readiness='ready', setup_tags=['hostile_target', 'weapon:carbine'], kits=['carbine']),
                'b': dict(readiness='needs_staging', setup_tags=['wounded_friendly', 'item:wound_pack'], kits=['medicine2']),
                'c': dict(readiness='ready', setup_tags=['item:instrument:fanfar'], kits=['instruments']),
                'd': dict(readiness='blocked_jedi', setup_tags=['item:survey_tool'], kits=['saber1h']),
                'e': dict(readiness='ready', setup_tags=['item:stimpack'])}
        self.assertEqual(cc.kits_for(['a', 'b', 'c', 'd', 'e'], cmds),
                         ['basic', 'support', 'carbine', 'medicine2', 'instruments'])
        self.assertEqual(cc.kits_for(['a'], cmds), ['basic', 'carbine'])

    def test_afflictions_follow_the_setup_tags(self):
        self.assertEqual(cc.needed_afflictions(['wounded_friendly', 'item:wound_pack', 'affliction:wounds']), ['wounds'])
        self.assertEqual(cc.needed_afflictions(['wounded_friendly', 'item:stimpack']), ['damage'])
        self.assertEqual(cc.needed_afflictions(['incapacitated_friendly']), ['incap'])
        self.assertEqual(cc.needed_afflictions(['friendly_target', 'sui']), [])
        self.assertTrue(cc.stageable(['affliction:poison']))
        self.assertTrue(cc.stageable(['incapacitated_friendly']))
        self.assertFalse(cc.stageable(['corpse']))
        self.assertFalse(cc.stageable(['resource_point']))
        self.assertFalse(cc.stageable([]))

    def test_afflict_reads_the_agentgear_answer(self):
        bot = Mock()
        bot.wait_for.return_value = {'text': '[agentgear] {"kit":"afflict","kind":"poison","states":8388608}'}
        self.assertEqual(cc.afflict(bot, 'poison')['kind'], 'poison')
        self.assertEqual(bot.slash.call_args[0][:2], ('agentGear', 'afflict poison'))
        bot.wait_for.return_value = None
        self.assertIn('error', cc.afflict(bot, 'poison'))

    def test_staged_entry_is_not_blocked_for_missing_affliction(self):
        e = dict(ability='curePoison', test_kind='heal_other', readiness='needs_staging',
                 readiness_missing=['affliction:poison'], setup_tags=['force_power'], slash='curePoison', messages=[])
        bot = Mock()
        bot.status.return_value = {'me': {'posture': 'upright', 'ham': {'action': 900}, 'max_ham': {'action': 900, 'health': 900}}}
        result = cc.probe(Mock(), bot, Mock(), e, {'held': {'curePoison'}})
        # force_power stops it, but only after the staging gate: the reason is not the readiness label
        self.assertNotIn('needs_staging', result['reason'])
        self.assertTrue(result['held'])
        corpse = dict(e, readiness_missing=['corpse'], setup_tags=['corpse'])
        self.assertIn('needs_staging', cc.probe(Mock(), bot, Mock(), corpse, {})['reason'])

    def test_performance_messages_seen_live(self):
        stop = entry('performance', ability='stopDance', slash='stopDance')
        self.assertEqual(self.verdict(stop, [system('@performance:dance_stop_self')]), 'WORKS')
        self.assertEqual(self.verdict(entry('performance', ability='stopMusic'),
                                      [system('@performance:music_prepare_stop_self')]), 'WORKS')
        self.assertEqual(self.verdict(entry('performance', ability='flourish+3'),
                                      [system('@performance:flourish_perform')]), 'WORKS')
        # late answers to the setup stop commands must not hide the start message
        late = [system('@performance:dance_not_performing'), system('@performance:music_not_performing'),
                system('@performance:music_start_self')]
        self.assertEqual(self.verdict(entry('performance', ability='startMusic+starwars3'), late), 'WORKS')
        # but a missing song still counts as a missing ability
        self.assertEqual(self.verdict(entry('performance'), late[:2] + [system('@performance:music_lack_skill_song_self')]),
                         'NOT_GRANTED')

    def test_effects_windows_and_squad_listing_are_evidence(self):
        for text in ('@performance:effect_perform_spot_light', '@performance:effect_perform_smoke_bomb'):
            self.assertEqual(self.verdict(entry('performance', ability='spotlight'), [system(text)]), 'WORKS')
        self.assertEqual(self.verdict(entry('performance', ability='firejet'),
                                      [system('@performance:effect_not_performing_correct')]), 'BLOCKED')
        track = entry(ability='areatrack', setup_tags=['sui'])
        self.assertEqual(self.verdict(track, [{'event': 'sui_page'}]), 'WORKS')
        self.assertEqual(self.verdict(entry(ability='conceal'), [system('@skl_use:sys_conceal_nokit')]), 'BLOCKED')
        self.assertEqual(self.verdict(entry(ability='sysgroup'), [system('Squad Leader Cresh: ')]), 'WORKS')

    def test_tester_choice_prefers_the_member_then_the_leader_for_squads_then_the_emptiest_inventory(self):
        def bot(name, profession, items):
            b = Mock(member={'profession': profession}, first=name)
            b.inventory.return_value = {'items': [{}] * items}
            return b
        bots = [bot('A', 'combat_marksman', 90), bot('B', 'combat_brawler', 40), bot('C', 'science_medic', 12)]
        g = MagicMock(bots=bots, leader=bots[0])
        g.__getitem__.side_effect = lambda name: next(b for b in bots if b.first == name)
        self.assertIs(cc.choose_tester(g, {'profession': 'science_medic'}), bots[2])
        self.assertIs(cc.choose_tester(g, {'profession': 'social_dancer'}), bots[2])  # emptiest inventory
        self.assertIs(cc.choose_tester(g, {'profession': 'outdoors_squadleader'}, needs_leader=True), bots[0])
        self.assertIs(cc.choose_tester(g, {'profession': 'social_dancer'}, 'B'), bots[1])

    def test_revoked_means_error_two_or_the_per_name_performance_gate(self):
        self.assertTrue(cc.revoked([{'event': 'command_failed', 'error': 2}]))
        self.assertTrue(cc.revoked([system('@performance:dance_lack_skill_self')]))
        self.assertTrue(cc.revoked([system('@performance:music_lack_skill_song_self')]))
        self.assertFalse(cc.revoked([system('@performance:dance_start_self')]))
        self.assertFalse(cc.revoked([{'event': 'command_failed', 'error': 5}]))

    def test_a_group_queue_keeps_the_order_and_may_cross_phases(self):
        plan = [dict(phase='P1 starters', profession='a'), dict(phase='P2 elites', profession='b'),
                dict(phase='P2 elites', profession='c')]
        self.assertEqual([r['profession'] for r in cc.select_many(plan, 'P2', ['c', 'b'])], ['c', 'b'])
        self.assertEqual([r['profession'] for r in cc.select_many(plan, 'RUN', ['b', 'a', 'b'])], ['b', 'a'])
        self.assertEqual(cc.select_many(plan, 'P0', []), [])
        for phase, names in (('P2', ['a']), ('P1', []), ('RUN', ['zzz'])):
            with self.assertRaises(ValueError):
                cc.select_many(plan, phase, names)
        with self.assertRaises(ValueError):
            cc.select_many(plan, 'P0', ['a'])
        self.assertEqual(cc.requested_for('Aurek', 'Aurek:science_medic+outdoors_ranger, Dorn:social_dancer'),
                         ['science_medic', 'outdoors_ranger'])

    def test_squad_leader_commands_need_the_tester_to_lead_a_grouped_squad(self):
        e = dict(ability='rally', test_kind='self', readiness='ready', readiness_missing=[],
                 setup_tags=['group_leader', 'group_member'], slash='rally', messages=[])
        ok = {'me': {'posture': 'upright', 'ham': {'action': 900, 'health': 900}, 'max_ham': {'action': 900, 'health': 900},
                     'group': 77, 'states': []}}
        bot, other = Mock(), Mock()
        bot.status.return_value = ok
        self.assertIn('special staging', cc.probe(Mock(leader=other), bot, Mock(), e)['reason'])
        no_group = {'me': dict(ok['me'], group=0)}
        bot.status.return_value = no_group
        self.assertIn('special staging', cc.probe(Mock(leader=bot), bot, Mock(), e)['reason'])
        bot.status.return_value = ok
        bot.slash.return_value = [{'ok': True, 'reply': 'command'}]
        result = cc.probe(Mock(leader=bot), bot, Mock(), e)
        self.assertNotIn('special staging', result.get('reason', ''))
        self.assertEqual(result['setup']['group'], 77)

    def test_each_group_takes_its_own_profession_from_one_variable(self):
        raw = 'Aurek:combat_brawler, Dorn:social_entertainer,science_medic'
        self.assertEqual(cc.requested_for('Aurek', raw), ['combat_brawler', 'science_medic'])
        self.assertEqual(cc.requested_for('Dorn', raw), ['social_entertainer', 'science_medic'])
        self.assertEqual(cc.requested_for('Besh', raw), ['science_medic'])
        self.assertEqual(cc.requested_for('Besh', ''), [])
        self.assertEqual(cc.requested_for('Besh', 'outdoors_scout'), ['outdoors_scout'])

    def test_instrument_names_match_without_underscores_and_with_aliases(self):
        items = [dict(oid=1, name='@obj_n:obj_flute_droopy'), dict(oid=2, name='@obj_n:obj_kloo_horn'),
                 dict(oid=3, name='@obj_n:ommni_box'), dict(oid=4, name='@weapon_name:pistol_cdef')]
        self.assertEqual(cc.matching(items, 'flutedroopy')[0]['oid'], 1)
        self.assertEqual(cc.matching(items, 'kloohorn')[0]['oid'], 2)
        self.assertEqual(cc.matching(items, cc.INSTRUMENT_ALIASES['omnibox'])[0]['oid'], 3)
        self.assertEqual(cc.matching(items, 'pistol_cdef')[0]['oid'], 4)
        self.assertEqual(cc.matching(items, 'traz'), [])

    def test_unequip_puts_the_weapon_in_the_inventory_and_ignores_the_bare_hand(self):
        box = dict(oid=1, parent=42, type='TANO', name='@item_n:inventory')
        hand = dict(oid=2, parent=42, type='WEAO', name='@obj_n:unknown_weapon')
        rifle = dict(oid=3, parent=42, type='WEAO', name='@weapon_name:rifle_cdef')
        bot = Mock(oid=42)
        bot.slash.return_value = []
        bot.inventory.side_effect = [{'items': [box, hand, rifle]}, {'items': [box, hand, dict(rifle, parent=1)]}]
        ok, evidence = cc.unequip(bot)
        self.assertTrue(ok)
        name, args = bot.slash.call_args[0][:2]
        self.assertEqual((name, args), ('transferItemMisc', '1 -1 0 0 0'))
        self.assertEqual(bot.slash.call_args[1]['target'], 3)
        bot.inventory.side_effect = [{'items': [box, hand, rifle]}, {'items': [box, hand, rifle]}]
        self.assertFalse(cc.unequip(bot)[0])
        bot.inventory.side_effect = [{'items': [box, hand]}]
        bot.slash.reset_mock()
        self.assertEqual(cc.unequip(bot), (True, {'already_unarmed': True}))
        bot.slash.assert_not_called()

    def test_an_instrument_replaces_the_one_in_hand_by_putting_it_away_first(self):
        box = dict(oid=1, parent=42, type='TANO', name='@item_n:inventory')
        slither = dict(oid=2, parent=42, type='TANO', name='@obj_n:obj_slitherhorn')
        nalargon = dict(oid=3, parent=1, type='TANO', name='@obj_n:obj_nalargon')
        bot = Mock(oid=42)
        calls = []
        bot.slash.side_effect = lambda name, args='', **kw: calls.append((name, kw.get('target'))) or []
        states = iter([
            {'items': [box, slither, nalargon]},                    # equip: look
            {'items': [box, slither, nalargon]},                    # unequip: look
            {'items': [box, dict(slither, parent=1), nalargon]},    # unequip: confirm
            {'items': [box, dict(slither, parent=1), dict(nalargon, parent=42)]}])   # equip: confirm
        bot.inventory.side_effect = lambda: next(states)
        ok, evidence = cc.equip(bot, 'nalargon', swap_out=True)
        self.assertTrue(ok)
        self.assertEqual(calls, [('transferItemMisc', 2), ('transferItemWeapon', 3)])
        # without swap_out nothing is put away
        calls.clear()
        states = iter([{'items': [box, slither, nalargon]}, {'items': [box, slither, dict(nalargon, parent=42)]}])
        cc.equip(bot, 'nalargon')
        self.assertEqual(calls, [('transferItemWeapon', 3)])

    def test_a_healer_without_line_of_sight_gets_the_ally_moved_and_asks_again(self):
        e = dict(ability='tendDamage', test_kind='heal_other', readiness='ready', readiness_missing=[],
                 setup_tags=['wounded_friendly'], slash='tendDamage', messages=[])
        me = {'posture': 'upright', 'states': [], 'ham': {'health': 900, 'action': 900, 'mind': 900},
              'max_ham': {'health': 1000, 'action': 1000, 'mind': 1000}}
        hurt = dict(me, ham={'health': 600, 'action': 900, 'mind': 900})
        here = {'planet': 'tatooine', 'cell': 0, 'x': 10.0, 'y': 10.0, 'me': me}
        bot, ally = Mock(oid=1, first='Tamsin'), Mock(oid=2, first='Jesh')
        bot.status.return_value = here
        ally.status.return_value = dict(here, me=hurt)
        bot.look.return_value = [{'oid': 2}]
        ally.look.return_value = [{'oid': 1}]
        ally.wait_for.return_value = {'text': '[agentgear] {"kit":"afflict","kind":"damage"}'}
        ally.walk.return_value = {'arrived': True}
        answers = iter([[system('@healing:no_line_of_sight')], [system('You heal Jesh for 300 health damage.')]])

        def slash(name, args='', **kw):
            return next(answers) if name == 'tendDamage' else []

        bot.slash.side_effect = slash
        result = cc.probe(Mock(), bot, ally, e, {'allies': [ally]})
        self.assertEqual(result['verdict'], 'WORKS')
        self.assertEqual(len(result['attempts']), 2)
        self.assertEqual(result['setup']['los_moves'], [True])
        self.assertEqual(ally.walk.call_args[0], (13.0, 10.0))

    def test_surprise_shot_gets_its_cover_first(self):
        self.assertEqual(cc.PRE_COMMAND['surpriseShot'], 'takeCover')

    def test_gather_cross_cell_partners_before_afflicting(self):
        bot, ally = Mock(oid=1), Mock(oid=2)
        here = dict(planet='tatooine', cell=0, x=3528, y=-4804)
        bot.status.return_value = here
        ally.status.side_effect = [dict(here, cell=99), dict(here, x=3529)]
        bot.look.return_value, ally.look.return_value = [{'oid': 2}], [{'oid': 1}]
        setup = {}
        self.assertIsNone(cc.stage_partner(bot, ally, [], setup))
        bot.walk.assert_called_once_with(*cc.TOWN)
        ally.walk.assert_called_once_with(3529, -4804)
        self.assertEqual(setup['mutual_visibility'], [True, True])
        ally.slash.assert_not_called()

    def test_gather_failure_and_missing_visibility_prevent_affliction(self):
        bot, ally = Mock(oid=1), Mock(oid=2)
        here = dict(planet='tatooine', cell=0, x=1, y=1)
        bot.status.return_value = here
        ally.status.return_value = dict(here, cell=9)
        self.assertIn('after gathering', cc.stage_partner(bot, ally, ['poison'], {}))
        ally.slash.assert_not_called()
        ally.status.return_value = here
        bot.look.return_value, ally.look.return_value = [{'oid': 2}], []
        self.assertIn('do not see', cc.stage_partner(bot, ally, ['poison'], {}))
        ally.slash.assert_not_called()

    def test_other_planet_is_not_walked(self):
        bot, ally = Mock(), Mock()
        bot.status.return_value = dict(planet='tatooine')
        ally.status.return_value = dict(planet='naboo')
        self.assertIn('another planet', cc.stage_partner(bot, ally, [], {}))
        bot.walk.assert_not_called()
        ally.walk.assert_not_called()

    def test_expired_afflictions_or_recovered_incap_are_not_server_failures(self):
        self.assertIsNone(cc.patient_problem(['poison'], {'states': ['poisoned']}))
        self.assertIn('expired', cc.patient_problem(['poison'], {'states': []}))
        self.assertIn('upright', cc.patient_problem(['incap'], {'posture': 'upright'}))
        self.assertIsNone(cc.patient_problem(['incap'], {'posture': 'incapacitated'}))

    def test_each_doctor_medicine_is_named_before_patient_is_afflicted(self):
        for ability, token in cc.MEDICINE.items():
            bot, ally = Mock(), Mock()
            me = dict(posture='upright', ham={'health': 900, 'action': 900, 'mind': 900},
                      max_ham={'health': 900, 'action': 900, 'mind': 900})
            bot.status.return_value = dict(me=me)
            bot.inventory.return_value = {'items': []}
            e = dict(ability=ability, test_kind='heal_other', readiness='ready', slash=ability,
                     setup_tags=['friendly_target'], messages=[])
            result = cc.probe(Mock(), bot, ally, e)
            self.assertEqual(result['verdict'], 'BLOCKED')
            self.assertEqual(result['reason'], 'missing kit item: ' + token)
            self.assertEqual(result['attempts'], [])
            ally.status.assert_not_called()

    def test_room_only_drops_observed_issued_surplus_and_confirms_removal(self):
        bot = Mock(oid=42)
        own = dict(oid=1, parent=99, name='own gear')
        pack = dict(oid=2, parent=99, name='cure_poison')
        surplus = dict(oid=3, parent=99, name='duplicate kit item')
        worn = dict(oid=4, parent=42, name='kit armor')
        items = [own, pack, surplus, worn]
        bot.inventory.side_effect = lambda: {'items': list(items)}
        bot.radial.return_value = {'items': [dict(name='item_drop', radial_id=12)]}
        bot.select.side_effect = lambda oid, radial: items.remove(surplus) or []
        evidence = cc.make_room(bot, {2, 3, 4}, {'cure_poison'}, reserve=80)
        bot.select.assert_called_once_with(3, 12)
        self.assertTrue(evidence[0]['dropped'])
        self.assertIn(own, items)
        self.assertIn(pack, items)
        self.assertIn(worn, items)

    def test_full_inventory_without_provenance_is_untouched(self):
        bot = Mock(oid=42)
        bot.inventory.return_value = {'items': [dict(oid=i, parent=99) for i in range(90)]}
        self.assertEqual(cc.make_room(bot, set(), set()), [])
        bot.radial.assert_not_called()
        bot.select.assert_not_called()

    def test_room_banks_only_new_surplus_after_walking_to_known_terminal(self):
        bot = Mock(oid=42)
        items = [dict(oid=1, parent=42, name='@item_n:bank'),
                 dict(oid=2, parent=99, name='own gear'),
                 dict(oid=3, parent=99, name='new surplus')]
        bot.inventory.side_effect = lambda: {'items': list(items)}
        terminal = dict(oid=7, x=1, y=2)
        bot.locate.return_value = [terminal]
        bot.go.return_value = {'arrived': True}
        bot.slash.side_effect = lambda *a, **kw: items[2].update(parent=1) or []
        evidence = cc.make_room(bot, {3}, set(), reserve=80)
        bot.go.assert_called_once_with(terminal)
        bot.slash.assert_called_once_with('transferItemMisc', '1 -1 0 0 0', target=3, wait=1)
        bot.radial.assert_not_called()
        self.assertTrue(evidence[-1]['moved'])
        self.assertEqual(items[1]['parent'], 99)

    def test_incomplete_medicine_kit_is_requested_but_complete_one_reused(self):
        from unittest.mock import patch
        bot = Mock(oid=42)
        e = dict(ability='curePoison', setup_tags=['item:cure_pack'], kits=['medicine2'])
        items = []
        bot.inventory.side_effect = lambda: {'items': list(items)}
        with patch.object(cc, 'gear', return_value={'kit': 'medicine2'}) as kit:
            cc.provision(bot, ['medicine2'], [e], {})
            kit.assert_called_once()
            kit.reset_mock()
            items.append(dict(oid=1, parent=99, name='@medicine_name:medpack_cure_poison'))
            result = cc.provision(bot, ['medicine2'], [e], {})
            kit.assert_not_called()
            self.assertIn('skipped', result['medicine2'])

    def test_provision_records_inventory_diff_and_makes_room_before_next_kit(self):
        bot = Mock(oid=42)
        old = dict(oid=1, parent=99, name='own')
        new = dict(oid=2, parent=99, name='kit')
        items = [old]
        bot.inventory.side_effect = lambda: {'items': list(items)}
        def kit(b, name):
            items.append(new) if name == 'basic' else None
            return {'kit': name}
        from unittest.mock import patch
        with patch.object(cc, 'gear', side_effect=kit), patch.object(cc, 'make_room', return_value=[]) as room:
            report = {}
            cc.provision(bot, ['basic', 'medicine2'], [], report)
            self.assertEqual(report['issued_items'], [new])
            self.assertEqual(room.call_args_list[1].args[1], {2})

    def test_treatment_kit_precedes_bulk_support_without_changing_kit_selection(self):
        from unittest.mock import patch
        bot = Mock(oid=42)
        bot.inventory.return_value = {'items': []}
        kits = ['support', 'medicine2']
        with patch.object(cc, 'gear', return_value={}) as gear:
            cc.provision(bot, kits, [], {})
            self.assertEqual([c.args[1] for c in gear.call_args_list], ['medicine2', 'support'])
        self.assertEqual(kits, ['support', 'medicine2'])

    def test_weapon_route_needs_a_carried_stock_weapon_except_unarmed(self):
        bot = Mock()
        bot.inventory.return_value = {'items': [dict(name='@weapon_name:lance_staff_wood_s1')]}
        self.assertTrue(cc.weapon_route(bot, 'weapon:polearm'))
        self.assertTrue(cc.weapon_route(bot, 'weapon:unarmed'))
        self.assertFalse(cc.weapon_route(bot, 'weapon:2h melee'))
        self.assertFalse(cc.weapon_route(bot, 'weapon:lightsaber'))

    def test_equip_takes_the_first_listed_template_that_is_carried(self):
        bot = Mock(oid=42)
        bot.inventory.return_value = {'items': [dict(oid=8, name='@weapon_name:knife_stone', parent=9)]}
        bot.slash.side_effect = lambda *a, **k: bot.inventory.return_value['items'][0].update(parent=42) or []
        ok, evidence = cc.equip(bot, cc.WEAPONS['1h melee'])
        self.assertTrue(ok)
        self.assertEqual(bot.slash.call_args[1]['target'], 8)

    def test_equip_verifies_body_parent_field(self):
        bot = Mock(oid=42)
        bot.inventory.return_value = {'items': [dict(oid=7, name='rifle_cdef', parent=42)]}
        ok, _ = cc.equip(bot, 'rifle_cdef')
        self.assertTrue(ok)
        bot.slash.assert_not_called()  # already in hand: no transfer
        bot.inventory.return_value['items'][0]['parent'] = 99
        self.assertFalse(cc.equip(bot, 'rifle_cdef')[0])


class Rest(unittest.TestCase):
    """rest() asks for /agentgear afflict restore once instead of waiting on regen that wounds have capped."""
    worn = {'me': {'ham': {'health': 279, 'action': 499, 'mind': 1},
                   'max_ham': {'health': 1000, 'action': 1000, 'mind': 500}}}
    fresh = {'me': {'ham': {'health': 1000, 'action': 1000, 'mind': 500},
                    'max_ham': {'health': 1000, 'action': 1000, 'mind': 500}}}

    def test_a_worn_tester_is_restored_without_waiting(self):
        bot = Mock()
        bot.status.side_effect = [self.worn, self.fresh]
        bot.wait_for.return_value = {'text': '[agentgear] {"kit":"afflict","kind":"restore","wounds":[0,0,0,0,0,0,0,0,0]}'}
        self.assertTrue(cc.rest(bot))
        bot.slash.assert_called_once_with('agentGear', 'afflict restore', target=0, wait=0)
        bot.idle.assert_not_called()

    def test_a_server_without_restore_falls_back_to_regen(self):
        bot = Mock()
        bot.status.side_effect = [self.worn, self.fresh]
        bot.wait_for.return_value = {'text': '[agentgear] {"kit":"afflict","error":"usage: /agentgear afflict ..."}'}
        self.assertTrue(cc.rest(bot))
        self.assertEqual(bot.slash.call_count, 1)
        bot.idle.assert_called_once_with(15)


if __name__ == '__main__':
    unittest.main()
