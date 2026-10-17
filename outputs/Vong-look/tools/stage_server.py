"""Vong look test, step 4, the server half (Claude, 17 Oct 2026). Edits a scratch copy of Core3-dev's scripts.

    python -I stage_server.py <scratch root holding MMOCoreORB/bin/scripts copies of the dev files>

What it adds (the owner's pick, 17 Oct: "Mix: bone + s02 collar", no helmet; one warrior to look at, patrols later):
- server templates for our eight wearables (no helmet), cloned from the stock bone s01 pieces and the marauder s02 chest with the
  same renames as the client step (build_vong_client.py): object/tangible/wearables/armor/vong/armor_vong_s01_<p> and
  .../armor/vongcrab/armor_vongcrab_s02_chest_plate. Stats are the stock ones; item names and descriptions still use
  the stock strings (our own strings come later);
- the outfit vong_fanatic_warrior_outfit (no customization: the cloned shaders' colour 0 is palette/white.pal);
- the mobile vong_fanatic_warrior_look: the generic human male body of the Mos Taike guards (mos_taike_guard_old.iff;
  fix of 17 Oct, see vong-look-body-fix.patch), our outfit, no helmet, scale 1.15, not attackable,
  no faction yet (the vong_fanatic side comes with the patrols);
- the screenplay OssusVongLookScreenPlay: one warrior at the Ossus Project fields, POI 7 (1400, 4900), on the ground.

Each edit replaces an anchor that must occur exactly once, so a moved dev file stops the step instead of patching the
wrong place. The patch in ../vong-look.patch is `git diff` of the result.
"""
import os
import re
import sys

ROOT = os.path.join(sys.argv[1], 'MMOCoreORB', 'bin', 'scripts')
ARMOR = 'object/tangible/wearables/armor'
BONE = ['bicep_l', 'bicep_r', 'bracer_l', 'bracer_r', 'boots', 'gloves', 'leggings']
HEAD = ('-- Vong look test (owner, 17 Oct 2026): our armour clones; the client files are in local_planets.tre\n'
        '-- (outputs/Vong-look/tools/build_vong_client.py). %s Claude.\n\n')


def read(rel):
    return open(os.path.join(ROOT, rel), encoding='utf-8', newline='').read()


def edit(rel, pairs):
    text = read(rel)
    for old, new_text in pairs:
        assert text.count(old) == 1, (rel, old[:70], text.count(old))
        text = text.replace(old, new_text)
    open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='').write(text)


def new(rel, text):
    path = os.path.join(ROOT, rel)
    assert not os.path.exists(path), rel
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8', newline='').write(text)


def shared_block(objects_text, var):
    """The `var = SharedTangibleObjectTemplate:new { ... }` block through its addClientTemplate line."""
    m = re.search(r'^%s = SharedTangibleObjectTemplate:new \{.*?^ObjectTemplates:addClientTemplate\(%s, "[^"]+"\)\n'
                  % (re.escape(var), re.escape(var)), objects_text, re.S | re.M)
    assert m, var
    return m.group(0)


def rename(text, pairs, keep):
    """Apply the renames, then put back the stock string references (@wearables_*:...) that `keep` names."""
    for old, new_text in pairs:
        text = text.replace(old, new_text)
    for k in keep:
        text = text.replace(k[1], k[0])
    return text


