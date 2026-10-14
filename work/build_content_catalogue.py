from pathlib import Path
import collections, hashlib, json, re, urllib.parse

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'outputs/Content-catalogue'
mtg=json.loads((OUT/'MTG-file-inventory.json').read_text(encoding='utf-8'))
assets={x['path']:x['archives'] for x in mtg['relevant_assets']}
S={
 'mtg':'https://github.com/ModTheGalaxy/mtgserver/wiki',
 'mtg_assets':'https://github.com/ModTheGalaxy/DevEnv',
 'sr':'https://swgsremu.com/features/main-features/',
 'sr_locations':'https://swgsremu.com/features/new-locations/',
 'sr_changes':'https://forum.swgsremu.com/viewtopic.php?t=2746',
 'sr_taanab':'https://forum.swgsremu.com/viewtopic.php?t=2036',
 'sr_acklay':'https://forum.swgsremu.com/viewtopic.php?t=2078',
 'stardust':'https://github.com/Levarrishawk/Stardust',
 'darklight':'https://github.com/Levarrishawk/DLSWG5',
 'hondo':'https://github.com/Tatwi/legend-of-hondo',
 'sunrunner':'https://swgsunrunner2.com/about/',
 'sunrunner_content':'https://swgsunrunner2.com/full-change-list/',
 'sunrunner_species':'https://swgsunrunner2.com/species/',
 'eif_credits':'https://www.empireinflames.net/?page_id=985',
 'eif_species':'https://www.empireinflames.net/?p=282',
 'species':'https://modthegalaxy.com/index.php?resources/new-species-for-swgemu.36/',
 'species_original':'https://modthegalaxy.com/index.php?threads/new-species-for-swgemu-core3-beta-0-5.629/',
 'taanab':'https://modthegalaxy.com/index.php?threads/new-planet-taanab-mini-expansion.686/',
 'hoth':'https://modthegalaxy.com/index.php?threads/new-planet-hoth.756/',
 'mandalore':'https://modthegalaxy.com/index.php?threads/mandalore-for-swgemu-based-emulators.433/',
 'kaas':'https://modthegalaxy.com/index.php?threads/dromund-kaas-for-swgemu-based-emulators.349/',
 'zeltros':'https://modthegalaxy.com/index.php?resources/zeltros-planet.135/',
 'kashyyyk':'https://modthegalaxy.com/index.php?resources/kashyyyk-for-precu.2/',
 'mustafar':'https://modthegalaxy.com/index.php?resources/mustafar-for-precu.3/',
 'passengers':'https://modthegalaxy.com/index.php?resources/swgemu-core3-multipassenger.74/',
 'passengers_code':'https://gitlab.com/Empire-In-Flames/swgemu-multipassenger',
 'infinity':'https://github.com/swginfinity/public',
 'infinity_worlds':'https://www.swginfinity.com/guides/adventure-guides',
 'newbeginnings':'https://www.swgnb.com/swg/',
}
STATUS={
 'P':'Published for server use',
 'C':'Published with explicit conditions',
 'A':'Original creator permission required',
 'U':'Release or permission unverified',
 'X':'Conflicting restrictive notice: exclude',
 'D':'Development or legacy data only',
}
rows=[]
def add(kind,name,status,origin,availability,notes,sources,**extra):
    rows.append(dict(id=f'{kind.lower()}-{len(rows)+1:03}',kind=kind,name=name,status=status,
        status_label=STATUS[status],origin=origin,availability=availability,notes=notes,
        sources=[S.get(s,s) for s in sources],runtime_validated=False,**extra))

