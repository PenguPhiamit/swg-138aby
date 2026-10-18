from pathlib import Path
p=Path('outputs/tools/bots/botpop_report.py');s=p.read_text()
s=s.replace('import collections','import argparse\nimport collections',1)
s=s.replace('from datetime import datetime','from datetime import datetime\nfrom botpop_analysis import gameplay_rows, summarize')
s=s.replace('def report(events, host):','def report(events, host, until_ms=None, comparisons=()):\n    summary = summarize(events, until_ms)\n    events, _ = gameplay_rows(events, until_ms)')
s=s.replace("    hours = max((t1 - t0) / 3600, 1e-6)","    hours = max((t1 - t0) / 3600, 1e-6)\n    host = [r for r in host if t0 <= r.get('t', 0) <= t1]")
a=s.index('    md.append(f"Credits held now:');b=s.index('    sells =',a)
s=s[:a]+'''    tr = summary['training']
    md.append(f"Credits held now: total {sum(cash)}, median {median(cash)}, best {max(cash) if cash else 0}. "
              f"Training paid {tr['spent']} credits for {tr['charged_boxes']} boxes; "
              f"legacy free boxes {tr['legacy_free_boxes']}, nominal cost {tr['nominal_cost']}. "
              f"Refused for credits: {tr['refusal_rows']} rows, {tr['refused_bot_boxes']} distinct bot/box pairs, "
              f"{tr['bots_refused']} bots. Corpses looted {sum(r.get('loots',0) for r in last.values())}.")
    income = summary['income']
    md.append(table(['source', 'credits', 'credits/bot-hour'],
                    [[k, income[k]['credits'], income[k]['per_bot_hour']] for k in ('missions','junk','loot_residual')]))
    md.append(income['method'])
    md.append(f"Exposure: {summary['bot_hours']} bot-hours for event income; "
              f"{income['loot_residual']['bot_hours']} for snapshot residual. {income['inference']} "
              f"Inferred payments: {income['mission_inferred_count']} / {income['mission_inferred_credits']} credits.")
''' + s[b:]
a=s.index('    # Support roles')
s=s[:a]+'''    md.append('## Missions (pending attempts are censored at the report boundary)\\n')
    md.append(table(['bot level','mission level','taken','success','resolved','pending','success/taken','success/resolved','finish median s','finish max s','reward median','offered median','trip median m'],
                    [[r['bot_level'],r['mission_level'],r['taken'],r['success'],r['resolved'],r['pending'],
                      pct(r['success'],r['taken']),pct(r['success'],r['resolved']),r['finish_secs']['median'],r['finish_secs']['max'],
                      r['reward']['median'],r['offered']['median'],r['distance_m']['median']] for r in summary['missions_by_level']]))
    md.append('Resolved = done, gone or aborted; gone without reconciled payment counts as unsuccessful. Pending attempts are excluded from success/resolved. Level is the bot level at acceptance.')
    md.append('Mission outcomes: ' + json.dumps(summary['mission_outcomes']) + '. Other rows: ' +
              ', '.join(f"{k} {len(by[k])}" for k in ('mission_none','terminal','explore','seen')) + '.')
    md.append('Lair distance from mission spot (metres): ' + json.dumps(summary['lair_from_spot_m']) +
              '; seconds to find lair: ' + json.dumps(summary['lair_find_secs']) + '.')
    md.append(table(['lair','finds'], sorted(summary['lairs_by_name'].items())))
    md.append('## Spawn level gate comparison\\n')
    compare = [(name,summarize(rs)) for name,rs in comparisons] + [('current',summary)]
    md.append(table(['run','bot-hours','deaths','deaths/bot-hour','killer >= bot + 8','share of deaths'],
                    [[n,r['bot_hours'],r['deaths'],r['deaths_per_bot_hour'],r['killer_at_least_8_above'],
                      pct(r['killer_at_least_8_above'],r['deaths'])] for n,r in compare]))
    md.append('Descriptive comparison: runs differ in duration, purse, population (including explorers), missions and bot behaviour; this does not isolate the gate as a cause.')
    md.append(table(['run','bot level','killer level','deaths'],
                    [[n,d['bot_level'],d['killer_level'],d['deaths']] for n,r in compare for d in r['deaths_by_levels']]))
    md.append('Final despawn exclusions: ' + json.dumps({n:r['exclusion'] for n,r in compare}) + '.')
    md.append('## Ossus census\\n')
    md.append(f"Explorers requested: {summary['explorers_requested']}. Seen rows are observations, not a unique-object census (no object IDs).")
    md.append(table(['planet','kind','name','observations'],
                    [[r['planet'],r['kind'],r['name'],r['observations']] for r in summary['census']]))

''' +s[a:]
a=s.index('def main(argv):');s=s[:a]+'''def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('events', nargs='?', default=EVENTS)
    parser.add_argument('--host', action='append')
    parser.add_argument('--out', default=os.path.join(SIM,'numbers.md'))
    parser.add_argument('--until-ms', type=int)
    parser.add_argument('--compare', action='append', default=[], metavar='NAME=PATH')
    args = parser.parse_args(argv)
    host_files = args.host or sorted(glob.glob(os.path.join(SIM,'host-*.jsonl')))
    host = [r for f in host_files for r in load(f)]
    comparisons = [(n,load(p)) for n,p in (x.split('=',1) for x in args.compare)]
    text = report(load(args.events), host, args.until_ms, comparisons)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\\n') as f:
        f.write(text)
    print(f'wrote {args.out} ({len(text)} chars)')


if __name__ == '__main__':
    main()
'''
p.write_bytes(s.replace('\n','\r\n').encode())
p=Path('outputs/tools/bots/botpop_analysis.py');s=p.read_text()
s=s.replace('cash, bank_spent, pending = {}, collections.Counter(), {}','cash, bank_spent, pending = {}, collections.Counter(), {}\n    unknown_training = collections.Counter()')
s=s.replace('            training.append(dict(r, charged=charged, bank_withdrawal=withdrawal))','            if withdrawal is None:\n                unknown_training[b] += 1\n            training.append(dict(r, charged=charged, bank_withdrawal=withdrawal))')
s=s.replace("len([t for t in training if t['bot'] == b and t['bank_withdrawal'] is None])",'unknown_training[b]')
s=s.replace("sum(t['bot'] == b and t['bank_withdrawal'] is None for t in training) - unknown",'unknown_training[b] - unknown')
p.write_bytes(s.replace('\n','\r\n').encode())