def clone_set(folder_old, folder_new, stem_old, stem_new, pieces):
    """Shared and server templates for one stock set, renamed; returns the include lines."""
    objects_old = read('%s/%s/objects.lua' % (ARMOR, folder_old))
    pairs = [('object_tangible_wearables_armor_%s_shared_armor_%s' % (folder_old, stem_old),
              'object_tangible_wearables_armor_%s_shared_armor_%s' % (folder_new, stem_new)),
             ('object_tangible_wearables_armor_%s_armor_%s' % (folder_old, stem_old),
              'object_tangible_wearables_armor_%s_armor_%s' % (folder_new, stem_new)),
             ('%s/%s/shared_armor_%s' % (ARMOR, folder_old, stem_old), '%s/%s/shared_armor_%s' % (ARMOR, folder_new, stem_new)),
             ('%s/%s/armor_%s' % (ARMOR, folder_old, stem_old), '%s/%s/armor_%s' % (ARMOR, folder_new, stem_new)),
             ('appearance/armor_%s' % stem_old, 'appearance/armor_%s' % stem_new)]
    keep = [('@wearables_%s:armor_%s' % (kind, stem_old), '@wearables_%s:armor_%s' % (kind, stem_new))
            for kind in ('name', 'detail', 'lookat', 'descriptions')]
    shared, includes = [], []
    for p in pieces:
        var = 'object_tangible_wearables_armor_%s_shared_armor_%s_%s' % (folder_old, stem_old, p)
        block = rename(shared_block(objects_old, var), pairs, keep)
        assert ('armor_%s' % stem_old) not in re.sub(r'"@wearables_[a-z]+:[^"]*"', '', block), block
        shared.append(block)
        server_old = read('%s/%s/armor_%s_%s.lua' % (ARMOR, folder_old, stem_old, p))
        server_new = rename(server_old, pairs, keep)
        assert ('armor_%s' % stem_old) not in re.sub(r'"@wearables_[a-z]+:[^"]*"', '', server_new), p
        new('%s/%s/armor_%s_%s.lua' % (ARMOR, folder_new, stem_new, p), server_new)
        includes.append('includeFile("tangible/wearables/armor/%s/armor_%s_%s.lua")\n' % (folder_new, stem_new, p))
    new('%s/%s/objects.lua' % (ARMOR, folder_new), HEAD % ('Shared templates cloned from the stock %s set.' % folder_old)
        + '\n'.join(shared))
    new('%s/%s/serverobjects.lua' % (ARMOR, folder_new), HEAD % ('Server templates.') + ''.join(includes))


# 1. the wearables
clone_set('bone', 'vong', 'bone_s01', 'vong_s01', BONE)
clone_set('marauder', 'vongcrab', 'marauder_s02', 'vongcrab_s02', ['chest_plate'])
edit('object/allobjects.lua', [
    ('includeFile("tangible/wearables/armor/bone/objects.lua")\n',
     'includeFile("tangible/wearables/armor/bone/objects.lua")\n'
     'includeFile("tangible/wearables/armor/vong/objects.lua") -- Sandbox: Vong look test\n'),
    ('includeFile("tangible/wearables/armor/marauder/objects.lua")\n',
     'includeFile("tangible/wearables/armor/marauder/objects.lua")\n'
     'includeFile("tangible/wearables/armor/vongcrab/objects.lua") -- Sandbox: Vong look test\n')])
edit('%s/serverobjects.lua' % ARMOR, [
    ('includeFile("tangible/wearables/armor/bone/serverobjects.lua")\n',
     'includeFile("tangible/wearables/armor/bone/serverobjects.lua")\n'
     'includeFile("tangible/wearables/armor/vong/serverobjects.lua") -- Sandbox: Vong look test\n'),
    ('includeFile("tangible/wearables/armor/marauder/serverobjects.lua")\n',
     'includeFile("tangible/wearables/armor/marauder/serverobjects.lua")\n'
     'includeFile("tangible/wearables/armor/vongcrab/serverobjects.lua") -- Sandbox: Vong look test\n')])

# 2. the outfit: the owner's mix, no helmet, no customization
items = ['%s/vongcrab/armor_vongcrab_s02_chest_plate.iff' % ARMOR] + \
        ['%s/vong/armor_vong_s01_%s.iff' % (ARMOR, p) for p in BONE]
new('mobile/outfits/vong_fanatic_warrior_outfit.lua',
    HEAD % ('The cloned shaders take colour 0 from palette/white.pal and our textures\' alpha (the hue mask) is 0, so\n'
            '-- no customization is set.')
    + 'vong_fanatic_warrior_outfit = {\n\t{\n'
    + ',\n'.join('\t\t{objectTemplate = "%s", customizationVariables = {} }' % t for t in items)
    + '\n\t}\n}\n\naddOutfitGroup("vong_fanatic_warrior_outfit", vong_fanatic_warrior_outfit)\n')