worlds=[
 ('Taanab','taanab','Takhomasak; restoration of unfinished SOE terrain','P','Original mini-expansion was released for server administrators. MTG terrain and snapshot are present. SR later quests are separate.',['taanab','mtg','sr_taanab']),
 ('Hoth','hoth','Takhomasak original public work; other server-specific variants','P','MTG terrain and snapshot present; original creator release located. Current Sunrunner and Infinity encounters are separate versions, not covered by this row.',['hoth','mtg','infinity_worlds']),
 ('Dromund Kaas','kaas','Levarrishawk original release; later SR terrain work credited to Tiny','P','Original standalone release plus public Stardust scripts. Later SR Prophet and Terentatek logic is not established by the old release.',['kaas','stardust','sr_locations']),
 ('Mandalore','mandalore','Bats (Ken Austin) original release; later independent revisions','P','Original release includes terrain, world Lua, NPCs and caves. MTG terrain/snapshot present; later SR and Sunrunner revisions require separate provenance.',['mandalore','mtg','sr_taanab']),
 ('Chandrila','chandrila','Levarrishawk/Stardust; acknowledged by EiF','P','MTG terrain/snapshot and public Stardust city/POI scripts present. Elysium release described its own version as complete in 2017; this is historical, not a local test.',['stardust','darklight','eif_credits']),
 ('Coruscant','coruscant','Levarrishawk/Stardust; acknowledged by EiF','P','MTG terrain/snapshot and public district/race scripts. The Elysium version was a sparse roleplay world. Sunrunner separately credits original third-party 3D art.',['stardust','darklight','eif_credits','sunrunner']),
 ('Jakku','jakku','Public Stardust implementation; precise asset authorship still to trace','P','MTG terrain/snapshot and published Jakku battle/Weapons Facility scripts. Do not equate this with every later SR encounter.',['stardust','sr_locations','mtg']),
 ('Moraband / Korriban','moraband','Levarrishawk/Darklight/Stardust','P','MTG terrain/snapshot and public Valley of the Dark Lords script. The 2017 author release called the world partial. These aliases count as one world.',['darklight','stardust','sr_locations']),
 ('Nal Hutta','hutta','Levarrishawk/Darklight public version; Sunrunner later original work','P','MTG terrain/snapshot. Elysium called its version partial with no server scripting. Current Sunrunner Nal Hutta content is a separate permission case.',['darklight','mtg','sunrunner']),
 ('Kashyyyk','kashyyyk','SOE expansion assets; community pre-CU adaptation','P','MTG full-world and segmented terrain exist. Sytner release directs users to MTG improvements. No complete expansion campaign has been verified for our installation.',['kashyyyk','mtg','infinity_worlds']),
 ('Mustafar','mustafar','SOE expansion assets; community pre-CU adaptation','P','MTG terrain/snapshot, NPC definitions and some public Stardust quest/region scripts. Not a verified complete Trials of Obi-Wan campaign.',['mustafar','mtg','stardust']),
]
for name,key,origin,status,notes,sources in worlds:
    evidence=[]
    for path in [f'terrain/{key}.trn',f'snapshot/{key}.ws']:
        if path in assets:evidence.append(dict(path=path,archives=assets[path]))
    add('Planet',name,status,origin,'Collected MTG assets; additional published source or original release links',notes,sources,zone=key,local_asset_evidence=evidence)
for name,key in [('Dagobah','dagobah'),('Mon Calamari / Dac','moncalamari'),('Kuat','kuat'),('Ord Mantell','ordmantell'),('Bespin','bespin'),('Kessel','kessel')]:
    add('Planet',name,'A','Sunrunner II team / individually credited contributors','Advertised on official server; no reusable full world release verified',
        'Modern Sunrunner version: see the common project permission statement below. Full reusable world package not verified.',
        ['sunrunner','sunrunner_content'],zone=key,local_asset_evidence=[])
add('Planet','Zeltros','C','tienvogh','Client and server ZIPs downloaded and inspected; hashes recorded',
    'Explicit resource-page CC-BY-NC statement: noncommercial use/modification with author credit. ZIPs contain no separate license-version text. Exploration world with no NPCs/combat initially. Includes terrain, snapshot, custom buildings and region/travel Lua. Old plural objects paths need adapting to our Core3 layout; requires MTG assets.',
    ['zeltros'],zone='zeltros',local_asset_evidence=[])
add('Station','Tansarii Point Station','U','SOE station assets; SR and Sunrunner station systems differ','MTG station object candidates and published server descriptions',
    'Station building assets and bespoke travel agents, vendors, quests and newbie encounters are separate. Full SR station gameplay package not verified.',
    ['sr_locations','sunrunner_content','mtg'])
for name in ['Nova Orion Station','Centerpoint Station']:
    add('Station',name,'A','Sunrunner II implementation','Official server description only',
        'Full station layout, travel network and original gameplay package not verified as a reusable release. Seek the relevant creator release or permission.',
        ['sunrunner','sunrunner_content'])
add('Candidate world','Otoh Gunga','D','Legacy SOE terrain; New Beginnings separate development effort','terrain/otoh_gunga.trn found in MTG archives',
    'Legacy terrain is not a finished underwater destination. New Beginnings advertises a separate version in development; no reusable release verified.',['newbeginnings','mtg'])
