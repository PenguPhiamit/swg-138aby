from pathlib import Path
import subprocess,json
r='/opt/swg/Core3-gpt'; base='MMOCoreORB/'
def commit(title,paths):
 paths=[base+p for p in paths]
 subprocess.run(['git','-C',r,'add','--',*paths],check=True)
 subprocess.run(['git','-C',r,'commit','-m',title+'\n\nAgent: ChatGPT','--',*paths],check=True)
 return subprocess.check_output(['git','-C',r,'rev-parse','--short=8','HEAD'],text=True).strip()
hashes={}
hashes['refusals']=commit('C54: give player Hutts their species ID and complete sit/call refusals',[
 'bin/scripts/object/creature/player/hutt_male.lua','bin/scripts/object/creature/player/hutt_female.lua',
 'src/server/zone/objects/creature/commands/SitServerCommand.h','src/server/zone/objects/creature/commands/MountCommand.h',
 'src/server/zone/objects/intangible/VehicleControlDeviceImplementation.cpp'])
folders=['mobile/vehicle','intangible/vehicle','tangible/deed/vehicle_deed','draft_schematic/vehicle/civilian']
stems=['a1_deluxe_floater','a1_deluxe_floater_pcd','a1_deluxe_floater_deed','a1_deluxe_floater']
paths=['bin/scripts/managers/crafting/schematics.lua']
for folder,stem in zip(folders,stems):paths.extend('bin/scripts/object/'+folder+'/'+f for f in [stem+'.lua','objects.lua','serverobjects.lua'])
hashes['floater']=commit('C54: add the Artisan-crafted A1 Deluxe Floater vehicle chain',paths)
hashes['names']=commit('C54: load original Hutt syllable and kajidic name tables',[
 'bin/scripts/managers/name/name_manager.lua','bin/scripts/managers/name/species/hutt.lua',
 'src/server/zone/managers/name/NameManager.cpp','src/server/zone/managers/name/NameManager.h'])
Path(__file__).with_name('c54-commits.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(json.dumps(hashes))
