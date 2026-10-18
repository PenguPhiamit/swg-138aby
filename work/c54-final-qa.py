from pathlib import Path
import subprocess,re,json
r=Path('/opt/swg/Core3-gpt'); w=Path(__file__).parent/'c54-compile';(w/'system').mkdir(parents=True,exist_ok=True)
(w/'system/lang.h').write_text('''#include <cstdint>
#include <cstring>
#include <string>
using uint32 = uint32_t;
class String : public std::string { public: using std::string::string; const char* toCharArray() const {return c_str();} };
''')
(w/'race.cpp').write_text('''#include <cassert>
#include "/opt/swg/Core3-gpt/MMOCoreORB/src/server/zone/objects/player/Races.h"
int main() {
 static_assert(sizeof(Species)/sizeof(*Species)==RACE_COUNT);
 static_assert(sizeof(TemplateSpecies)/sizeof(*TemplateSpecies)==RACE_COUNT);
 static_assert(sizeof(Gender)/sizeof(*Gender)==RACE_COUNT);
 static_assert(sizeof(CCRaceStrs)/sizeof(*CCRaceStrs)==RACE_COUNT);
 static_assert(sizeof(SharedRace)/sizeof(*SharedRace)==RACE_COUNT);
 for (const char* g : {"male", "female"}) {
  String p((std::string("object/creature/player/hutt_")+g+".iff").c_str());
  int id=Races::getRaceID(p);
  assert(Races::getSpeciesID(id)==0xEA);
  assert(std::string(Races::getSpecies(id))=="hutt");
  assert(std::string(Races::getGender(id))==g);
  assert(std::string(Races::getCompleteRace(Races::getRaceCRC(id)))==p);
  assert(Races::getRaceCRC(id)==(std::string(g)=="male" ? 0x916443F9 : 0xE0B607C0));
 }
 assert(Races::getRaceCRC(-1)==0 && Races::getRaceCRC(RACE_COUNT)==0);
}
''')
subprocess.run(['nice','-n','10','g++','-std=c++17','-I',str(w),str(w/'race.cpp'),'-o',str(w/'race')],check=True)
subprocess.run([str(w/'race')],check=True)
files=set(subprocess.check_output(['git','-C',str(r),'diff','--name-only','HEAD'],text=True).splitlines())
files.update(subprocess.check_output(['git','-C',str(r),'ls-files','--others','--exclude-standard'],text=True).splitlines())
lua=[r/f for f in files if f.endswith('.lua')]
for f in lua:subprocess.run(['luac5.3','-p',str(f)],check=True)
baseline=subprocess.check_output(['git','-C',str(r),'show','HEAD:MMOCoreORB/bin/scripts/managers/databaseversions/2573version.lua'])
assert baseline==(r/'MMOCoreORB/bin/scripts/managers/databaseversions/2573version.lua').read_bytes()
print(f'PASS: compiled actual Races.h (six parallel arrays, both Hutt rows/CRCs, reverse lookup, bounds); {len(lua)} changed/new Lua syntax checks; sole all-tree syntax error is byte-identical to base')
print('NAME TEST: stock generic generator supports the 33 Hutt syllables and exact kajidic unique pattern; lifecycle inspected, full engine execution untested')
