from pathlib import Path
import collections,hashlib,json,shutil,zipfile

BASE=Path(__file__).resolve().parents[1]
CAT=BASE/'outputs/Content-catalogue'
OUT=CAT/'EiF-Uprising'
ROOT=BASE/'work/research/eif-public'
audit=json.loads((OUT/'eif-source-audit.json').read_text())
original=json.loads((CAT/'content-catalogue.json').read_text())
REV=audit['revision']
SOURCE=f'https://gitlab.com/Empire-In-Flames/EiF-Public/-/blob/{REV}/'
REPORT=OUT/'EiF-and-Uprising-research.md'
ACTIVE=CAT/'SWG-active-content-catalogue.md'

bundle_files=[]
for f in audit['inspected_files']:
    p=f['path']
    if ('/scripts/object/creature/player/' in p or p.endswith('/Races.h') or '/managers/player/creation/' in p
        or '/managers/skill/imagedesign/' in p or p.endswith('/COPYING')):
        bundle_files.append(p)
bundle=OUT/'EiF-2017-species-source-reference.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    for p in bundle_files:z.write(ROOT/p,p)
    z.write(OUT/'LGPL-2.1.txt','LGPL-2.1.txt')
    z.writestr('REFERENCE-NOTES.txt',f'''EiF published species source reference
Repository: {audit['repository']}
Revision: {REV} (2017-08-09)
This is a selected source reference, not a complete server or installation bundle.
Keep MMOCoreORB/COPYING and all file-level LGPL/AGPL notices and creator credits.
The full published corresponding source remains available at the pinned repository.
Matching player-template names were found in the original public starsider01.tre.
The client artwork and later private screenplays have separate unresolved reuse terms.
Do not replace modern Core3 managers wholesale with these 2017 files.
No source from Sentinel's Republic is included.
''')
audit['species_reference_bundle']=dict(name=bundle.name,files=len(bundle_files)+2,sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),bytes=bundle.stat().st_size)
archive_out=OUT/'EiF-starsider01-reference.tre'
if not archive_out.exists():shutil.copyfile(BASE/'work/research/eif-starsider01.tre',archive_out)
assert hashlib.sha256(archive_out.read_bytes()).hexdigest()==audit['inspected_client_archive']['sha256']
audit['inspected_client_archive']['retained_copy']=str(archive_out)

sources={
 'eif_public':audit['repository'],
 'eif_license':SOURCE+'MMOCoreORB/COPYING',
 'eif_species_code':SOURCE+'MMOCoreORB/src/server/zone/objects/player/Races.h',
 'eif_patches':'https://gitlab.com/EiF-Public/patch-files',
 'eif_author':'https://modthegalaxy.com/index.php?resources/authors/halyn.3892/',
 'eif_species_release':'https://modthegalaxy.com/index.php?resources/new-species-for-swgemu.36/',
 'eif_datapad':'https://modthegalaxy.com/index.php?resources/halyns-datapad.41/',
 'eif_blades':'https://modthegalaxy.com/index.php?resources/unstable-lightsaber-blades.118/',
 'eif_passengers':'https://modthegalaxy.com/index.php?resources/swgemu-core3-multipassenger.74/',
 'eif_astromechs':'https://modthegalaxy.com/index.php?resources/better-astromechs.35/',
 'eif_newsnet':'https://modthegalaxy.com/index.php?resources/useful-newsnet-terminals.20/',
 'eif_new_species':'https://www.empireinflames.net/?p=1745',
 'eif_species_history':'https://www.empireinflames.net/?cat=22',
 'eif_credits':'https://www.empireinflames.net/?page_id=985',
 'eif_about':'https://www.empireinflames.net/?p=714',
 'eif_guide':'https://www.empireinflames.net/?p=1467',
 'eif_planets':'https://www.empireinflames.com/?m=201809',
 'eif_team_work':'https://www.empireinflames.com/?p=1789',
 'eif_hilts':'https://www.empireinflames.net/?p=1597',
 'eif_harvest':'https://www.empireinflames.net/?p=2261',
 'eif_2026_events':'https://www.empireinflames.net/?p=1542',
 'eif_2022_changes':'https://www.empireinflames.net/?tag=update-notes',
 'eif_contact':'https://www.empireinflames.net/?page_id=220',
 'uprising':'https://swguprising.com/',
 'uprising_features':'https://swguprising.com/#features',
 'uprising_guide':'https://swguprising.com/#whats-different',
 'uprising_credits':'https://swguprising.com/#acknowledgements',
 'uprising_staff':'https://swguprising.com/#staff',
 'uprising_terms':'https://swguprising.com/#terms',
}
def link(key,label='source'):return f'[{label}]({sources[key]})'
def local(path,label):return f'[{label}](<{path.as_posix()}>)'

