#!/usr/bin/env python3
"""Offline C34r regression: compile extracted command code with narrow stand-ins.

Run as swgemu in WSL: python3 <this file> [--repo /opt/swg/Core3-gpt]
No server build or runtime access. Does not test locking, observers or persistence.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def function(source, signature):
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


PRELUDE = r'''
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <string>
#include "json.hpp"
using uint64 = uint64_t;
using uint8 = uint8_t;
using JSONSerializationType = nlohmann::json;
constexpr int SUCCESS = 0, GENERALERROR = 1, INVALIDPARAMETERS = 2;
#define STRING_HASHCODE(x) 12345
struct String {
    std::string value;
    String(const char* s): value(s) {}
    bool operator==(const char* s) const { return value == s; }
    const char* toCharArray() const { return value.c_str(); }
    friend String operator+(const char* a, const String& b) {
        return String((std::string(a) + b.value).c_str());
    }
};
struct Math {
    static float min(float a, float b) { return std::min(a,b); }
    static float max(float a, float b) { return std::max(a,b); }
};
struct System { static int roll; static int random(int) { return roll; } };
int System::roll = 0;
struct CreatureAttribute { static constexpr uint8 HEALTH=0, ACTION=3, MIND=6; };
struct CreatureState {
    static constexpr uint64 POISONED=1ull<<30, DISEASED=1ull<<31,
        ONFIRE=1ull<<32, BLEEDING=1ull<<33, SWIMMING=1ull<<34;
};
struct CreatureObject {
    std::array<int,9> wounds{}, ham{100,100,100,100,100,100,100,100,100};
    uint64 states = 0;
    uint8 posture = 0;
    int shock = 0, damageCalls = 0;
    bool destroy = false;
    JSONSerializationType last;
    uint64 getObjectID() { return 9007199254740993ull; }
    void addWounds(int p,int n,bool,bool) { wounds[p] += n; }
    void addShockWounds(int n,bool,bool) { shock += n; }
    void setDizziedState(int) { states |= 1; }
    void setStunnedState(int) { states |= 2; }
    void setBlindedState(int) { states |= 4; }
    void setIntimidatedState(int) { states |= 8; }
    bool hasState(uint64 s) { return states & s; }
    int getHAM(int p) { return ham[p]; }
    int getWounds(int p) { return wounds[p]; }
    uint64 getStateBitmask() { return states; }
    uint8 getPosture() { return posture; }
    int getShockWounds() { return shock; }
    void inflictDamage(CreatureObject* attacker, int p, float n, bool d) {
        assert(attacker); ++damageCalls; destroy=d; ham[p]-=int(n);
    }
    void sendSystemMessage(const String& s) { last=JSONSerializationType::parse(s.value.substr(12)); }
    int addDotState(CreatureObject*, uint64 dotType, uint64 source, unsigned strength,
                    uint8 pool, unsigned duration, float potency, unsigned defense,
                    int secondaryStrength=0) {
        assert(source==12345 && strength==30 && pool==0 && defense==0);
        assert(duration==(dotType==CreatureState::POISONED || dotType==CreatureState::DISEASED ? 120u:60u));
        assert(secondaryStrength==(dotType==CreatureState::ONFIRE ? 6:0));
        auto* victim=this;
        /*ADMISSION*/
        states |= dotType;
        return 30;
    }
};
struct Command {
/*COMMAND*/
};
'''

MAIN = r'''
int main(int argc,char**) {
    const bool fixed = argc>1;
    Command command;
    int absent=0, errors=0;
    for (const char* kind : {"poison","disease","fire","bleeding"}) {
        for (int roll=0;roll<=100;++roll) {
            CreatureObject caller, patient;
            System::roll=roll;
            int rc=command.applyAffliction(&caller,&patient,String(kind));
            auto& reply=caller.last;
            assert(reply["dot"].is_number_integer());
            assert(reply["target"].is_number_unsigned() && reply["target"]==9007199254740993ull);
            assert(reply["states"].is_number_unsigned());
            assert(reply["posture"].is_number_integer());
            assert(reply["wounds"].is_array() && reply["wounds"].size()==9);
            assert(reply["ham"].is_array() && reply["ham"].size()==9);
            assert(rc==SUCCESS);
            absent += patient.states==0;
            errors += reply.contains("error");
        }
    }
    assert(absent==(fixed ? 0:84) && errors==0);
    int swimErrors=0;
    for (int roll=0;roll<=100;++roll) {
        CreatureObject caller, patient;
        patient.states=CreatureState::SWIMMING;
        System::roll=roll;
        int rc=command.applyAffliction(&caller,&patient,String("fire"));
        assert(caller.last["dot"]==0);
        assert(rc==(fixed ? GENERALERROR:SUCCESS));
        swimErrors+=caller.last.contains("error");
    }
    assert(swimErrors==(fixed ? 101:0));
    for (const char* kind : {"wounds","fatigue","dizzy","stunned","blinded","intimidated","damage","incap","invalid"}) {
        CreatureObject caller, patient;
        int rc=command.applyAffliction(&caller,&patient,String(kind));
        assert(rc==(std::string(kind)=="invalid" ? INVALIDPARAMETERS:SUCCESS));
        if (std::string(kind)=="damage") {
            assert(patient.damageCalls==3 && !patient.destroy);
            assert(patient.ham[0]==50 && patient.ham[3]==50 && patient.ham[6]==50);
        }
        if (std::string(kind)=="incap") {
            assert(patient.damageCalls==1 && patient.destroy && patient.ham[0]==-1);
        }
        if (std::string(kind)=="wounds") for (int w:patient.wounds) assert(w==100);
        if (std::string(kind)=="fatigue") assert(patient.shock==100);
    }
    std::cout<<JSONSerializationType({{"dot_trials",404},{"missing_dots",absent},
        {"swimming_trials",101},{"reported_swimming_errors",swimErrors},
        {"other_dispatch_cases",9},{"numeric_json_and_arrays",true}}).dump()<<"\n";
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('/opt/swg/Core3-gpt'))
    parser.add_argument('--compiler', default=shutil.which('clang++') or shutil.which('clang++-19')
                        or '/usr/lib/llvm-19/bin/clang++')
    parser.add_argument('--engine-include', type=Path, default=Path(
        '/opt/swg/Core3-dev/MMOCoreORB/utils/engine3/MMOEngine/src/engine/util'))
    args = parser.parse_args()
    root = args.repo / 'MMOCoreORB'
    header = 'MMOCoreORB/src/server/zone/objects/creature/commands/AgentGearCommand.h'
    original = subprocess.check_output(['git', 'show', '9b93665d:'+header], cwd=args.repo, text=True)
    patched = (args.repo/header).read_text()
    dot_list = (root/'src/server/zone/objects/creature/damageovertime/DamageOverTimeList.cpp').read_text()
    start = dot_list.index('if (strength == 0 || duration == 0)')
    end = dot_list.index('if (pool == CreatureAttribute::UNKNOWN)', start)
    admission = dot_list[start:end]
    include = args.engine_include
    results = {}
    with tempfile.TemporaryDirectory(prefix='c34r-') as tmp:
        tmp = Path(tmp)
        for name, source in [('original', original), ('patched', patched)]:
            cpp = PRELUDE.replace('/*ADMISSION*/', admission).replace(
                '/*COMMAND*/', function(source, 'int applyAffliction(')) + MAIN
            file = tmp/(name+'.cpp')
            file.write_text(cpp)
            exe = tmp/name
            subprocess.run([args.compiler, '-std=c++17', '-Wall', '-Wextra',
                            '-Wno-unused-parameter', '-I'+str(include), str(file), '-o', str(exe)], check=True)
            results[name] = json.loads(subprocess.check_output(
                [str(exe)] + (['fixed'] if name=='patched' else []), text=True))
    kits = function(patched, 'static bool addItemKit(')
    paths = sorted(set(re.findall(r'"(object/[^"\n]+\.iff)"', kits)))
    assert len(paths)==63
    for path in paths:
        assert path in (root/'bin/scripts'/path.replace('.iff','.lua')).read_text(), path
    results['registered_unique_kit_paths'] = len(paths)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