add('Candidate world','Geonosis','D','Bats announced an intention to build it','Mentioned as a future project in original Mandalore thread',
    'No completed public planet release verified. Do not confuse Yavin IV Geonosian Bio-Lab with a Geonosis planet.',['mandalore'])
add('Legacy/test world','Umbra and developer terrains','D','SOE development/test data','MTG archive index names recorded in MTG-inventory-summary.json',
    'Includes Umbra, numeric 09/10/11, dungeon1/2, character_farm, creature_test and other test terrains. Not counted among the 18 content worlds.', ['mtg'])

species=[('Aqualish','aqualish',['male','female']),('Bith','bith',['male','female']),('Chiss','chiss',['male','female']),
 ('Devaronian','devaronian',['male']),('Gotal','gotal',['male']),('Gran','gran',['male']),('Hutt','hutt',['male','female']),
 ('Ishi Tib','ishi_tib',['male']),('Nautolan','nautolan',['male']),('Nightsister','nightsister',['female']),('Nikto','nikto',['male']),
 ('Quarren','quarren',['male']),('Singing Mountain Clan Witch','smc',['female']),('Talz','talz',['male']),('Weequay','weequay',['male'])]
for name,key,genders in species:
    evidence=[dict(path=f'object/creature/player/shared_{key}_{g}.iff',archives=assets.get(f'object/creature/player/shared_{key}_{g}.iff',[])) for g in genders]
    add('Species',name,'P','Halyn, with Phoenix; creator-released species package','Player shared assets found in MTG; original server/client ZIP collected',
        'Shared 2016 species package.',
        ['species','species_original','mtg'],genders=genders,local_asset_evidence=evidence)
add('Species','Togruta','P','Halyn MTG species resource actual ZIP; MTG compilation','Female player Lua and Races.h entry verified inside downloaded newspecies.zip; assets also in MTG patch 023',
    'Release page list omits Togruta, but the actual download includes its player Lua and C++ race entries. Package/page mismatch recorded. Modern Core3 port and tests still required.',
    ['species','mtg','eif_species'],genders=['female'],local_asset_evidence=[dict(path='object/creature/player/shared_togruta_female.iff',archives=assets.get('object/creature/player/shared_togruta_female.iff',[]))])
for name in ['Abyssin','Arcona','Cerean','Duros','Feeorin','Gungan','IG-100 Droid','Iktotchi','Kel Dor','Kubaz','Mirialan','Sanyassan','Zeltron']:
    add('Species',name,'U','Empire in Flames implementation','Listed by EiF; complete reusable species package not verified',
        'Availability on EiF is evidence of implementation, not a reuse grant. Some underlying NPC models exist in game data; a complete player species requires additional code, data and any custom artwork permission.',
        ['eif_species','eif_credits'])