uprising=[
 dict(name='Resource search and crafting comparisons',summary='In-game materials board with recipe comparisons and survey waypoints.',priority=1),
 dict(name='Crafting and production conveniences',summary='Recipe recovery, larger factory runs, component returns and clear ingredient names.',priority=2),
 dict(name='Housing and vendor conveniences',summary='Furnished-house packing, shared storage, vendor customization and full furniture rotation.',priority=3),
 dict(name='Companions and service support',summary='Harvesting droids, enhanced pet genetics and configurable medical assistants.',priority=4),
 dict(name='Encounters and rewards',summary='Exar Kun, Axkva Min, Decrepit Droid Factory, Lost Star Destroyer and roaming bosses.',priority=5),
 dict(name='Jedi and faction progression',summary='Grey Jedi and Ronin faction development alongside Light/Dark progression.',priority=6),
]
eif_unreleased=[
 ('Arkanian and Echani','Later playable species, announced March 2022; not in the collected 2017 server snapshot.','eif_new_species'),
 ('IG-100 and female Devaronian','Later player options; female Devaronian client template is in starsider01, but absent from the inspected server race header. IG-100 is distinct from its NK3 droid.','eif_species_history'),
 ('Sith Shrine, Plasma Mining Facility and EiF Axkva Min','Documented encounters; matching complete server implementation not found in the public snapshot.','eif_guide'),
 ('Pazaak, click collections and seasonal reward systems','Documented content; complete reusable implementation not established.','eif_guide'),
 ('Holocomm, Kyber systems, configurable weapons and custom animations','Contributor work identified; no complete standalone release verified.','eif_team_work'),
 ('Kuat Drive Yards, Dac City and related planet revisions','Contributions span EiF and Sunrunner. Obtain the exact package and relevant creators’ terms.','eif_credits'),
 ('Taanab Harvest and modern Empire Day missions','Current event descriptions and reward paths exist; they are separate from the original public Taanab terrain release.','eif_harvest'),
 ('Airspeeder/jetpack backend and surveillance tools','Later systems documented in 2022; the 2021 passenger demonstration does not supply this whole backend.','eif_2022_changes'),
 ('Custom lightsaber hilts, BB droids and starship art','Different authors and third-party licenses apply. Model rights and EiF conversion rights must be traced separately.','eif_hilts'),
]

rows=[]
for old in original['rows']:
    if old['kind'] in ['SR gameplay','Excluded file','Species']:continue
    row=dict(old)
    row['sources']=[s for s in row['sources'] if 'swgsremu' not in s and 'sentinelsrepublic' not in s.lower()]
    if row['kind']=='Planet' and row['status']=='P':
        clean_notes={
          'Taanab':'Original Takhomasak mini-expansion and MTG terrain/snapshot. Use the original release; write any missing encounters ourselves.',
          'Dromund Kaas':'Original Levarrishawk release and published Stardust source. Later independent revisions require separate provenance.',
          'Mandalore':'Bats original release includes terrain, world Lua, NPCs and caves. MTG terrain/snapshot present; later revisions are separate.',
          'Jakku':'MTG terrain/snapshot and public Stardust battle/Weapons Facility scripts. Precise artwork provenance still needs review.'}
        if row['name'] in clean_notes:row['notes']=clean_notes[row['name']]
        if row['name']=='Dromund Kaas':row['origin']='Levarrishawk original public release'
    if row['name']=='Tansarii Point Station':
        row['origin']='SOE station assets; independent community implementations'
        row['notes']='Station assets do not supply a complete travel, vendor or quest implementation. Build missing gameplay ourselves.'
    if row['kind']=='Restricted or unverified family' and row['name'].startswith('EiF'):
        row['notes']='EiF public server source and client patch repository have now been located. Custom ship art still has individual author/license conditions; see the new report.'
    rows.append(row)

