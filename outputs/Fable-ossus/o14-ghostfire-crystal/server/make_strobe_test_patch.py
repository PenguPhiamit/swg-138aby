"""Stage the server half of the O14 strobe-trail test saber B (Claude, 18 Oct 2026) as a patch for Core3-dev. Writes
nothing under /opt/swg: it copies the touched files from the dev tree's HEAD into a scratch git repo under /tmp, edits
them there (every edit asserts its anchor), and writes strobe-test-dev.patch next to this script.

    wsl -d Debian -- python3 make_strobe_test_patch.py

Test saber B is the Ghostfire Lightsaber (O13) under a second template, so the client can give it its own trail row
(appearance/sw_ghostfire_b.swh). Staff spawn it with: /server loot item ossus_ghostfire_saber_b 1
"""
import os
import shutil
import subprocess

DEV = '/opt/swg/Core3-dev'
S = 'MMOCoreORB/bin/scripts/'
D = S + 'object/weapon/melee/sword/crafted_saber/'
STAGE = '/tmp/ghostfire-strobe-stage'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'strobe-test-dev.patch')
FILES = {'objects': D + 'objects.lua', 'serverobjects': D + 'serverobjects.lua', 'items': S + 'loot/items.lua'}
A_TPL, B_TPL = D + 'sword_lightsaber_one_handed_ghostfire.lua', D + 'sword_lightsaber_one_handed_ghostfire_b.lua'
A_ITEM, B_ITEM = S + 'loot/items/ossus/ossus_ghostfire_saber.lua', S + 'loot/items/ossus/ossus_ghostfire_saber_b.lua'


def git(*args, cwd=STAGE):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True).stdout


def head(path):
    return git('show', 'HEAD:' + path, cwd=DEV).decode('utf-8')


def put(path, text):
    full = os.path.join(STAGE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def once(text, old, new):
    assert text.count(old) == 1, 'anchor not unique: %r' % old[:80]
    return text.replace(old, new)


def main():
    shutil.rmtree(STAGE, ignore_errors=True)
    os.makedirs(STAGE)
    git('init', '-q')
    git('config', 'user.name', 'stage')
    git('config', 'user.email', 'stage@localhost')
    for p in FILES.values():
        put(p, head(p))
    git('add', '-A')
    git('commit', '-q', '-m', 'Core3-dev HEAD')

    objects = head(FILES['objects'])
    assert 'one_handed_ghostfire_b' not in objects and 'one_handed_ghostfire.iff' in objects
    put(FILES['objects'], objects + '''
-- O14 strobe-trail test saber B (18 Oct 2026): the Ghostfire Lightsaber under a second template, for its own trail row.
object_weapon_melee_sword_crafted_saber_shared_sword_lightsaber_one_handed_ghostfire_b = SharedWeaponObjectTemplate:new {
	clientTemplateFileName = "object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire_b.iff"
}

ObjectTemplates:addClientTemplate(object_weapon_melee_sword_crafted_saber_shared_sword_lightsaber_one_handed_ghostfire_b, "object/weapon/melee/sword/crafted_saber/shared_sword_lightsaber_one_handed_ghostfire_b.iff")
''')
    tpl = head(A_TPL).replace('sword_lightsaber_one_handed_ghostfire', 'sword_lightsaber_one_handed_ghostfire_b')
    assert tpl.count('one_handed_ghostfire_b') == 4
    tpl = once(tpl, '-- The Ossus ghostfire lightsaber (O13, 18 Oct 2026)',
               '-- O14 strobe-trail test saber B (18 Oct 2026), a copy of the Ossus ghostfire lightsaber (O13, 18 Oct 2026)')
    put(B_TPL, tpl)
    put(FILES['serverobjects'], once(
        head(FILES['serverobjects']),
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_ghostfire.lua") -- Ossus O13\n',
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_ghostfire.lua") -- Ossus O13\n'
        'includeFile("weapon/melee/sword/crafted_saber/sword_lightsaber_one_handed_ghostfire_b.lua") -- O14 trail test B\n'))
    item = head(A_ITEM).replace('ossus_ghostfire_saber', 'ossus_ghostfire_saber_b')
    item = once(item, '"Ghostfire Lightsaber"', '"Ghostfire Lightsaber (trail test B)"')
    item = once(item, 'sword_lightsaber_one_handed_ghostfire.iff', 'sword_lightsaber_one_handed_ghostfire_b.iff')
    put(B_ITEM, '-- O14 strobe-trail test saber B (18 Oct 2026): staff only, /server loot item ossus_ghostfire_saber_b 1\n' + item)
    put(FILES['items'], once(head(FILES['items']), 'includeFile("items/ossus/ossus_ghostfire_saber.lua")\n',
                             'includeFile("items/ossus/ossus_ghostfire_saber.lua")\n'
                             'includeFile("items/ossus/ossus_ghostfire_saber_b.lua")\n'))

    git('add', '-N', B_TPL, B_ITEM)
    patch = git('diff')
    with open(OUT, 'wb') as f:
        f.write(patch)
    git('apply', '--check', OUT, cwd=DEV)
    for p in list(FILES.values()) + [B_TPL, B_ITEM]:
        subprocess.run(['luac', '-p', os.path.join(STAGE, p)], check=True)
    print('wrote %s (%d bytes); git apply --check on %s: ok; luac -p on 5 files: ok' % (OUT, len(patch), DEV))


if __name__ == '__main__':
    main()