packs=[
 ("Borrie's Torch Pack",'P','Borrie BoBaka','https://modthegalaxy.com/index.php?resources/borries-torch-pack.96/','Explicit server TRE redistribution statement; credit appreciated. No acquisition schematics supplied.'),
 ("Borrie's Kitchen Pack",'P','Borrie BoBaka / Dark Rebellion RP','https://modthegalaxy.com/index.php?resources/borries-kitchen-pack.106/','Explicit server TRE redistribution statement; credit appreciated. Crafters/vendor acquisition must be added.'),
 ("Borrie's Dark Interiors",'P','Borrie BoBaka','https://modthegalaxy.com/index.php?resources/borries-dark-interiors.100/','Explicit distributed-server-file use statement. Release 0.5 identifies roughly 13 crashing structures; exclude those until repaired.'),
 ("Borrie's Naboo Structure Pack",'P','Borrie BoBaka','https://modthegalaxy.com/index.php?resources/borries-naboo-structure-pack.98/','Explicit server TRE distribution statement; credit appreciated. Deeds, schematics and placement acquisition not included.'),
 ("Borrie's Light Megapack",'P','Borrie BoBaka / Dark Rebellion RP','https://modthegalaxy.com/index.php?resources/borries-light-megapack.113/','Published specifically for server/world-builder use; downloaded README confirms integration and credits. No separate redistribution clause found: clarify that before rehosting a bundled public client. 11,928 files; not 11,928 finished items.'),
 ("Borrie's Wall Pack Vol. 1",'P','Borrie BoBaka','https://modthegalaxy.com/index.php?resources/borries-wall-pack-vol-1.12/','Downloaded README expressly allows repacking into a server TRE for players. Credit appreciated. Client/server asset files included.'),
 ("Abi's Lamp Pack",'P','Abi','https://modthegalaxy.com/index.php?resources/abis-lamp-pack.99/','Downloaded source files explicitly offer the work through MTG with Abi credited on the server website. Includes schematic and tangible definitions; retain notices.'),
 ('SWGEmu Core3 Multipassenger','P','Halyn / Empire in Flames',S['passengers'],'Explicit public code/assets release, AGPLv3 source, credit EiF. Matching passenger TRE downloaded. Demonstrates Flash speeder passengers; not a release of every EiF custom vehicle.'),
 ('Useful Newsnet Terminals','P','Halyn / Empire in Flames','https://modthegalaxy.com/index.php?resources/useful-newsnet-terminals.20/','Creator explicitly releases the script for other servers. Original two-file ZIP inspected. Requires lua-socket and replacing EiF website URLs with our own information source; retain its source notices.'),
 ('Better Astromechs','P','Halyn / Empire in Flames','https://modthegalaxy.com/index.php?resources/better-astromechs.35/','Explicit server-use offer with EiF credit requested. Changes NPC astromech base/trim colors; not a new playable droid species.'),
 ("Borrie's Wearable Rank Plates",'P','Borrie BoBaka','https://modthegalaxy.com/index.php?resources/borries-wearable-rank-plates.55/','Explicit permission to repack in server TREs; credit appreciated. Gender appearance-table changes required; no player acquisition route supplied.'),
 ('Named Saber Crystals','U','Original MTG thread author to verify','https://modthegalaxy.com/index.php?threads/named-saber-crystals.419/','Public release thread identified; individual files and terms not inspected.'),
 ('Classic BARC Assets','U','Original MTG thread author to verify','https://modthegalaxy.com/index.php?threads/classic-barc-speeder-assets-patch.238/','Public release thread identified; check whether already covered by MTG, and preserve asset provenance.'),
 ('Post-14.1 House Assets','U','Original MTG thread author to verify','https://modthegalaxy.com/index.php?threads/post-14-1-house-assets-patch.237/','Historical release identified; MTG also supplies many house definitions. Full placement/crafting still needs testing.'),
 ("Borrie's /tool and Jawa object syncing",'U','Borrie BoBaka','https://modthegalaxy.com/index.php?threads/borries-tool-command-featuring-the-jawa-toolbox-object-syncing-command.1395/','Public development tool thread identified; file-level license and current Core3 port not checked.'),
 ('Sytner IFF Editor (SIE)','U','Sytner','https://modthegalaxy.com/index.php?resources/sie.1/','Official tool release located. Check distribution terms before bundling the tool; no tool installed during this audit.'),
 ('SWG Galaxy Map Editor','U','digedaduku','https://modthegalaxy.com/index.php?resources/swg-galaxy-map-editor.173/','2026 map/UI editor. Full resource content explicitly requires a Mod the Galaxy login; download and license not inspected.'),
 ('SWG Forge','P','wickedhangover / monkjames','https://github.com/monkjames/SWG-Forge','Public GPL-2.0 source for VS Code IFF/STF/TRE/CRC/texture editors, terrain viewer, crafting and mount tools. Preserve its license; build/runtime quality not tested. No extension installed.'),
]
downloaded_pack_names={"Borrie's Torch Pack","Borrie's Kitchen Pack","Borrie's Naboo Structure Pack","Borrie's Light Megapack","Borrie's Wall Pack Vol. 1","Abi's Lamp Pack",'SWGEmu Core3 Multipassenger','Useful Newsnet Terminals','Better Astromechs',"Borrie's Wearable Rank Plates"}
for name,status,author,url,notes in packs:
    add('Pack or tool',name,status,author,'ZIP downloaded and inspected; not installed' if name in downloaded_pack_names else 'Published resource or release thread located; not installed by this audit',notes,[url]+(['passengers_code'] if name=='SWGEmu Core3 Multipassenger' else []))
add('Tool','SWG Mobile Template Viewer','P','[name removed] / [name removed]','Public source and hosted viewer',
    'Creator identifies authorship and asks for credit for modifications; repository carries an informal named license. Useful NPC reference, not a playable species package.',
    ['https://github.com/[name removed]/swgmtv'])

for kind,category in [('Housing','object/building'),('Schematics','object/draft_schematic'),('Inventory items / decor / armor / vehicles','object/tangible'),('Weapons','object/weapon'),('NPC and creature objects','object/mobile'),('Ships','object/ship')]:
    count=mtg['category_counts'].get(category,0)
    add('MTG family',kind,'P','MTG contributors; many restored SOE assets',f'{count:,} published Lua definition files in collected bundle',
        'Published definitions: common MTG terms apply. See the per-file inventory; acquisition and runtime behavior require testing.', ['mtg'])