original_public={r['name'] for r in original['rows'] if r['kind']=='Species' and r['status']=='P'}
for species in audit['species']:
    public=species['name'] in original_public
    rows.append(dict(kind='Species',name=species['name'],status='P' if public else 'S',
      status_label='Published for server use' if public else 'Published server code; client asset reuse unresolved',origin='Halyn / Empire in Flames public source snapshot',
      availability='Player Lua, race header and matching public starsider01 template located; not installed',
      notes='2017 reference only; client selection, equipment, appearance dependencies and modern Core3 compatibility remain untested. '+('Original MTG species package is also collected.' if public else 'Client art terms need a specific release statement or author agreement before importing that contribution.'),
      sources=[species['source'],SOURCE+'MMOCoreORB/bin/scripts/object/creature/player/serverobjects.lua'],runtime_validated=False,
      components=dict(server_code='AGPL repository / LGPL player Lua headers',client_assets='Creator species release' if public else 'Reuse not established by player-patch availability'),
      model_evidence=species['models']))
for name in ['Arkanian','Echani','IG-100 Droid']:
    rows.append(dict(kind='Species',name=name,status='U',status_label='Later EiF implementation; reusable complete package unverified',origin='Empire in Flames',
      availability='Officially documented player option; not in the inspected 2017 species set',notes='Do not substitute the NK3 droid implementation for IG-100. Seek exact source/client package and terms.',
      sources=[sources['eif_new_species'] if name!='IG-100 Droid' else 'https://www.empireinflames.net/?p=282'],runtime_validated=False))
for name,key,notes in [
 ("Halyn's Development Datapad",'eif_datapad','Two-file public developer tool; no new client assets. Replace sample calls to missing EiF heroics and restrict controls to authorized staff.'),
 ('Unstable Lightsaber Blades','eif_blades','Halyn shaders and Auri textures. Public use with credit requested. Cosmetic blade overrides; selectively package after testing.'),
 ('EiF public server source snapshot','eif_public','August 2017 AGPL compliance release. Useful selected source; private custom screenplays and modern content are not present.')]:
    rows.append(dict(kind='Pack or tool',name=name,status='P',status_label='Published for identified purpose',origin='Halyn / Empire in Flames',
      availability='Collected reference files; not installed',notes=notes,sources=[sources[key]],runtime_validated=False))
for feature in uprising:
    rows.append(dict(kind='Design reference',name='Uprising: '+feature['name'],status='U',status_label='Reference only; no official reuse release found',origin='SWG Uprising',
      availability='Documented behavior; no official source/assets collected',notes=feature['summary']+' Candidate for our own implementation.',sources=[sources['uprising_guide']],runtime_validated=False))
for i,row in enumerate(rows,1):row['id']=f'active-{i:03}'
active=dict(researched='2026-10-13',scope='Active content research; Sentinel’s Republic excluded by user instruction. Preserve historical research separately. LAN first; public deployment requires a separate rights/dependency review.',
            counts=dict(entries=len(rows),ground_worlds=sum(r['kind']=='Planet' for r in rows),stations=sum(r['kind']=='Station' for r in rows),additional_species_candidates=sum(r['kind']=='Species' for r in rows)),
            rows=rows,deep_report=str(REPORT),server_changes=False)