edit('mobile/outfits/serverobjects.lua', [
    ('includeFile("outfits/vardias_tyne_outfit.lua")',
     'includeFile("outfits/vardias_tyne_outfit.lua")\nincludeFile("outfits/vong_fanatic_warrior_outfit.lua") -- Sandbox: Vong look test')])

# 3. the warrior: the Mos Taike guards' generic human male body (it wears stock armour outfits; human_male.iff draws a fat
#    commoner, see the comment in the template), bare-headed (owner: "no helmet"), taller
#    (Wookieepedia: much taller and heavier than humans). Not attackable and no faction for the look.
new('mobile/sandbox/ossus_vong.lua', HEAD % ('One warrior for the owner\'s look at the Ossus Project fields.') + '''vong_fanatic_warrior_look = Creature:new {
	objectName = "",
	customName = "a Vong warrior",
	socialGroup = "",
	mobType = MOB_NPC,
	faction = "",
	level = 30,
	chanceHit = 0.39,
	damageMin = 290,
	damageMax = 300,
	baseXp = 0,
	baseHAM = 8400,
	baseHAMmax = 10200,
	armor = 0,
	resists = {0,0,0,0,0,0,0,-1,-1},
	meatType = "",
	meatAmount = 0,
	hideType = "",
	hideAmount = 0,
	boneType = "",
	boneAmount = 0,
	milk = 0,
	tamingChance = 0,
	ferocity = 0,
	pvpBitmask = NONE,
	creatureBitmask = NONE,
	optionsBitmask = AIENABLED + INVULNERABLE,
	diet = HERBIVORE,
	scale = 1.15,
	-- A body with the generic client data (client_shared_npc_human_m.cdf), as the Mos Taike guards that wear stock
	-- armour outfits. object/mobile/human_male.iff uses client_shared_npc_dressed_commoner_fat_human_male_02.cdf,
	-- which makes the client draw a fat commoner (blend_fat 204, jacket, pants, shoes, hair) instead of our armour
	-- (owner, 17 Oct: "the vong is just a fat human"). This body has no hair of its own: the warrior is bald.
	templates = {"object/mobile/mos_taike_guard_old.iff"},
	lootGroups = {},
	primaryWeapon = "unarmed",
	secondaryWeapon = "none",
	outfit = "vong_fanatic_warrior_outfit",
	primaryAttacks = {},
	secondaryAttacks = {}
}

CreatureTemplates:addCreatureTemplate(vong_fanatic_warrior_look, "vong_fanatic_warrior_look")
''')
edit('mobile/serverobjects.lua', [
    ('includeFile("sandbox/ossus_people.lua")\n',
     'includeFile("sandbox/ossus_people.lua")\nincludeFile("sandbox/ossus_vong.lua") -- Sandbox: Vong look test\n')])

# 4. the spawn: POI 7, the Ossus Project fields (Fable-ossus/o6/README.md), on the ground; no respawn needed
new('screenplays/sandbox/ossus_vong_look.lua', HEAD % ('One warrior at POI 7 for the owner\'s look; patrols later.') + '''OssusVongLookScreenPlay = ScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "OssusVongLookScreenPlay",

	planet = "ossus",
	x = 1400, y = 4900, heading = 200,
}

registerScreenPlay("OssusVongLookScreenPlay", true)

function OssusVongLookScreenPlay:start()
	if (isZoneEnabled(self.planet)) then
		spawnMobile(self.planet, "vong_fanatic_warrior_look", 0, self.x, getWorldFloor(self.x, self.y, self.planet), self.y, self.heading, 0)
	end
end
''')
edit('screenplays/screenplays.lua', [
    ('includeFile("sandbox/ossus_world.lua")\n',
     'includeFile("sandbox/ossus_world.lua")\nincludeFile("sandbox/ossus_vong_look.lua") -- Sandbox: Vong look test\n')])
print('staged')
