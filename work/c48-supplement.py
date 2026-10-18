import sys, json, collections, statistics, re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
sys.path.insert(0, str(ROOT/'tools/bots'))
import botpop_analysis as a
TZ = ZoneInfo('America/Los_Angeles')
def when(t):
    return datetime.fromtimestamp(t/1000, TZ).strftime('%-I:%M %p')
data=json.loads((ROOT/'Bot-reports/launch-sim/analysis.json').read_text())
result=data['runs'][-1]
raw=a.load(result['path'])
# Use precisely the end read by the standard analysis, rather than later live rows.
raw=[r for r in raw if r['t'] <= result['end_ms']]
host_samples=[r for p in sorted((ROOT/'Bot-reports/launch-sim').glob('host-*.jsonl')) for r in a.load(p)]
rows, exclusion=a.gameplay_rows(raw, a.host_cutoff(raw,host_samples))
from botpop_report import report
sim=ROOT/'Bot-reports/launch-sim'
(sim/'numbers-run8.md').write_text(report(raw,host_samples,None,[(r['run'],r) for r in data['runs'][:-1]],name='run8'),encoding='utf-8')
spawn={r['bot']:r for r in rows if r.get('e')=='spawn'}
latest={r['bot']:r for r in rows if r.get('e')=='snap'}
groups=collections.defaultdict(set)
for b,r in spawn.items(): groups[(r.get('style','unlabeled'),r.get('sp','unlabeled'))].add(b)
lines=['# Run 8: styles, point budgets and watchdog','',f"16 Oct 2026, {when(result['start_ms'])} to {when(result['end_ms'])} Pacific. Active-run checkpoint, not the finished night.",'',
'Source: the same event-log prefix as `analysis.json` and [numbers-run8.md](numbers-run8.md), read in WSL as swgemu. Run 8 is auto-discovered as `r16-0113`; the first spawn is at 1:13 AM (the board rounds it to about 1:20 AM). No server writes, bot commands or restarts. The standard report was regenerated from that fixed prefix to prevent its second live read extending the window.','',
'Rows below group bots by their spawn `style` and `sp` labels, retaining all their later events. Explorers are separate. Boxes means train events, including novice purchases; XP column is medical XP still banked at the last snapshot, not lifetime earned. Mission outcomes use the standard tool\'s matching and payment accounting. Bot-hours run from each spawn to the shared endpoint, so later spawning is allowed for.','',
'| Style | SP label | Bots | Bot-hours | Kills | Deaths | Missions taken / success / pending | Training boxes | Training paid | Latest boxes median | Medical XP median |',
'|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|']
allstats=[]
for (style,sp),bots in sorted(groups.items(),key=lambda x:(x[0][0],str(x[0][1]))):
    sub=[r for r in rows if r.get('bot') in bots]
    # A neutral endpoint row ensures all groups use the same duration.
    summary=a.summarize(sub+[{'e':'checkpoint','t':result['end_ms']}])
    m=summary['missions_total']; ev=summary['event_counts']
    snaps=[latest[b] for b in bots if b in latest]
    val=[style,sp,len(bots),summary['bot_hours'],ev.get('kill',0),ev.get('death',0),f"{m['taken']} / {m['success']} / {m['pending']}",ev.get('train',0),summary['training']['spent'],a.med([r['boxes'] for r in snaps if 'boxes' in r]),a.med([r.get('xp',{}).get('medical',0) for r in snaps])]
    lines.append('| '+' | '.join(str(x) for x in val)+' |')
    allstats.append({'style':style,'sp':sp,'bots':len(bots),'summary':summary})
lines += ['',f"Coverage: {sum(len(b) for b in groups.values())} spawn identities; {len(latest)} with a snapshot. Logout exclusion: {exclusion}.",'',
'**Point-cap caution:** `sp` is the assigned budget label, not demonstrated consumption. Latest snapshots with `sp_left` greater than their `sp` label: '+str(sum(r.get('sp_left',0)>r.get('sp',100000) for r in latest.values()))+'. This needs source/runtime checking before any claim that 250 versus 1,000 caps are enforced. Do not interpret different style outcomes as a controlled balance test: weapon choice, city, activity and initial skills also differ.','',
'**Healing:** Core3 awards no medical XP for self-healing. Heal counts alone do not establish medical progression; bots should heal injured allies, and the next check should distinguish self from other and XP actually awarded. Use the researched [buying orders](../../Documentation-support/precu-player-builds.md), including XP-cap priority and skipping unaffordable boxes.','',
'## Watchdog','', 'Read `/var/tmp/swg-bots/watchdog.log` without changing it. Times below are Pacific on the night of 15–16 Oct; MB are the log\'s units.']
watch=Path('/var/tmp/swg-bots/watchdog.log').read_text()
samples=[]
for line in watch.splitlines():
    m=re.fullmatch(r'(\d\d):(\d\d) available (\d+) MB, core3 (\d+) MB',line)
    if m:
        h,mi,avail,rss=map(int,m.groups())
        if 80<=h*60+mi<=(datetime.fromtimestamp(result['end_ms']/1000,TZ).hour*60+datetime.fromtimestamp(result['end_ms']/1000,TZ).minute): samples.append((h,mi,avail,rss))
lines += ['', '| Time | Available MB | core3 MB |','|---|---:|---:|']
for h,mi,av,rss in samples:
    lines.append(f"| {h%12 or 12}:{mi:02} {'AM' if h<12 else 'PM'} | {av} | {rss} |")
lines += ['',f"Run-8 samples: {len(samples)}; minimum available {min(s[2] for s in samples):,} MB; core3 {samples[0][3]:,} to {samples[-1][3]:,} MB. No threshold/despawn message appears in the captured log. The earlier 1:11 AM entry says `watchdog: core3 not running`; it precedes run 8 and does not state a cause. Sampling every ten minutes cannot exclude a shorter dip. These samples show memory growth, not its cause or a proven leak.",'',
'The earlier logged samples run from 10:50 PM (7,758 MB available, core3 7,718 MB) through 1:10 AM (6,744 / 8,606 MB). They include earlier runs and must not be fitted as run-8 growth. The 2 GB watchdog remains a safety threshold, not a forecast.','']
(sim/'run8-style-watchdog.md').write_text('\n'.join(lines),encoding='utf-8')
(ROOT.parent/'work/c48-summary.json').write_text(json.dumps({'result':result,'groups':allstats},indent=1))
assert sum(g['summary']['kills'] for g in allstats)==result['kills']
assert sum(g['summary']['deaths'] for g in allstats)==result['deaths']
assert sum(g['summary']['training']['charged_boxes'] for g in allstats)==result['training']['charged_boxes']
print('Wrote numbers-run8.md and run8-style-watchdog.md; grouped kills/deaths/charged training reconcile.')
print('MISSIONS',result['missions_total']); print('DEATHS',result['killer_at_least_8_above']); print('INCOME',result['income']['missions'])