add('Quest example','The Beginning','P','MTG tutorial contributor; retain original release credits','Published Lua plus locally adapted example already installed',
    'Han/Chewbacca introductory quest framework. Other duplicate formatted and blank tutorial files are references, not additional finished quests.', ['mtg'])

for name in ['Hydro Station','Taanab System Excavations Cave','Downed Ship / Voler Navire','Norulac Freebooter Cave','Senate Theme Park Part II','Acklay Cavedweller solo instance','Droideka Quest','SEA Removal Tool Quest','Duplicator Prototype / data-disk collections','Secrets of Dromund Kaas / Force-sensitive skill removal','Ancient Terentatek world event','Tansarii crafting courier and exploration quick travel','Corellian Droid Facility']:
    add('SR gameplay',name,'U','SR team and individually credited contributors','Advertised content; complete reusable implementation not found in either inspected SR public tree',
        'Obtain an author-released package or written permission for the specific implementation. Original public planet content with a similar name does not establish permission for later SR scripts.',
        ['sr_taanab','sr_acklay','sr_changes','sr_locations'] if name!='Corellian Droid Facility' else ['https://swgsremu.com/'])
for name in ['Sunrunner original Lua quests / encounters','Sunrunner original artwork / planet revisions','EiF custom ship models and converted third-party artwork']:
    add('Restricted or unverified family',name,'A' if name.startswith('Sunrunner') else 'U','Relevant original creators',
        'Server feature descriptions and credits; full reuse grant not verified',
        ('Original Lua is held in private repositories; no full creator release verified.' if name=='Sunrunner original Lua quests / encounters' else
         'Original artwork requires creator permission and credit under the published project policy.' if name.startswith('Sunrunner') else
         'Credits identify original and separately licensed third-party artwork. Check the license for each model and conversion; no blanket reuse grant established.'),
        ['sunrunner'] if name.startswith('Sunrunner') else ['eif_credits'])
for name in ['autoEntertain.lua','autoGroupInvite.lua']:
    add('Excluded file',name,'X','Wasted Potential Studios notice in newer SR public checkout','File exists in research checkout; excluded from reusable reference ZIP',
        'Header says proprietary and not for distribution. Conflicts with treating the entire fork as a blanket reusable package; obtain author clarification before copying this contribution.',
        [f'https://github.com/swgsremu/sentinelsrepublic-server/blob/5df918b48f9fe011e93738c539311778906e189f/MMOCoreORB/bin/scripts/commands/{name}'])

repos=[
 ('stardust','Levarrishawk/Stardust','8acad60560c9048ce10846389acfcb9a775fb9ba','2019-08-16'),
 ('darklight','Levarrishawk/DLSWG5','4d7faa864ecf176671eb16880d5d7689c7634658','2017-03-02'),
 ('legend-of-hondo','Tatwi/legend-of-hondo','41d09df6c342b8bd656f81de5cf1c8211a648c2b','2021-03-10'),
 ('eif-multipassenger','Empire-In-Flames/swgemu-multipassenger','4dadcd651d4dbe0992641df2aa7b19ebbaba660a','2021-07-24'),
]
baseline=set((BASE/'work/research/current-core3-tree.txt').read_text(encoding='utf-8-sig').splitlines())
source_inventory=[]
for folder,repo,rev,date in repos:
    tree=(BASE/f'work/research/{folder}-tree.txt').read_text(encoding='utf-8-sig').splitlines()
    paths=[]
    for path in tree:
        if folder=='legend-of-hondo': selected='/hondo/' in path or path.startswith('doc/features/')
        elif folder=='eif-multipassenger':selected='passenger_flash_speeder' in path
        else:selected=path.endswith('.lua') and '/bin/scripts/' in path and path not in baseline
        if selected:
            url=(f'https://gitlab.com/{repo}/-/blob/{rev}/' if folder=='eif-multipassenger' else f'https://github.com/{repo}/blob/{rev}/')+urllib.parse.quote(path)
            paths.append(dict(path=path,source=url,classification='Published source candidate; dependencies and individual notices require review before import'))
    source_inventory.append(dict(repository=repo,revision=rev,date=date,paths=paths,
        note='Additional paths are relative to current stock Core3 file names; a different path is not proof of original authorship. This also does not detect changed contents in same-named files.'))

