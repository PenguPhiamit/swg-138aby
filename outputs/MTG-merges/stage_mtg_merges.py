"""stage_mtg_merges.stage_mtg_merges(stage_dir, base): give back the MTG rows that stock files hide (Claude, 15 Oct 2026;
extended to every additive file by the shadow audit, 15 Oct 2026).

The client and the server both load MTG's archives *below* stock, so when a file exists in both, stock's copy wins and
MTG's additions vanish. The owner's BARC speeder (15 Oct) spawned on the server but stayed invisible: the four mount
tables and the monster names come from stock (patch_11_02, patch_13_00), which know nothing of the BARC, while MTG's
copies (mtg_patch_022, mtg_patch_013_configurable_02) carry it. Without a saddle-appearance row the client has no body
to draw for the mount.

shadow_audit.py then compared all 125,571 files that stock and MTG both hold (shadow-audit.md). The files here are the
ones where MTG only adds: datatables with identical columns and types, string files and CRC string tables. Each becomes
base + MTG's extra entries: every base row, string or CRC entry stays as it is (rows and strings in order); MTG entries
whose key the base lacks are added, from the highest-priority MTG copy first (MTG_COPIES, client order), so a key in two
MTG copies takes the higher copy's value. Nothing MTG *edits* is applied: where MTG changes a stock value (valid_scale_range's
bantha_hue, logical_saddle_name_map's nerf_hue, five monster names), the stock value stays.

  TABLES       the four mount tables (the BARC), plus dungeon2's radar range and disabled planetary map (MTG's zone)
  STRINGS      monster_name (the BARC's name) and 74 string/en files where MTG adds keys and edits none: names and
               texts for MTG's vehicles, ships, houses, deeds, foods, badges, crafting parts, quests, UI options
  CRC_TABLES   misc/planet_crc_string_table.iff (39 MTG zone names: kashyyyk, mustafar, dungeon2-4, space zones ...)
               and misc/quest_crc_string_table.iff (1,953 MTG quests); CRCs checked against the SOE CRC of each name

base is the chain's staging base: the copy an earlier step already staged (Hoth, Ossus, species: planet CRC table,
creature names, skill and species strings), else the client's winning (stock) copy. Server notes: Core3 reads
valid_scale_range (mount training), misc/quest_crc_string_table (quest tasks) and every string/en file (the strings
database, refilled only on a new database or reloadstrings). The merged files go in local_planets.tre, which the client
loads at the top and the server first. Idempotent.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
from swgfmt import swg_tables as st, trn_iff  # noqa: E402

MTG_COPIES = ['mtg_patch_023.tre', 'mtg_patch_022.tre', 'mtg_planets.tre', 'mtg_patch_019.tre',
              'mtg_patch_013_configurable_02.tre']   # every MTG archive holding a merged file, client priority order (higher first)
TABLES = {   # file -> number of leading columns that make a row's key
    'datatables/mount/logical_saddle_name_map.iff': 1,   # sat_or_skt_name
    'datatables/mount/saddle_appearance_map.iff': 2,     # logical_saddle_name, saddle_capacity
    'datatables/mount/rider_pose_map.iff': 2,            # saddle_appearance_name, seat_index
    'datatables/mount/valid_scale_range.iff': 2,         # appearance_name, saddle_capacity
    'datatables/planetary_map/disabled_planetary_map.iff': 1,   # Planet (+ dungeon2, like stock's dungeon1)
    'datatables/radar/radar_range.iff': 1,               # Planet (+ dungeon2, like stock's dungeon1)
}
STRINGS = [
    'string/en/monster_name.stf',
    'string/en/badge_d.stf',
    'string/en/badge_n.stf',
    'string/en/building_detail.stf',
    'string/en/building_lookat.stf',
    'string/en/craft_armor_ingredients_n.stf',
    'string/en/craft_clothing_ingredients_d.stf',
    'string/en/craft_clothing_ingredients_n.stf',
    'string/en/craft_dna_components_d.stf',
    'string/en/craft_dna_components_n.stf',
    'string/en/craft_item_ingredients_d.stf',
    'string/en/craft_item_ingredients_n.stf',
    'string/en/craft_results.stf',
    'string/en/deed.stf',
    'string/en/deed_detail.stf',
    'string/en/dungeon/space_dungeon.stf',
    'string/en/error_message.stf',
    'string/en/event_perk_jukebox_songs.stf',
    'string/en/faction/faction_names.stf',
    'string/en/food_name.stf',
    'string/en/game_language.stf',
    'string/en/got_n.stf',
    'string/en/group.stf',
    'string/en/hyperspace_points_d.stf',
    'string/en/hyperspace_points_n.stf',
    'string/en/lair_d.stf',
    'string/en/lair_n.stf',
    'string/en/launch_names.stf',
    'string/en/mob/creature_names.stf',
    'string/en/money/acct_n.stf',
    'string/en/monster_lookat.stf',
    'string/en/npc_lookat.stf',
    'string/en/npc_name.stf',
    'string/en/obj_d.stf',
    'string/en/performance.stf',
    'string/en/pet/pet_menu.stf',
    'string/en/player/player_utility.stf',
    'string/en/player_species.stf',
    'string/en/quest/pirates.stf',
    'string/en/ship_component_n.stf',
    'string/en/ship_slot_compatabilities_d.stf',
    'string/en/ship_slot_compatabilities_n.stf',
    'string/en/ship_slot_d.stf',
    'string/en/ship_slot_n.stf',
    'string/en/sign_name.stf',
    'string/en/skl_d.stf',
    'string/en/skl_n.stf',
    'string/en/slicing/slicing.stf',
    'string/en/space/quest.stf',
    'string/en/space/scst_short_n.stf',
    'string/en/space/ship_names.stf',
    'string/en/space/space_interaction.stf',
    'string/en/space/space_item.stf',
    'string/en/space/space_mobile_type.stf',
    'string/en/space_crafting_d.stf',
    'string/en/space_crafting_n.stf',
    'string/en/space_item_n.stf',
    'string/en/space_ship.stf',
    'string/en/spacequest/quests.stf',
    'string/en/terminal_lookat.stf',
    'string/en/terminal_ui.stf',
    'string/en/texture_kit.stf',
    'string/en/theme_park/racing/racing.stf',
    'string/en/theme_park_name.stf',
    'string/en/ui_auc.stf',
    'string/en/ui_chatroom.stf',
    'string/en/ui_group_launch.stf',
    'string/en/ui_opt.stf',
    'string/en/ui_opt_sound.stf',
    'string/en/ui_planet_map.stf',
    'string/en/ui_radial.stf',
    'string/en/ui_spacehud.stf',
    'string/en/ui_text_color.stf',
    'string/en/ui_trade.stf',
    'string/en/wound_terminal.stf',
]
# 35 of the 41 string/en files where MTG also edits a few stock strings (shadow-audit.md, top item 1; Claude, 15 Oct;
# the other six only edit, so there is nothing to add):
# merge_strings adds only the keys the base lacks, so every stock text stays as it is, as in monster_name.
STRINGS += [
    'string/en/building_name.stf',
    'string/en/clientpoi_d.stf',
    'string/en/clientpoi_n.stf',
    'string/en/container_error_message.stf',
    'string/en/craft_armor_ingredients_d.stf',
    'string/en/crafting.stf',
    'string/en/crafting_detail.stf',
    'string/en/dungeon/death_watch.stf',
    'string/en/event_perk.stf',
    'string/en/food_detail.stf',
    'string/en/frn_d.stf',
    'string/en/frn_n.stf',
    'string/en/gcw.stf',
    'string/en/item_d.stf',
    'string/en/item_n.stf',
    'string/en/monster_detail.stf',
    'string/en/obj_n.stf',
    'string/en/pet_deed.stf',
    'string/en/planet_n.stf',
    'string/en/player_structure.stf',
    'string/en/quest/groundquests.stf',
    'string/en/quest_armorsmith.stf',
    'string/en/quest_item_d.stf',
    'string/en/quest_item_n.stf',
    'string/en/space/cargo.stf',
    'string/en/spacequest/escort_duty/corellia_imperial_tier4_2.stf',
    'string/en/spacequest/escort_duty/tatooine_imperial_tier4_escortduty_1.stf',
    'string/en/terminal_detail.stf',
    'string/en/terminal_name.stf',
    'string/en/theme_park_nym/messages.stf',
    'string/en/ui.stf',
    'string/en/weapon_detail.stf',
    'string/en/weapon_name.stf',
    'string/en/wearables_detail.stf',
    'string/en/wearables_name.stf',
]
CRC_TABLES = ['misc/planet_crc_string_table.iff', 'misc/quest_crc_string_table.iff']


WHOLE_FILES = {   # binary file -> the MTG copy that replaces stock's whole, with the stock names it may drop
    # The BARC rider fix (15 Oct, build_barc_ride_archive.py): stock's male animation table has no rider pose
    # vehicle_barc_speeder, so Enter did nothing. MTG's copy adds 185 names (mount poses for MTG's vehicles) and drops
    # one tumble animation and three duplicate saddle aliases whose proper names it keeps. Client only; Core3 reads no .lat.
    'appearance/lat/all_m.lat': ('mtg_patch_022.tre', {
        'appearance/animation/all_b_cbt_pistol_kneeling_ready_fire_tumble_to_pistol_standing_ready.ans',
        'saddle_body2_narrrow', 'saddle_body_1_wide', 'saddle_body_2_wide'}),
}


def merged_files():
    return sorted(list(TABLES) + STRINGS + CRC_TABLES + list(WHOLE_FILES))


def mtg_copy(name, archive):
    path = os.path.join(trn_iff.CLIENT, archive)
    return trn_iff.open_tre_entry(path, name) if name in trn_iff.list_tre(path) else None


def merge_table(name, keylen, base):
    data = base(name)
    stock = st.read_dtii(data)
    assert st.write_dtii(stock) == data, f'{name}: base does not round-trip'
    rows = [list(r) for r in stock['rows']]
    have = {tuple(r[:keylen]) for r in rows}
    added = []
    for archive in MTG_COPIES:
        copy = mtg_copy(name, archive)
        if copy is None:
            continue
        t = st.read_dtii(copy)
        assert t['columns'] == stock['columns'] and t['types'] == stock['types'], f'{name}: {archive} has other columns'
        for r in t['rows']:
            key = tuple(r[:keylen])
            if key not in have:
                rows.append(list(r))
                have.add(key)
                added.append((archive, key))
    out = st.write_dtii({'version': stock['version'], 'columns': stock['columns'], 'types': stock['types'], 'rows': rows})
    back = st.read_dtii(out)
    assert [list(r) for r in back['rows'][:len(stock['rows'])]] == [list(r) for r in stock['rows']], f'{name}: stock rows changed'
    return out, added


def merge_strings(name, base):
    data = base(name)
    stf = st.read_stf(data)
    assert st.write_stf(stf) == data, f'{name}: base does not round-trip'
    have = dict(st.stf_items(stf))
    added = []
    for archive in MTG_COPIES:
        copy = mtg_copy(name, archive)
        if not copy:   # absent, or an empty placeholder entry in a lower MTG archive
            continue
        for key, text in st.stf_items(st.read_stf(copy)):
            if key not in have:
                st.stf_add(stf, key, text)
                have[key] = text
                added.append((archive, key))
    out = st.write_stf(stf)
    back = dict(st.stf_items(st.read_stf(out)))
    assert all(back[k] == v for k, v in st.stf_items(st.read_stf(data))), f'{name}: a stock string changed'
    return out, added


def merge_crc_table(name, base):
    """CRC string table: base entries kept, MTG names the base lacks added; written in ascending CRC order (the client
    binary-searches CRCT). An MTG name whose CRC is not the SOE CRC of the name, or whose CRC another name already
    holds, stops the merge."""
    data = base(name)
    t = st.read_cstb(data)
    assert st.write_cstb(t['entries'], t['version']) == data, f'{name}: base does not round-trip'
    entries = list(t['entries'])
    names = {n for _, n in entries}
    crcs = {c: n for c, n in entries}
    added = []
    for archive in MTG_COPIES:
        copy = mtg_copy(name, archive)
        if copy is None:
            continue
        m = st.read_cstb(copy)
        assert m['version'] == t['version'], f'{name}: {archive} has table version {m["version"]}'
        for crc, n in m['entries']:
            if n in names:
                continue
            assert crc == st.soe_crc(n), f'{name}: {archive} lists {n} with CRC {crc:08x}'
            assert crc not in crcs, f'{name}: {archive} {n} collides with {crcs[crc]}'
            entries.append((crc, n))
            names.add(n)
            crcs[crc] = n
            added.append((archive, n))
    out = st.write_cstb(entries, t['version'])
    back = st.read_cstb(out)
    assert set(t['entries']) <= set(back['entries']) and len(back['entries']) == len(t['entries']) + len(added), f'{name}: base entries changed'
    return out, added


def iff_names(data):
    return set(x.decode('latin-1') for x in re.findall(rb'[a-z][a-z0-9_]*(?:/[a-z0-9_]+)*(?:\.ans)?(?=\x00)', data))


def take_whole(name, base):
    """MTG's copy replaces the base whole; it must keep every base name except the listed ones."""
    archive, may_drop = WHOLE_FILES[name]
    data, copy = base(name), mtg_copy(name, archive)
    assert copy is not None and copy[:4] == data[:4] == b'FORM' and copy[8:12] == data[8:12], f'{name}: no matching MTG copy'
    if data == copy:   # staged already (a second run)
        return copy, []
    old, new = iff_names(data), iff_names(copy)
    assert old - new == may_drop, f'{name}: MTG drops {sorted(old - new - may_drop)[:5]}'
    return copy, [(archive, n) for n in sorted(new - old)]


def stage_mtg_merges(stage_dir, base):
    report = {}
    for name, keylen in TABLES.items():
        report[name] = merge_table(name, keylen, base)
    for name in STRINGS:
        report[name] = merge_strings(name, base)
    for name in CRC_TABLES:
        report[name] = merge_crc_table(name, base)
    for name in WHOLE_FILES:
        report[name] = take_whole(name, base)
    result = {}
    for name, (out, added) in report.items():
        path = os.path.join(stage_dir, name.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(out)
        result[name] = {'added': len(added), 'from': {a: sum(1 for x, _ in added if x == a) for a in MTG_COPIES},
                        'barc_keys': [k for _, k in added if 'barc' in str(k)], 'sha256': hashlib.sha256(out).hexdigest()}
    return result


if __name__ == '__main__':
    print(__doc__)
