"""Ordinary equipment commands only, existing test Esk crew; no provisioning."""
GROUP = 'Esk'


def run(g):
    for name in ('Esk', 'Tovan'):
        bot = g[name]
        inv = bot.inventory()
        own = inv.get('self')
        if not g.check(name + ': ownership known', bool(own) and inv.get('ok')):
            return
        armor = {}
        for item in inv.get('items', []):
            if 'armor_composite' in str(item.get('name')):
                # Prefer an already worn duplicate; never equip every duplicate.
                key = item['name']
                if key not in armor or item.get('parent') == own:
                    armor[key] = item
        for item in armor.values():
            if item.get('parent') != own:
                bot.slash('transferItemArmor', f'{own} 4 0 0 0', target=item['oid'], wait=1)
        final = bot.inventory()
        worn = [i['name'] for i in final.get('items', [])
                if 'armor_composite' in str(i.get('name')) and i.get('parent') == own]
        g.check(name + ': all supplied composite pieces worn', len(set(worn)) == len(armor) and bool(armor),
                {'worn': worn, 'supplied_unique': len(armor)})
        g.note(name + ': post-equipment HAM: ' + str(bot.status().get('me', {})))
    g.note('No armor statistics, encumbrance limits or skills changed by this verification.')