(CAT/'active-content-catalogue.json').write_text(json.dumps(active,indent=2),encoding='utf-8')
lines=['# Active SWG content catalogue','',
 'Updated 13 October 2026. Sentinel’s Republic has been removed from the active research/import plan at the user’s request. Historical records remain available.', '',
 f"This catalogue contains {len(rows)} research entries, including 18 ground worlds, 3 stations and 40 additional species/character candidates. The species count includes 37 legacy EiF source definitions and three later options; it is not a claim of 40 installed or currently selectable additions.", '',
 local(REPORT,'Read the EiF and Uprising findings'), '',
 'P: published for the identified purpose; S: published server code with unresolved client-art terms; U: unresolved release/permission or design reference; A: creator permission required; C: explicit conditions; D: development/legacy data. None of the new entries is runtime-tested.', '',
 '| Content | Category | Decision | Availability / limitation | Sources |','|---|---|---|---|---|']
for row in rows:
    refs=', '.join(f'[source {i+1}]({s})' for i,s in enumerate(row['sources']))
    notes=(row['availability']+'. '+row['notes']).replace('|','/').replace('\n',' ')
    lines.append(f"| {row['name']} | {row['kind']} | {row['status']} | {notes} | {refs} |")
ACTIVE.write_text('\n'.join(lines)+'\n',encoding='utf-8')

lines=['# EiF and Uprising: LAN content research','', 'Researched 13 October 2026. No server or working-client changes made.', '',
 '## Decisions for this project','',
 '- Sentinel’s Republic is excluded from the active content plan. Missing encounters and quests can be written for our own setting.',
 '- The immediate target is a private LAN game. A later public launch is a separate decision; record creator permissions, licenses and any agreed payment against each contribution.',
 '- Published code, downloadable player patches, complete content and permission to redistribute artwork are different findings.', '',
 '## The significant EiF discovery','',
 f"The official {link('eif_public','EiF public server repository')} contains an **August 9, 2017** snapshot at `{REV}`. Its root COPYING is AGPLv3, and the player Lua files retain LGPL-2-or-later headers. The selected source is available under those notices; preserve credits and applicable corresponding-source requirements. No separate purchase requirement was found for the published code.", '',
 '**The race header has 66 gender entries representing 47 species/character options: 10 original options plus 37 additions.** Player Lua registration and shared-template declarations were checked. This is source evidence, not a statement that all 47 were enabled in character creation or are playable on today’s EiF.', '',
 'The public client patch repository also exists. Its pinned manifest lists 23 TRE archives totaling 4,333,368,394 bytes, dated October 19, 2025. One original archive, starsider01.tre, was downloaded into the separate research collection. Its size and MD5 match the published manifest, and its index contains matching player templates for all 37 legacy additions. Sixteen of those additions already have matching MTG player templates. No client patch was installed.', '',
 'This resolves the earlier uncertainty about whether the additional species files exist. It does **not** establish a blanket artwork license for the entire EiF player patch. Its README has only the project title and no general asset reuse grant. Client-selection data and full appearance/equipment dependencies still require review.', '',
 'The same server snapshot loads `bin/custom_scripts/screenplays/screenplays.lua`, but the public tree contains only a .gitignore under custom_scripts. Modern heroics and event scripts cannot be recovered merely by downloading its published server tree.', '',
 '## All 37 legacy additions with source evidence','',
 '| Species / character option | Server genders | Already in MTG | EiF matching player template |','|---|---|---|---|']
for row in audit['species']:
    genders=', '.join(m['gender'] for m in row['models'])
    mtg='Yes' if all(m['local_mtg_archives'] for m in row['models']) else 'No matching player template found'
    lines.append(f"| {row['name']} | {genders} | {mtg} | Found in starsider01 |")
