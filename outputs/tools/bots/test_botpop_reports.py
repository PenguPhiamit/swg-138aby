"""Offline contracts for launch telemetry; no server or bot access."""
import json
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from botpop_analysis import gameplay_rows, summarize, run, host_cutoff, main, host, discover_runs, despawn_burst
from botpop_report import report


def row(e, t, **kw):
    return dict(e=e, t=t*1000, **dict({'bot':1}, **kw))


def spawn(bot=1, t=0, role='brawler'):
    return row('spawn', t, role=role, city='Theed', planet='naboo', bot=bot)


class TelemetryTest(unittest.TestCase):
    def test_spawn_exposure_uses_each_arrival(self):
        s = summarize([spawn(), spawn(2,1800), row('server',3600,online=2)])
        self.assertEqual(s['bot_hours'],1.5)

    def test_training_charged_only_new_schema_and_unique_refusals(self):
        rows = [spawn(),row('train',1,cost=250,skill='a'),row('train',2,cost=250,spent=250,skill='b'),
                row('broke',3,skill='c'),row('broke',4,skill='c')]
        tr = summarize(rows)['training']
        self.assertEqual((tr['spent'],tr['nominal_cost'],tr['legacy_free_boxes']),(250,500,1))
        self.assertEqual((tr['refusal_rows'],tr['refused_bot_boxes'],tr['bots_refused']),(2,1,1))

    def test_masked_bank_payment_inferred_from_exact_reward(self):
        rows = [spawn(),row('snap',1,cash=100,bank=1000),row('mission_take',2,lvl=1,mlvl=2,reward=400),
                row('train',3,cost=600,spent=600),row('mission_gone',4,paid=-100,reward=400,secs=2),
                row('snap',5,cash=0,bank=900)]
        s=summarize(rows)
        self.assertEqual(s['income']['missions']['credits'],400)
        self.assertEqual(s['income']['mission_inferred_count'],1)
        self.assertEqual(s['income']['loot_residual']['credits'],0)
        self.assertEqual(s['missions_by_level'][0]['success'],1)

    def test_positive_but_masked_done_uses_reward(self):
        rows=[spawn(),row('snap',1,cash=0,bank=1000),row('mission_take',2,lvl=1,mlvl=2,reward=400),
              row('train',3,cost=250,spent=250),row('mission_done',4,paid=150,reward=400)]
        s=summarize(rows)['income']
        self.assertEqual((s['missions']['credits'],s['mission_inferred_count']),(400,1))

    def test_ambiguous_gone_is_not_assumed_paid(self):
        for before in ([],[row('snap',1,cash=100,bank=1000)]):
            rows=[spawn()]+before+[row('mission_take',2,lvl=1,mlvl=2,reward=400),
                row('train',3,cost=250,spent=250),row('mission_gone',4,paid=-100,reward=400)]
            self.assertEqual(summarize(rows)['income']['mission_inferred_count'],0)

    def test_new_done_not_double_compensated(self):
        rows=[spawn(),row('snap',1,cash=0,bank=1000),row('mission_take',2,lvl=1,mlvl=2,reward=400),
              row('train',3,cost=500,spent=500),row('mission_done',4,paid=400,reward=400)]
        self.assertEqual(summarize(rows)['income']['missions']['credits'],400)

    def test_snapshot_residual_excludes_purse_and_uses_matching_windows(self):
        rows=[spawn(),row('sell',1,credits=100),row('snap',2,cash=1100,bank=100000),
              row('train',3,cost=250,spent=250),row('sell',4,credits=50),
              row('snap',3602,cash=930,bank=100000),row('sell',3603,credits=70)]
        inc=summarize(rows)['income']
        self.assertEqual(inc['junk']['credits'],220)
        self.assertEqual(inc['loot_residual']['credits'],30)
        self.assertEqual(inc['loot_residual']['per_bot_hour'],30)

    def test_mission_denominators_and_acceptance_level(self):
        rows=[spawn(),row('mission_take',1,lvl=1,mlvl=2),row('mission_done',5,lvl=3,paid=100,secs=4),
              row('mission_take',6,lvl=1,mlvl=2),row('mission_abort',9,mlvl=2),row('mission_take',10,lvl=1,mlvl=2)]
        m=summarize(rows)['missions_by_level'][0]
        self.assertEqual((m['taken'],m['success'],m['resolved'],m['pending']),(3,1,2,1))
        self.assertEqual(m['success_per_resolved'],.5)
        self.assertEqual(m['finish_secs']['median'],4)

    def test_despawn_marker_and_explicit_cutoff(self):
        rows=[spawn(),row('despawn',10),row('mission_gone',11,paid=99)]
        kept,info=gameplay_rows(rows)
        self.assertEqual(len(kept),1)
        self.assertEqual(info['excluded_rows'],2)
        self.assertEqual(len(gameplay_rows(rows,9000)[0]),1)

    def test_population_decline_conservative_tail_exclusion(self):
        rows=[spawn(),row('server',5,online=1),row('mission_gone',6),row('server',7,online=0)]
        kept,info=gameplay_rows(rows)
        self.assertEqual(info['cutoff_ms'],5000)
        self.assertEqual([r['e'] for r in kept],['spawn'])

    def test_host_logout_cuts_unsampled_despawn_and_ignores_old_runs(self):
        rows=[spawn(t=100),row('mission_gone',130,paid=99)]
        samples=[{'t':50,'botpop':{'online':0,'logged_out_total':99}},
                 {'t':110,'botpop':{'online':1}},
                 {'t':140,'botpop':{'online':0,'leaving':1}}]
        self.assertEqual(host_cutoff(rows,samples),110000)
        self.assertEqual(summarize(rows,host_cutoff(rows,samples))['income']['missions']['credits'],0)

    def test_levels_lair_distance_and_census(self):
        rows=[spawn(),row('death',1,lvl=2,klvl=10),row('death',2,lvl=2,klvl=9),
              row('lair',3,from_spot=50,secs=70,lair='nest'),row('seen',4,planet='ossus',kind='creature',name='bird'),
              row('seen',5,planet='ossus',kind='creature',name='bird')]
        s=summarize(rows)
        self.assertEqual(s['killer_at_least_8_above'],1)
        self.assertEqual(s['lair_from_spot_m']['median'],50)
        self.assertEqual(s['census'][0]['observations'],2)

    def test_partial_json_and_empty_run(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'events.jsonl';p.write_text('{"e":"server","t":1}\n{"e":')
            self.assertEqual(run('empty',p)['event_counts'],{'server':1})
        self.assertIn('No spawn',report([],[]))

    def test_one_command_generates_json_and_markdown_and_1700_host(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            events=td/'events.jsonl';events.write_text('{"e":"server","t":1000}\n')
            samples=td/'host.jsonl'
            samples.write_text('\n'.join(json.dumps({'t':t,'rss_mb':100+t,'cores':2,'wsl_avail_mb':500,
                                'botpop':{'online':1700,'pass_ms':3}}) for t in range(0,1001,100)))
            out=td/'analysis.json';numbers=td/'numbers.md'
            with contextlib.redirect_stdout(io.StringIO()):
                main([str(out),'--run','run6='+str(events),'--host',str(samples),'--numbers-out',str(numbers)])
            self.assertEqual(json.loads(out.read_text())['runs'][0]['run'],'run6')
            self.assertIn('No spawn',numbers.read_text())
            self.assertEqual(host([samples])[0]['online'],1700)

    def test_report_charged_training_and_new_tables(self):
        rows=[spawn(),row('snap',1,cash=100,bank=1000,role='brawler',boxes=0,lvl=1,min=1,planet='naboo',city='Theed',x=0,y=0),
              row('train',2,cost=250,spent=250,skill='abc',boxes=1,min=1,lvl=2),row('server',3600,online=1,tick_ms_avg=1)]
        text=report(rows,[])
        for expected in ('Paid 250 credits','Spawn level gate','Missions (','Ossus census','loot_residual','Income per bot-hour, by role'):
            self.assertIn(expected,text)
        self.assertNotIn('not charged',text)
        self.assertIn('the same as the rows above',text)

    # ---- C47 extension: run 7 rows, income by role, missions, level gap, final despawn, run discovery ----

    def test_final_despawn_burst_of_mission_gone_is_cut(self):
        live = [spawn(), row('mission_take',1,lvl=1,mlvl=1,reward=100), row('kill',50,target='x')]
        burst = ([row('mission_gone',100,bot=b+10,paid=0) for b in range(4)]
                 + [row('mission_gone',100.4,bot=b+20,paid=0) for b in range(3)] + [row('widen',100.5)])
        kept,info = gameplay_rows(live+burst)
        self.assertEqual((info['cutoff_ms'],info['excluded_rows'],info['excluded_mission_gone']),(100000,8,7))
        self.assertEqual(len(kept),3)
        s = summarize(live+burst)
        self.assertEqual(s['mission_outcomes'],{})
        self.assertEqual(s['missions_total']['pending'],1)

    def test_burst_needs_a_cluster_at_the_end_of_the_file(self):
        live = [spawn(), row('kill',50,target='x')]
        burst = [row('mission_gone',100,bot=b+10) for b in range(6)]
        self.assertIsNone(despawn_burst(live+burst+[row('kill',160,target='y')]))  # bots kept playing: not a despawn
        self.assertEqual(despawn_burst(live+burst+[{'e':'server','t':500000,'online':0}]),100000)  # only server rows follow
        self.assertIsNone(despawn_burst(live+burst[:4]))  # four in a second is ordinary
        slow = [row('mission_gone',100+i*3,bot=i+10) for i in range(10)]
        self.assertIsNone(despawn_burst(live+slow))  # one every three seconds is ordinary
        self.assertIsNone(despawn_burst(live))

    def test_a_few_logouts_do_not_look_like_a_despawn(self):
        rows = [spawn(),row('server',10,online=1700),row('server',70,online=1699),row('server',130,online=1700),row('kill',140)]
        self.assertIsNone(gameplay_rows(rows)[1]['cutoff_ms'])
        self.assertEqual(gameplay_rows(rows+[row('server',190,online=1000),row('kill',191)])[1]['cutoff_ms'],130000)
        samples = [{'t':10+30*i,'botpop':{'online':1700-(i>1),'logged_out_total':int(i>1),'leaving':int(i==3)}} for i in range(5)]
        events = [spawn(),row('kill',200)]
        self.assertIsNone(host_cutoff(events,samples))
        samples.append({'t':160,'botpop':{'online':1000,'leaving':700,'queued_logout':1000,'logged_out_total':1}})
        self.assertEqual(host_cutoff(events,samples),130000)

    def test_income_per_bot_hour_by_role_adds_up_to_the_totals(self):
        rows = [spawn(1,0),spawn(2,0,'medic'),
                row('snap',0,bot=1,cash=100,bank=1000),row('snap',0,bot=2,cash=100,bank=1000),
                row('mission_take',50,bot=1,lvl=2,mlvl=2,reward=400),
                row('mission_done',100,bot=1,paid=400,reward=400,mlvl=2,secs=50,lvl=2),
                row('sell',200,bot=1,items=2,credits=50,cash=150),
                row('train',300,bot=1,cost=250,spent=250,credits=1550,skill='a'),
                row('train',301,bot=2,cost=250,spent=250,credits=1100,skill='b'),
                row('snap',3600,bot=1,cash=0,bank=1330),row('snap',3600,bot=2,cash=0,bank=850)]
        inc = summarize(rows)['income']
        brawler,medic = inc['by_role']['brawler'],inc['by_role']['medic']
        self.assertEqual((brawler['bot_hours'],medic['bot_hours']),(1.0,1.0))
        self.assertEqual((brawler['missions']['per_bot_hour'],brawler['junk']['per_bot_hour'],brawler['loot_residual']['per_bot_hour']),(400,50,30))
        self.assertEqual((brawler['training_spent'],medic['training_spent'],brawler['income_per_bot_hour']),(250,250,480))
        self.assertEqual((medic['missions']['credits'],medic['junk']['credits'],medic['loot_residual']['credits']),(0,0,0))
        for source in ('missions','junk','loot_residual'):
            self.assertEqual(inc[source]['credits'],sum(v[source]['credits'] for v in inc['by_role'].values()))

    def test_training_refusals_are_counted_per_bot_and_box_with_shortfall(self):
        rows = [spawn(1,0),spawn(2,0,'medic'),
                row('broke',1,bot=1,skill='a',cost=500,credits=350),row('broke',2,bot=1,skill='b',cost=500,credits=450),
                row('broke',3,bot=1,skill='a',cost=500,credits=350),row('broke',4,bot=2,skill='a',cost=500,credits=250)]
        s = summarize(rows)
        training = s['training']
        self.assertEqual((training['refusal_rows'],training['refused_bot_boxes'],training['bots_refused']),(4,3,2))
        self.assertEqual(training['refused_skills'],{'a':2,'b':1})
        self.assertEqual((training['refusal_shortfall']['median'],training['refusal_shortfall']['max']),(150,250))
        self.assertEqual(s['income']['by_role']['medic']['refused_bot_boxes'],1)

    def test_mission_groups_count_done_gone_aborted_and_minutes(self):
        rows = [spawn(1,0),spawn(2,0,'scout'),
                row('mission_take',1,bot=1,lvl=2,mlvl=3,reward=500,offered=6,dist=1000),
                row('mission_done',361,bot=1,lvl=2,mlvl=3,reward=500,paid=500,secs=360),
                row('mission_take',400,bot=1,lvl=2,mlvl=3,reward=500),
                row('mission_gone',500,bot=1,lvl=2,mlvl=3,reward=500,paid=0,secs=100),
                row('mission_take',2,bot=2,lvl=2,mlvl=3,reward=500),
                row('mission_abort',1202,bot=2,mlvl=3,reward=500),
                row('mission_take',1300,bot=2,lvl=3,mlvl=5,reward=900)]
        s = summarize(rows)
        cell = s['missions_by_level'][0]
        self.assertEqual((cell['bot_level'],cell['mission_level']),(2,3))
        self.assertEqual((cell['taken'],cell['done'],cell['gone'],cell['aborted'],cell['pending'],cell['resolved']),(3,1,1,1,0,3))
        self.assertEqual((cell['success'],cell['finish_minutes']['median']),(1,6.0))
        self.assertAlmostEqual(cell['success_per_taken'],1/3)
        self.assertEqual(s['missions_by_level'][1]['pending'],1)
        self.assertEqual([(g['level_gap'],g['taken']) for g in s['missions_by_level_gap']],[(1,3),(2,1)])
        self.assertEqual([(g['bot_level'],g['taken']) for g in s['missions_by_bot_level']],[(2,3),(3,1)])
        self.assertEqual([(g['mission_level'],g['taken']) for g in s['missions_by_mission_level']],[(3,3),(5,1)])
        roles = {g['role']:g for g in s['missions_by_role']}
        self.assertEqual((roles['brawler']['done'],roles['brawler']['gone'],roles['scout']['aborted'],roles['scout']['pending']),(1,1,1,1))
        total = s['missions_total']
        self.assertEqual((total['taken'],total['done'],total['gone'],total['aborted'],total['pending']),(4,1,1,1,1))

    def test_outcome_without_a_take_counts_income_but_stays_out_of_the_tables(self):
        s = summarize([spawn(),row('mission_done',5,paid=100,reward=100,mlvl=2,lvl=2,secs=4)])
        self.assertEqual(s['income']['missions']['credits'],100)
        self.assertEqual((s['mission_outcomes_unmatched'],s['missions_total']['resolved']),(1,0))

    def test_deaths_by_killer_level_minus_bot_level(self):
        rows = [spawn(),row('death',1,lvl=1,klvl=5,killer='a',planet='naboo'),row('death',2,lvl=1,klvl=9,killer='b',planet='rori'),
                row('death',3,lvl=1,klvl=13,killer='b',planet='rori'),row('death',4,lvl=1,klvl=1,killer='c',planet='naboo'),
                row('death',5,lvl=1,klvl=0,killer=''),row('death',6,lvl=3,klvl=11,killer='b',planet='rori')]
        s = summarize(rows)
        self.assertEqual(s['deaths_by_gap'],{'0':1,'4':1,'8':2,'12':1})
        self.assertEqual(s['deaths_by_gap_bucket'],{'<= 0':1,'1-2':0,'3-4':1,'5-7':0,'8-11':2,'12+':1})
        self.assertEqual((s['death_gap']['known'],s['death_gap']['unknown_killer'],s['death_gap']['median']),(5,1,8.0))
        self.assertEqual(s['killer_at_least_8_above'],3)
        self.assertEqual(s['gate_leaks'][0],{'killer':'b','killer_level':9,'planet':'rori','deaths':1})
        self.assertEqual(len(s['gate_leaks']),3)

    def test_discover_runs_names_orders_and_skips(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            def write(name, start, minutes):
                lines = ({'e':'launch','t':start*1000},{'e':'snap','t':(start+minutes*60)*1000})
                (td/name).write_text('\n'.join(json.dumps(r) for r in lines)+'\n')
            write('botpop-launch-run2.jsonl',1792110823,165)
            write('botpop-launch.jsonl.2027.old',1792110833,168)
            write('botpop-launch.jsonl.2211.old',1792127069,3)
            write('botpop-launch.jsonl.2353.old',1792132336,16)
            write('botpop-launch.jsonl.0001.old',1700000000,30)
            write('botpop-launch.jsonl',1792133596,50)
            (td/'botpop-launch.jsonl.1709.old').write_text('{"e":')
            found = discover_runs(str(td),str(td))
            used = [f for f in found if f[4] is None]
            self.assertEqual([f[0] for f in used][1:],['run2','run6','run7'])
            self.assertTrue(used[0][0].startswith('r') and not used[0][0].startswith('run'))
            why = {Path(f[1]).name:f[4] for f in found}
            self.assertEqual(why['botpop-launch.jsonl.2027.old'],'same run as an earlier file')
            self.assertIn('under 5',why['botpop-launch.jsonl.2211.old'])
            self.assertEqual(why['botpop-launch.jsonl.1709.old'],'empty or unreadable')

    def test_one_command_finds_logs_and_compares_every_run_with_the_newest(self):
        def log(path, start, klvls):
            at = lambda r, ms: dict(r, t=start*1000+ms)
            rows = [at(row('launch',0),0), at(spawn(),0),
                    at(row('snap',1,cash=100,bank=1000,role='brawler',boxes=0,lvl=1,min=1,planet='naboo',city='Theed',x=0,y=0),1000)]
            rows += [at(row('death',2,lvl=1,klvl=k,killer='k',planet='naboo',city='Theed',x=0,y=0),2000) for k in klvls]
            rows += [at(row('server',3,online=1,tick_ms_avg=1),600000)]
            path.write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            log(td/'botpop-launch.jsonl.2353.old',1792132336,[10,11])
            log(td/'botpop-launch.jsonl',1792133596,[2])
            nohost = td/'host.jsonl'
            nohost.write_text('')
            args = ['--log-dir',str(td),'--agent-dir',str(td),'--host',str(nohost)]
            shown = io.StringIO()
            with contextlib.redirect_stdout(shown):
                main(args+['--list'])
            self.assertIn('run6',shown.getvalue())
            self.assertIn('run7',shown.getvalue())
            out,numbers = td/'analysis.json',td/'numbers.md'
            with contextlib.redirect_stdout(io.StringIO()):
                main([str(out),'--numbers-out',str(numbers)]+args)
            self.assertEqual([r['run'] for r in json.loads(out.read_text())['runs']],['run6','run7'])
            text = numbers.read_text()
            self.assertIn('this report is about run7',text)
            self.assertIn('| gap | run6 | run7 |',text)
            with contextlib.redirect_stdout(io.StringIO()):
                main([str(out),'--numbers-out',str(numbers),'--current','run6']+args)
            self.assertIn('this report is about run6',numbers.read_text())

    def test_report_shows_runs_compared_and_gap_bands(self):
        def events(t0, klvls):
            at = lambda r, ms: dict(r, t=t0*1000+ms)
            snap = row('snap',1,cash=100,bank=1000,role='brawler',boxes=0,lvl=1,min=1,planet='naboo',city='Theed',x=0,y=0)
            rows = [at(spawn(),0),at(snap,1000)]
            rows += [at(row('death',2,lvl=1,klvl=k,killer='k',planet='naboo',city='Theed',x=0,y=0),2000) for k in klvls]
            return rows+[at(row('server',3600,online=1,tick_ms_avg=1),3600000)]
        text = report(events(10000,[2,3]),[],comparisons=[('run6',events(0,[10,12,20]))],name='run7')
        self.assertIn('this report is about run7',text)
        self.assertIn('| gap | run6 | run7 |',text)
        self.assertIn('| 1-2 | 0% (0) | 100% (2) |',text)
        self.assertIn('| 8-11 | 67% (2) | 0% (0) |',text)
        self.assertIn('| 12+ | 33% (1) | 0% (0) |',text)
        self.assertLess(text.index('| run6 |'),text.index('| run7 |'))  # oldest run first
        self.assertNotIn('Killers 8 or more',text)  # none of this run's killers is 8 levels above its bot


if __name__=='__main__':
    unittest.main()
