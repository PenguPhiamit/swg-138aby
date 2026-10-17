-- One item, so createLoot() hands over exactly the ghostfire crystal (Ossus ghostfire quest, 17 Oct 2026).

ossus_ghostfire_crystal = {
	description = "",
	minimumLevel = 0,
	maximumLevel = 0,
	lootItems = {
		{itemTemplate = "ossus_ghostfire_crystal", weight = 10000000}
	}
}

addLootGroupTemplate("ossus_ghostfire_crystal", ossus_ghostfire_crystal)
