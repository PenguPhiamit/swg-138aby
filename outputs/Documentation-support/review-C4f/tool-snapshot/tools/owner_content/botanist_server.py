"""Botanist feasibility test, server side (owner, 14 Oct: Botanist first; new professions enter at IV).

Inside Debian, as swgemu (writes LF files in /opt/swg/Core3-dev only):
    python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/owner_content/botanist_server.py [--dry-run]

The client half (skills.iff rows outdoors_botanist + outdoors_botanist_novice, and the strings) is built into
local_planets.tre by tools/hoth/hoth_client_build.py; the server reads the same skills.iff from that archive (test
galaxy: first in its archive list). This adds what a trainer needs:
  - screenplays/trainers/trainerData.lua: trainer_botanist teaches outdoors_botanist_novice;
  - mobile/conversations/trainer/trainer_conv.lua: botanistTrainerConvoTemplate (the stock trainer conversation);
  - mobile/trainer/trainer_botanist.lua: Bio-Engineer's trainer with a ranger's outfit, + its serverobjects include;
  - screenplays/cities/tatooine_mos_eisley.lua: one trainer outdoors in Mos Eisley, 5 m from the Scout trainer.
Re-running is safe: every change is made once.
"""
import re, sys
from pathlib import Path

S = Path('/opt/swg/Core3-dev/MMOCoreORB/bin/scripts')
DRY = '--dry-run' in sys.argv
NOTE = '-- Botanist feasibility test (14 Oct 2026, Claude; outputs/Content-catalogue/owner-SWG-SW5E/README.md)'


def edit(rel, marker, change):
    path = S / rel
    text = path.read_text(encoding='utf-8')
    assert '\r\n' not in text, rel
    if marker in text:
        print(f'already done: {rel}')
        return
    new = change(text)
    assert new != text, rel
    if DRY:
        print(f'would change {rel} (+{len(new) - len(text)} bytes)')
    else:
        path.write_text(new, encoding='utf-8', newline='\n')
        print(f'changed {rel}')


def after(anchor, addition):
    def change(text):
        assert text.count(anchor) == 1, anchor
        return text.replace(anchor, anchor + addition)
    return change


def main():
    edit('screenplays/trainers/trainerData.lua', 'trainer_botanist',
         after('\t\t"outdoors_bio_engineer_production_04"\n\t},\n',
               f'\n\t{NOTE}\n\ttrainer_botanist = {{\n\t\t"outdoors_botanist_novice"\n\t}},\n'))
    edit('mobile/conversations/trainer/trainer_conv.lua', 'botanistTrainerConvoTemplate',
         after('createTrainerConversationTemplate("bioengineerTrainerConvoTemplate", "trainer_bioengineer")\n',
               'createTrainerConversationTemplate("botanistTrainerConvoTemplate", "trainer_botanist") ' + NOTE + '\n'))

    bio = (S / 'mobile/trainer/trainer_bioengineer.lua').read_text(encoding='utf-8')
    ranger = (S / 'mobile/trainer/trainer_ranger.lua').read_text(encoding='utf-8')
    outfit = re.search(r'\ttemplates = \{.*?\n\t\},\n', ranger, re.S).group(0)
    body = re.sub(r'\ttemplates = \{.*?\n\t\},\n', lambda m: outfit, bio, count=1, flags=re.S)
    body = (body.replace('trainer_bioengineer', 'trainer_botanist')
                .replace('bioengineerTrainerConvoTemplate', 'botanistTrainerConvoTemplate'))
    assert body.count('trainer_botanist') >= 3 and 'dressed_ranger_trainer' in body
    target = S / 'mobile/trainer/trainer_botanist.lua'
    text = NOTE + ': the Bio-Engineer trainer with a ranger\'s outfit.\n\n' + body
    if DRY:
        print(f'would write mobile/trainer/trainer_botanist.lua ({len(text)} bytes)')
    elif not target.exists() or target.read_text(encoding='utf-8') != text:
        target.write_text(text, encoding='utf-8', newline='\n')
        print('wrote mobile/trainer/trainer_botanist.lua')
    edit('mobile/trainer/serverobjects.lua', 'trainer_botanist.lua',
         after('includeFile("trainer/trainer_bioengineer.lua")\n', 'includeFile("trainer/trainer_botanist.lua") ' + NOTE + '\n'))

    edit('screenplays/cities/tatooine_mos_eisley.lua', '"trainer_botanist"',
         after('\t\t{"trainer_scout",0,3519.76,5,-4786.9,77,0, ""},\n',
               '\t\t{"trainer_botanist",0,3516.0,5,-4783.0,77,0, ""}, ' + NOTE + '\n'))


if __name__ == '__main__':
    main()
