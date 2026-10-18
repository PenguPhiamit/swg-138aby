from pathlib import Path
p=Path('outputs/Documentation-support/player-cities-research.md')
s=p.read_text(encoding='utf-8')
lines=s.splitlines()
r={
12:'2. **Notable cities had a purpose:** Hero\'s Legacy was a guild fortress under base raids, and Elysium had three malls and a temple. Sections 1.3 and 1.4.',
13:'3. **What kept them:** a guild or friend group that stays, room and services, and rules that clear inactive cities (live removed inactive citizens from 1 May 2009; Infinity prepared inactive cities for demolition in 2023). **What stalled them:** city caps (the SOE list) and upkeep (our calculation in 2.6).',
19:'9. **Creativity evidence retained:** Home Shows on Empire in Flames and Finalizer, Infinity\'s Best Dressed City, free-form object placement on live, and the decoration-limit increase in Game Update 8. Section 4.',
20:'10. **Owner-approved direction:** a monthly Home Show / Best Dressed City with a modest credit prize; test 30 decorations per rank and zero decoration upkeep; make Clone Lab and Entertainment District work at configured values; a 10-static-prop pilot. No terrain edits or cities on Hoth/Ossus. Disposable bot towns come first. See the answered question list and [M1 plan](bot-cities-plan.md).',
28:'- **Provenance:** only the retained sources below support this revision; no material from the excluded servers is an implementation dependency.',
66:'2. **Slots saturate on a big server.** Starsider was at its cap in the 2011 SOE list. Live removed citizens inactive 90 days (Game Update 8, effective 1 May 2009) [official]; Infinity prepared inactive cities for demolition in March 2023 [press: mmofolklorist roundup].',
67:'3. **Services draw crowds.** Entertainers and medics work in player cantinas and hospitals; merchants moved into big cities [press: Unwinnable, snippet]. Our launch run recorded 2,659 of 2,661 rests watching a dancer where hurt hunters, medics and dancers met [measured: `FINDINGS.md` section 6].',
68:'4. **Terrain constrains placement here.** Core3 checks build permission and footprints and does not flatten terrain [code: 2.2]. Select naturally suitable sites; owner Q10 forbids terrain edits.',
69:'5. **Identity is a design goal.** Guild homes and Elysium\'s three approved house styles are retained examples [community: guild pages, City:Elysium]. Their effect on retention has not been measured here.',
75:'| **Black Sands** | Gorath, Tatooine; founded 29 Mar 2004; rank 4 in Feb 2011 | Listed in SOE\'s survivor snapshot | No development history retained | Present in the February 2011 list | [official][archive] SOE list 2011 |',
298:'| Crafters\' market | Elysium malls | hall, plaza, ring of shops and houses, Research Center |',
299:'| Role-play town | Original layout proposal; no retained case-specific evidence | main street with cantina at one end, theater at the other |',
413:'| **Contests with a prize or badge** | Empire in Flames first show Jun 2023 (winner\'s badge); Finalizer first show 26 Jun-5 Jul 2023; Infinity Best Dressed City (May 2023) | public recognition and entries using props and furniture | [press] mmofolklorist May-Jul 2023 |',
415:'| **Better tools** | SWGEmu rotate on every axis (Apr 2023); Core3 yaw, pitch and roll | lowers layout effort | [press] mmofolklorist Apr 2023; [code] `RotateFurnitureCommand.h` |',
416:'| **Decoration limits that grow** | live GU8: base decorations/civic structures +50%; Outdoor Enhancement +33% | greater placement capacity | [official] Game Update 8 notes |',
417:'| **Event staging** | Storyteller (Chapter 6, 22 May 2007); GU8 extends Storyteller lifetime in cities and with Encore Performance | temporary scene dressing | [press] Shacknews and Engadget search summaries; [official] GU8 |',
418:'| **Specializations** | Core3 has eight configured options, two without consumers at the research snapshot | distinct services are possible; implementation gaps remain | [code] 2.5 |',
419:'| **Added planets with cities** | Stardust\'s added planets | additional sites | [community] Stardust wiki |',
421:'| **Recognition** | SOE\'s public city list | public visibility; retention effect unmeasured | [official][archive] SOE list |',
424:'Stronghold was removed on live in Game Update 8 [official]. The retained research does not establish a general outcome for raising upkeep or changing thresholds.',
440:'| 2 | **Test decoration freedom:** 30 per rank, zero decoration upkeep | separate test configuration for decoration upkeep; leave terminal/trainer charges and placement cost unchanged | S-M | current rank-5 decoration upkeep is 37,500 per week [calc]; owner Q7 authorizes a test | object count; distinguish decorations from props |',
442:'| 4 | **Naturally suitable founding sites**; terrain edits rejected by owner Q10 | census and server validation | M | Core3 does not flatten terrain | no-build zones, slope and footprints |',
443:'| 5 | **Mayor-pinned static event props**, pilot 10 per city (owner Q11) | static-template allow-list, city ownership/count, removal and teardown | S-M | original proposal reusing existing static props | rental timers, collision, quota enforcement |',
444:'| 6 | **Visible rank rewards**: banners, a plaza or a landmark from existing art | design and template review | M | original optional design; not approved as extra slots | object count and art provenance |',
445:'| 7 | **Spotlight and gallery** alongside the monthly contest | staff process, explicit permission before posting | S | original recognition proposal; SOE listed cities publicly | Discord approval |',
446:'| 8 | **CitiesAllowed safety guard only**: safely refuse missing/zero entries; Hoth and Ossus remain forbidden (owner Q9) | validate current guard; regression probes | S | prevents invalid indexing without enabling planets | fail-open behavior |',
451:'| 13 | **New civic structures**: original park, library or observatory proposal | existing licensed meshes/templates or own art pipeline; Claude and GPT only | M-L | optional things to build | art rights and scope; outside M1 |',
453:'| 15 | **Terraforming** | terrain changes | L | rejected for founding sites by owner Q10 | outside approved plan |',
}
drop={92,93,94,96,422,498,499,500,505,506,507,508}
out=[]
for i,l in enumerate(lines,1):
 if i in drop: continue
 l=r.get(i,l)
 if 118<=i<=127:
  cells=l.split('|'); l='|'.join(cells[:6]+cells[8:])
 l=l.replace("MassivelyOP's Felucia article, ",'').replace("Legends' spring 2024 newsletter, ",'').replace('MassivelyOP Felucia headline (https://massivelyop.com/?p=239683); ','').replace("Legends' spring 2024 newsletter; ",'')
 l=l.replace('ruin-themed ring on Ossus','ruin-themed ring on an allowed planet')
 l=l.replace('Five servers ran it in 2023','Retained examples are Empire in Flames, Finalizer and Infinity')
 out.append(l)