lines+=['',f"The authoritative list is the {link('eif_species_code','pinned race header')}, paired with its player Lua files. Nightsister and Singing Mountain Clan are character options rather than separate biological species. The droid template refers to `appearance/nk3.sat`; it is not proof of the later IG-100 player implementation.", '',
 '## Later species and variations','',
 f"**Arkanian and Echani** were introduced in {link('eif_new_species','March 2022 patch notes')}; their complete reusable packages are not in this 2017 snapshot. **IG-100** and **female Devaronian** appear in the {link('eif_species_history','August 2017 client-release history')}. Female Devaronian’s player template is in the inspected client archive, but the old server header includes only male Devaronian. These distinctions prevent treating every modern option as covered by the old code.", '',
 '## Explicit public EiF releases worth using','',
 '| Contribution | Evidence / practical use |','|---|---|',
 f"| Original species mod | {link('eif_species_release','Creator release')}; original ZIP collected earlier, with 16 additions including Togruta. Modern port needed. |",
 f"| Multipassenger vehicles | {link('eif_passengers','Creator release')}; public AGPL source and matching TRE collected. Flash-speeder example; not the complete modern vehicle catalog. |",
 f"| Better Astromechs | {link('eif_astromechs','Creator release')}; NPC paint customization with EiF credit requested. Original ZIP collected earlier. |",
 f"| Useful Newsnet Terminals | {link('eif_newsnet','Creator release')}; informational terminal scripts. Replace EiF endpoints with local project information; original ZIP collected earlier. |",
 f"| Development Datapad | {link('eif_datapad','Creator release')}; newly collected two-file tool. Uses an existing client appearance. Sample menu calls EiF-specific heroic methods that we must replace; staff checks should be added when adapted. |",
 f"| Unstable saber effects | {link('eif_blades','Halyn and Auri release')}; newly collected 54-file ZIP. Creator explicitly offers use with credit. Selective cosmetic integration and testing needed. |", '',
 'Abi’s Lamp Pack and the already collected Borrie packs retain their individual public release terms; association with a private server does not undo their separate creator releases.', '',
 '## Other EiF content and missing material','',
 '| Content / family | Finding | Source |','|---|---|---|']
for name,notes,key in eif_unreleased:lines.append(f'| {name} | {notes} | {link(key)} |')
lines+=['',
 f"EiF’s {link('eif_planets','2018 planet release notes')} document Chandrila, Coruscant, Kuat and Mon Calamari; the credits distinguish Levarris’s Coruscant/Chandrila work from Sunrunner contributions. Taanab has its own original public creator release. A server partnership is evidence of collaboration, not a transferable blanket grant to all partner assets.", '',
 f"Its {link('eif_credits','credits')} identify separate artwork authors: AgentOrangeJuice (including V-wing), MTD/X-Wing Alliance Upgrade (YT-2000 and MC80 Liberty), Admiral Tributon (HWK-290 and Clone Wars Y-wing), and BB-unit model authors/converters. The BB-9E original is linked to CC-BY 4.0; the exact EiF conversion still needs its own provenance. No price list or blanket LAN-use exception was found in the inspected official materials.", '',
 f"EiF’s {link('eif_about','profession design')} deliberately changes the original profession structure and crafting. Our pre-CU project can select content without adopting that entire overhaul. An old guide’s statement that JtL is unavailable is outdated: EiF’s {link('eif_2026_events','2026 Empire Day description')} includes a space escort activity.", '',
 '## Uprising findings','',
 f"Uprising identifies Core3 as its base in the {link('uprising_credits','acknowledgements')}. Its {link('uprising_staff','staff page')} names Idewu for engineering and Avix for project direction. The official website advertised an October 2, 2026 launch and the browser showed recent October updates during this audit; no operational test was performed.", '',
 f"The {link('uprising_guide','feature guide')} advertised **311 entries across 18 categories**. These are documented behaviors, not 311 separately licensed original mods. Useful candidates for our project are:", '',
 '| Priority | Reference |','|---:|---|']