result=dict(researched='2026-10-13',scope='Pre-CU-compatible community content discovery: SR advertised worlds/species; all collected MTG Lua and relevant archive index names; Sunrunner official world/species lists; EiF racial list and credits; original MTG releases; pinned Stardust, Darklight, Hondo and EiF passenger public sources. Private, unindexed and unreleased projects can contain additional content.',
 statuses=STATUS,rows=rows,source_revisions=[dict(repository=r['repository'],revision=r['revision'],date=r['date']) for r in source_inventory],
 underlying_rights='Contributor release statements cover only the work their authors can grant. They do not grant ownership of original SOE/Lucasfilm assets. Preserve the user-owned client baseline and do not treat this catalogue as permission to redistribute a complete game client.',
 counts=dict(ground_worlds=sum(r['kind']=='Planet' for r in rows),stations=sum(r['kind']=='Station' for r in rows),additional_species=sum(r['kind']=='Species' for r in rows),mtg_lua_files=len(mtg['files']),catalogue_entries=len(rows)))
(OUT/'content-catalogue.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(OUT/'published-source-paths.json').write_text(json.dumps(source_inventory,indent=2),encoding='utf-8')

lines=['# SWG community content catalogue','', 'Historical audit. The user subsequently excluded Sentinel’s Republic and requested deeper EiF/Uprising research. Use [the active catalogue](<C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Content-catalogue/SWG-active-content-catalogue.md>) for current decisions and updated species evidence.','', 'Researched 13 October 2026. Server and client unchanged during this research.','',
       f"This catalogue records **{result['counts']['ground_worlds']} named ground worlds, {result['counts']['stations']} stations and {result['counts']['additional_species']} additional playable-species implementations/candidates**, plus content packs, quests, tools and source-file inventories. These are discoveries across the audited sources, not a claim to catalogue every private mod ever created.", '',
       '## How to read the decisions','',
       '| Code | Decision |','|---|---|']
for code,label in STATUS.items():lines.append(f'| {code} | {label} |')
lines+=['',
 'P means a creator/project has offered the identified contribution for server use; it does not mean the package is installed, tested, complete, or cleared for every possible redistribution. C records explicit restrictions. U is an unresolved question, not a finding that a creator prohibits reuse. A follows an express permission requirement or the absence of a release for that original implementation. X identifies a conflicting restrictive notice; leave the file out until resolved.', '',
 'Permission, download availability, completeness and compatibility are separate. Keep credits and licenses with every imported package. MTG asks for full creator credit on a server website and no claim of authorship. Retain AGPL and file-level notices for published code; preserve the corresponding source and satisfy the applicable license when distributing or operating modified code.', '',
 result['underlying_rights'], '',
 '## What we actually possess','',
 '- The 23 MTG archives already collected and installed as fallback assets were read by index only in this audit.',
 '- All 16,734 Lua files in the published MTG content bundle were inventoried. They register 12,556 distinct object paths, including shared definitions, NPCs, props and support data. These are not 12,556 finished new items.',
 '- The existing in-game MTG builder catalogue has 8,051 inventory-oriented entries. That is a separate filtered count.',
 '- The working server still defines the original ten player species in Races.h. Custom player models/data in an archive do not enable character creation by themselves.',
 '- Thirteen original creator ZIPs were downloaded and inspected after the user signed into MTG. Their contents, hashes and retained notices are recorded in downloaded-package-evidence.json.',
 '- All newly researched projects remain separate reference copies. No additional planets, species, binary tools or gameplay packages were installed or executed.', '',
 '## Collected original packages','',
 'These are retained creator downloads, not prepared installation bundles. Counts include supporting files and do not represent finished gameplay items. Full SHA-256 hashes and original archive paths are in downloaded-package-evidence.json.', '',
 '| Package | Creator/project | Files | Size |','|---|---|---:|---:|']
package_authors={
 'newspecies.zip':'Halyn / Phoenix; thanks Sytner and Timbab',
 'zeltros_client.zip':'tienvogh', 'zeltros_server.zip':'tienvogh',
 "Abi's Lamp Pack.zip":'Abi', 'multipassenger.zip':'Halyn / Empire in Flames',
 'newsnet.zip':'Halyn / Empire in Flames', 'betterAstromechs.zip':'Halyn / Empire in Flames'}
for package in json.loads((OUT/'downloaded-package-evidence.json').read_text(encoding='utf-8')):
    filename='newspecies-original.zip' if package['name']=='newspecies.zip' else package['name']
    target=(OUT/filename).as_posix()
    author=package_authors.get(package['name'],'Borrie BoBaka / Dark Rebellion RP')
    lines.append(f"| [{filename}](<{target}>) | {author} | {len(package['files']):,} | {package['bytes']/1024:,.1f} KiB |")
lines+=['', '## Planets and stations','',
 '| Destination | Origin/version | Decision | Files and practical limitation | Sources |','|---|---|---|---|---|']
def links(row):return ', '.join(f'[source {i+1}]({u})' for i,u in enumerate(row['sources']))
def clean(s):return str(s).replace('|','/').replace('\n',' ')
for row in rows:
    if row['kind'] in ['Planet','Station','Candidate world','Legacy/test world']:
        proof='; '.join(x['path'] for x in row.get('local_asset_evidence',[]))
        lines.append(f"| {row['name']} | {clean(row['origin'])} | {row['status']} | {clean(row['notes'])}{(' Local: '+proof) if proof else ''} | {links(row)} |")
lines+=['',
 'The nine destinations on SR’s feature page are eight planets plus Tansarii Station. The ground worlds here include later expansion adaptations because they can be investigated for a pre-CU server; no NGE combat/profession system is being proposed.', '',
 'Kashyyyk assets also include separate main, hunting, dead-forest, Rryatt trail, north/south dungeon and PoB-dungeon terrains. These are subzones/variants, not seven additional planets. All terrain and snapshot names, including stock and developer data, are listed in MTG-inventory-summary.json.', '',
 'Different servers can have different versions of the same named planet. A public Bats Mandalore release is not permission for every later Mandalore makeover, and a public Taanab mini-expansion is not the same package as SR’s Hydro Station quests.', '',
 '## Additional species','',
 '| Species/character option | Decision | Verified player-model genders | Source and implementation gap |','|---|---|---|---|']
for row in rows:
    if row['kind']=='Species':
        genders=', '.join(row.get('genders',[])) or 'Complete package not inspected'
        lines.append(f"| {row['name']} | {row['status']} | {genders} | {clean(row['availability'])}. {links(row)} |")
lines+=['',
 'The first 15 entries are named in Halyn’s original 2016 beta 0.5 description. That page describes image-design, clothing/hood, naming and stat-migration issues. The author asks permission for uses outside the stated species-mod purpose. The actual downloaded newspecies.zip also includes Togruta player Lua and race-header entries, giving 16 additions. This supersedes the earlier description-only assumption that Togruta had no source in this package.', '',
 'Model evidence is deliberately limited: Talz has a male player template in the inspected archives, while an attribute table also names a female entry. That table entry alone does not establish a working female model. Nightsister and Singing Mountain Clan are separate playable options, not distinct biological species.', '',
 'For the 13 EiF-only candidates, an NPC appearance in MTG does not authorize copying EiF’s complete playable implementation or newly authored artwork. A fresh port from available assets is a separate possibility.', '',
 '## Packs, tools and asset families','',
 '| Content | Decision | Creator/project | What is available / remaining check | Sources |','|---|---|---|---|---|']
for row in rows:
    if row['kind'] in ['Pack or tool','Tool','MTG family','Quest example']:
        lines.append(f"| {row['name']} | {row['status']} | {clean(row['origin'])} | {clean(row['availability'])}. {clean(row['notes'])} | {links(row)} |")
lines+=['',
 '## SR gameplay whose complete release is still missing','',
 '| Feature | Decision | Finding | Sources |','|---|---|---|---|']
for row in rows:
    if row['kind']=='SR gameplay':lines.append(f"| {row['name']} | U | Complete reusable server implementation not found in the two inspected SR trees. | {links(row)} |")
lines+=['',
 'The SR location page also names Kaas’s Mailoc/Gundark caves, Dark Force Temple/Shrine, Ancient Tomb and Separatist Facility; Mandalore’s Darth Caedus cave, Bralor/Vizsla/Pyke/Shadow Collective locations and Taung bunker; Moraband’s Bane tomb and Sith academy; Chandrila’s Senate/Chandriltech locations; and Coruscant’s four districts. A location name can overlap a public version while later encounter logic remains unavailable. Use the source inventory to identify a specific published implementation.', '',
 '## Restrictions and unresolved rights','',
 '| Contribution | Decision | Action | Sources |','|---|---|---|---|']
for row in rows:
    if row['kind'] in ['Restricted or unverified family','Excluded file']:
        lines.append(f"| {row['name']} | {row['status']} | {clean(row['notes'])} | {links(row)} |")
lines+=['',
 'The older SR public tree and the newer SR public tree both load a separate custom_scripts screenplay entry point whose content is absent from their published trees. Their public labels therefore cannot substitute for the missing content or its authors’ terms.', '',
 '## Additional public code collections','',
 '| Project | Pinned revision / date | What the evidence supports |','|---|---|---|']
descriptions={
 'Levarrishawk/Stardust':'Author explicitly invites reuse of his published work. Includes city/POI scripts, Jakku Weapons Facility, several dungeon/heroic scripts and some Mustafar work. Its 2019 engine dependency and separate stardust_s.tre reference prevent treating it as a drop-in modern package.',
 'Levarrishawk/DLSWG5':'Creator announced the Elysium/Darklight release. Historical README identifies Chandrila, Coruscant, Kaas, Moraband and Hutta at different completeness levels plus Imperial, New Republic and Reelo theme parks.',
 'Tatwi/legend-of-hondo':'Creator explicitly permits using code, concepts and documentation. Includes a breadcrumb quest, NPC merchant, housing/decor, junk-dealer, bazaar-bot and admin-tool work. Archived project targets a 2016 server/engine base.',
 'Empire-In-Flames/swgemu-multipassenger':'Public AGPLv3 source linked by Halyn’s creator release. Actual Flash-speeder passenger source paths verified; matching passenger TRE downloaded and inventoried.'}
for repo in source_inventory:
    lines.append(f"| {repo['repository']} | `{repo['revision']}` / {repo['date']} | {descriptions[repo['repository']]} {len(repo['paths'])} candidate paths indexed. |")
lines+=['',
 'published-source-paths.json records every selected path and a revision-pinned source link. For Stardust/Darklight, these are Lua paths not present under the same name in our current Core3 tree. That is an efficient candidate list, not proof every file is original or functional; same-named modified files are outside that comparison.', '',
 '## Availability gaps and contact targets','',
 '| Target | Concrete question / missing material |','|---|---|',
 '| Halyn / Empire in Flames | Any modern-Core3 fixes for the collected species package; terms/source for the 13 further EiF species and their custom art. Public passenger TRE has now been collected. |',
 '| Takhomasak / Sunrunner II | Which original planet releases remain available, and which specific modern planet/art/script versions may be reused with credit. |',
 '| Levarrishawk / Stardust | Current mirrors for Stardust_01/02/03 TREs and the server-only stardust_s.tre; confirmation of third-party notices for the selected planet packages. |',
 '| Bats | Current complete mirror for original Mandalore terrain, world/NPC/cave files, and any later released Geonosis work. |',
 '| tienvogh | Exact CC-BY-NC version if needed for public redistribution; client/server ZIPs are now collected. |',
 '| Borrie | Light Megapack redistribution scope before rehosting; Wall/Torch/Kitchen/Naboo/Rank-plate notices are resolved. Abi’s file-level credit permission is also verified. |',
 '| SR content authors / current SR staff | An author-approved release for each selected missing dungeon or quest, with source, assets, dependencies and credits. |', '',
 'No contact messages or permission requests were sent. The user signed into MTG, permitting inspection of 13 ZIP packages. Original archive contents and notices were retained; no code was run. Old Drive links remain leads: failed web fetches alone do not prove deletion. Some newly published tools still need package-level terms reviewed.', '',
 '## Practical shortlist','',
 '1. Original public Taanab release; original Mandalore and Dromund Kaas releases, supplemented by carefully selected published Stardust source. Keep each version and creator separate.',
 '2. Halyn’s collected species ZIP as a 16-addition porting reference. Test creation, relog, image design, equipment, cloning and stat migration.',
 '3. Zeltros for noncommercial exploration/world-building, with creator credit and its resource-page CC terms retained alongside the ZIPs.',
 '4. Borrie’s explicitly redistributable Torch, Kitchen and Naboo Structure packs. Treat Dark Interiors as a repair/test project because its release documents crashing variants.',
 '5. Halyn’s public multipassenger system and Hondo’s documented merchant/quest/building tools as separate modern-Core3 ports.', '',
 'This is a permission and availability audit, not an installation approval or a claim that every contribution has been reviewed by its rights holder. An item marked U stays unresolved until its actual package or author statement resolves the gap.', '']
(OUT/'SWG-content-catalogue.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(dict(counts=result['counts'],status_counts=dict(collections.Counter(r['status'] for r in rows)),source_candidates={r['repository']:len(r['paths']) for r in source_inventory}),indent=2))
