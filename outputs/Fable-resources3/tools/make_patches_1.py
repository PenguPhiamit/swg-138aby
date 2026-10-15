"""R3 part 1 (Hoth complete): patch tools/hoth/hoth_client_build.py resource_tree() for MTG's four gem leaves and the
three site-limited energies, and resource_manager.lua for their pools. Edits on the verbatim copies in work/orig."""
import os
import subprocess

R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3'
O, N = R + '/work/orig', R + '/work/new'
LF = chr(10)


def rd(rel):
    with open(O + '/' + rel, encoding='utf-8', newline='') as f:
        return f.read()


def wr(rel, text):
    os.makedirs(os.path.dirname(N + '/' + rel), exist_ok=True)
    with open(N + '/' + rel, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def edited(text, reps, label):
    for old, new in reps:
        assert text.count(old) == 1, (label, old[:70], text.count(old))
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------- the builder
B = 'tools/hoth/hoth_client_build.py'
GEMS = LF.join([
    "# MTG's four Hoth gem leaves are named <class>_hoth_<n>, so endswith('_hoth') missed them (Fable R3, 14 Oct 2026). Core3",
    "# restricts a type by the '_hoth' substring (ResourceTree::setZoneRestriction), so the names are kept; their text is",
    "# retyped (MTG: \"Hothian Type 1 Crystal Amorphous Gem\"), spelt as the stock class text (\"Amorphous Gemstone\").",
    "HOTH_GEMS = {'armophous_hoth_1': 'Hothian Type 1 Amorphous Gemstone', 'armophous_hoth_2': 'Hothian Type 2 Amorphous Gemstone',",
    "             'crystalline_hoth_1': 'Hothian Type 1 Crystalline Gemstone', 'crystalline_hoth_2': 'Hothian Type 2 Crystalline Gemstone'}",
    '', '', 'def resource_tree():'])
builder = edited(rd(B), [
    ('def resource_tree():', GEMS),
    ("        elif r[1].endswith('_hoth'):" + LF + "            rows.append(list(r))" + LF,
     "        elif r[1].endswith('_hoth') or r[1] in HOTH_GEMS:" + LF +
     "            row = list(r)" + LF +
     "            if r[1] in HOTH_GEMS:" + LF +
     "                row[next(j for j in range(2, 10) if r[j] != '')] = HOTH_GEMS[r[1]]" + LF +
     "            rows.append(row)" + LF),
    ("    for base, label in (('energy_renewable_unlimited_solar', 'Hoth Solar Renewable Energy')," + LF +
     "                        ('energy_renewable_unlimited_wind', 'Hoth Wind Renewable Energy')):" + LF,
     "    # The three site-limited energies too (R3): stock has no class row for them, only the per-planet leaves, so a new" + LF +
     "    # leaf goes after the last leaf of its kind." + LF +
     "    for base, label in (('energy_renewable_unlimited_solar', 'Hoth Solar Renewable Energy')," + LF +
     "                        ('energy_renewable_unlimited_wind', 'Hoth Wind Renewable Energy')," + LF +
     "                        ('energy_renewable_site_limited_geothermal', 'Hoth Geothermal Renewable Energy')," + LF +
     "                        ('energy_renewable_site_limited_tidal', 'Hoth Tidal Renewable Energy')," + LF +
     "                        ('energy_renewable_site_limited_hydron3', 'Hoth Hydron-3 Renewable Energy')):" + LF),
    ("        p = next(i for i, r in enumerate(rows) if r[1] == base)" + LF +
     "        end = next((i for i in range(p + 1, len(rows)) if depth[i] <= depth[p]), len(rows))" + LF,
     "        p = next((i for i, r in enumerate(rows) if r[1] == base), None)" + LF +
     "        if p is None:   # no class row (the site-limited energies): after the last leaf named <base>_<planet>" + LF +
     "            end = max(i for i, r in enumerate(rows) if r[1].startswith(base + '_')) + 1" + LF +
     "        else:" + LF +
     "            end = next((i for i in range(p + 1, len(rows)) if depth[i] <= depth[p]), len(rows))" + LF),
], B)
wr(B, builder)

# ---------------------------------------------------------------- the pools
L = 'MMOCoreORB/bin/scripts/managers/resource_manager.lua'
lua = edited(rd(L), [
    ('for _, hothType in ipairs({"steel_hoth", "iron_hoth", "aluminum_hoth", "copper_hoth", "ore_extrusive_hoth", "ore_intrusive_hoth",' + LF +
     '\t\t"radioactive_hoth", "gas_reactive_hoth", "petrochem_fuel_liquid_hoth", "petrochem_fuel_solid_hoth"}) do' + LF +
     '\ttable.insert(minimumpoolincludes, {hothType, 1})' + LF + 'end' + LF,
     'for _, hothType in ipairs({"steel_hoth", "iron_hoth", "aluminum_hoth", "copper_hoth", "ore_extrusive_hoth", "ore_intrusive_hoth",' + LF +
     '\t\t"radioactive_hoth", "gas_reactive_hoth", "petrochem_fuel_liquid_hoth", "petrochem_fuel_solid_hoth",' + LF +
     '\t\t-- R3 (Fable, 14 Oct 2026): MTG\'s four Hoth gem leaves (<class>_hoth_<n>; Core3 restricts them by the "_hoth" substring)' + LF +
     '\t\t"armophous_hoth_1", "armophous_hoth_2", "crystalline_hoth_1", "crystalline_hoth_2",' + LF +
     '\t\t-- R3: Hoth\'s three site-limited energies. No stock pool spawns the site-limited energies anywhere (nativepoolincludes' + LF +
     '\t\t-- lists 42 types: solar and wind are its only energies, hence 42 natives a planet, not 45); here they are Hoth-only,' + LF +
     '\t\t-- one of each. The galaxy-wide alternative is adding the three to nativepoolincludes (+3 natives on every planet).' + LF +
     '\t\t"energy_renewable_site_limited_geothermal_hoth", "energy_renewable_site_limited_tidal_hoth", "energy_renewable_site_limited_hydron3_hoth"}) do' + LF +
     '\ttable.insert(minimumpoolincludes, {hothType, 1})' + LF + 'end' + LF),
], L)
wr(L, lua)

os.makedirs(R + '/patch', exist_ok=True)
p = subprocess.run(['diff', '-u', '--label', 'a/outputs/' + B, '--label', 'b/outputs/' + B, O + '/' + B, N + '/' + B], capture_output=True)
open(R + '/patch/h-r3-1-hoth_client_build.patch', 'wb').write(p.stdout)
p2 = subprocess.run(['diff', '-u', '--label', 'a/' + L, '--label', 'b/' + L, O + '/' + L, N + '/' + L], capture_output=True)
open(R + '/patch/core3-r3-1-hoth-pools.patch', 'wb').write(p2.stdout)
print('h patch lines', len(p.stdout.splitlines()), '| core3 patch lines', len(p2.stdout.splitlines()))