for r in uprising:lines.append(f"| {r['priority']} | {r['summary']} |")
lines+=['',
 f"The {link('uprising_features','overview')} also describes three-faction planetary conflict and expanded pre-CU encounters. No official Uprising server-source repository or reusable content package was found in the official links and public repository searches checked. Two third-party client helpers surfaced on GitHub, but neither is the server implementation. No new-planet or species release package was identified. Its {link('uprising_terms','terms page')} was a placeholder during the audit and supplies no content reuse grant.", '',
 'For Uprising, use the documented behavior to write our own systems unless its authors release the relevant source or grant specific permission. The resource/crafting board is the strongest first design reference for this LAN sandbox.', '',
 '## LAN use, public use and payment','',
 'For published EiF code, follow the included licenses; LAN-only access does not replace their conditions. Keep corresponding source available to users as required by the applicable license. For client art whose terms are unresolved, ask for the specific LAN permission now, and a separate public redistribution/hosting permission if the project later opens to the public.', '',
 'The willingness to pay can be recorded as an offer for an agreed license, porting work or support. It does not establish that payment is required, that an author will sell a license, or that one team can license another contributor’s artwork. Agree on named files, permitted changes, credits, redistribution, scope and any fee before relying on a custom agreement.', '',
 f"Start with Halyn/the EiF team through their {link('eif_contact','official contact page')}; ask them to route any third-party art questions. Uprising’s {link('uprising_staff','staff page')} and official Discord identify the engineering/project contacts. **No messages were sent, terms accepted or payments arranged.**", '',
 'Useful questions for the creators:', '',
 '1. Which of the named species packages and client templates may be reused on a private, noncommercial LAN, and which require separate original-artist permission?',
 '2. Is there a newer public species patch or source release compatible with current Core3, including Arkanian, Echani, IG-100 and female Devaronian?',
 '3. Are any selected encounter, vehicle, housing or utility systems offered as standalone releases? Which exact source revision and asset dependencies belong together?',
 '4. What additional terms, attribution and fees, if any, would apply to a later public free-to-play server and redistribution of its custom patch?', '',
 '## Retained files and validation','',
 local(bundle,'Selected EiF species source reference')+' — source and licenses only; not a complete install bundle.', '',
 local(OUT/'halyns_datapad.zip',"Halyn’s Development Datapad")+'; '+local(OUT/'unstable_lightsaber_blade.zip','Unstable saber effects')+'.', '',
 local(archive_out,'Original starsider01 research copy')+' — public player-patch download retained for inspection; no blanket reuse grant established.', '',
 local(OUT/'eif-source-audit.json','File-level source/package evidence')+'; '+local(OUT/'EiF-starsider01-index.json','Client archive index and creation-table evidence')+'; '+local(ACTIVE,'Updated active catalogue')+'.', '',
 'Validation: 1,100 selected source files inspected for notices; no proprietary/not-for-distribution marker found in that inspected subset. The selected source ZIP and both new creator ZIPs passed archive-integrity checks. All 37 source options have registered player Lua and matching shared-template names in the inspected EiF archive. These checks do not validate appearance dependencies, character selection, gameplay or modern Core3 behavior.', '',
 'The bulk remote range-index attempt was unsuccessful; no conclusions rely on it. The successful local starsider01 index is the asset evidence used above. The other 22 required archives were not downloaded or inventoried.', '',
 '## Recommended next work','',
 '1. Adapt the public development datapad into an owner-only tool for our own screenplays.',
 '2. Port the original public species package first; use the broader EiF source as a reference and resolve the remaining client-art terms.',
 '3. Build our own resource/recipe board and missing quests using current Core3 and assets already covered by creator releases.',
 '4. Evaluate public multipassenger support separately from later private vehicles, and test each cosmetic pack in a copied client before deployment.', '',
 'Nothing in this report authorizes or performs an installation, public launch, external message or payment.', '']
REPORT.write_text('\n'.join(lines),encoding='utf-8')
audit['sources']=sources
audit['newer_options_unverified']=['Arkanian','Echani','IG-100 Droid','Female Devaronian implementation']
audit['uprising']=dict(references=uprising,official_source_release_found=False,source_search_scope='Official website links, acknowledgements and staff pages; public GitHub repository searches for SWG Uprising and Idewu',
                      reuse='Documented behavior only; independent implementation or specific creator release required',sources=[sources[k] for k in ['uprising_features','uprising_guide','uprising_credits','uprising_staff','uprising_terms']])
(OUT/'eif-source-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(dict(active_counts=active['counts'],selected_source_files=len(bundle_files),report=str(REPORT),source_bundle=audit['species_reference_bundle']),indent=2))