s='\n'.join(out)+'\n'
s=s.replace('\n\n16 Oct 2026,', '\n\n**16 Oct revision (C52): SWG Legends and SWG Restoration citations and claims dependent only on them were removed at the owner\'s request (Q13, 05:40). Owner answers below supersede the original proposals; [bot-cities-plan.md](bot-cities-plan.md) is the current M1 plan.**\n\n16 Oct 2026,',1)
s=s.replace('5. **Empty `CitiesAllowed` entry** (2.11 item 1). Do not test on Hoth or Ossus until `CitiesAllowed` lists them and `isCityRankCapped` guards a missing key.','5. **Empty `CitiesAllowed` entry** (historical finding, 2.11 item 1). Verify safe refusal only; Hoth and Ossus must stay forbidden (owner Q9).')
s=s.replace('and idea 8\'s Lua and guard, after probe 2.','and verification of idea 8\'s guard, after safe-refusal probes.')
s=s.replace('idea 4 for the first two sites on Tatooine and Rori.','idea 4 selects natural sites on an eligible planet, with no terrain edits.')
s=s.replace('3. **Quota.** Bots may use at most **30% of each planet\'s slots at each rank** (core planets: 6 cities, others: 15),','3. **Quota.** Bots may use at most **30% of each planet\'s slots at each rank** (rank-1 caps: core 6, others 15; higher-rank limits are smaller, see the M1 plan),')
answers=[
'Disposable simulation towns first; persistent towns later from a staff Town Keeper.',
'A 6-minute simulated week on the test copy only.',
'At most 30% of a planet\'s city slots, never on the planet the owner is testing.',
'Political XP grants only in labeled accelerated runs; keep the natural baseline.',
'Bots donate plus logged treasury top-ups, with a no-top-up baseline; upkeep x0.5 stays.',
'A monthly Home Show / Best Dressed City with a modest credit prize. Posting still needs approval.',
'Test 30 decorations per rank and zero decoration upkeep.',
'Make Clone Lab and Entertainment District work at their configured values.',
'The CitiesAllowed guard only; no player cities on Hoth or Ossus.',
'No terrain edits for founding sites.',
'A pilot of 10 static event props per city.',
'Era-fitting names and themes from our own lists (138-139 ABY).',
'Do not cite SWG Legends or SWG Restoration pages; those citations and sole-source claims are removed in this revision.'
]
a=s.index("## Owner's questions")
b=s.index('## Sources',a)
part=s[a:b]
for n,answer in enumerate(answers,1):
 ls=part.splitlines()
 idx=next(i for i,l in enumerate(ls) if l.startswith(f'{n}. '))
 ls.insert(idx+1,'   **Owner, 16 Oct 05:40:** '+answer)
 part='\n'.join(ls)+'\n'
s=s[:a]+part+'\n'+s[b:]
s=s.replace('**Provenance.** Are you comfortable with me citing Legends and Restoration\'s public wiki and news pages as evidence (they are not on SWGEmu\'s AGPL-compliant list)? I used nothing else from them. Sentinel\'s Republic was left out as you asked.','**Provenance.** May the two disputed servers\' public wiki/news pages be cited?')
p.write_bytes(s.replace('\n','\r\n').encode('utf-8'))
