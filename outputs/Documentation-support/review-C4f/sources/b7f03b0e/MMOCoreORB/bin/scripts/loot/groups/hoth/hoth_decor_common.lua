-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/loot/groups/bellum/hoth/hoth_decor_common.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Cut to the 4 of 18 items whose objects our client has; equal weights.

hoth_decor_common = {
	description = "",
	minimumLevel = 0,
	maximumLevel = 0,
	lootItems = {
		{itemTemplate = "hoth_decor_frn_plush_tauntaun", weight = 2500000},
		{itemTemplate = "hoth_decor_decorative_stuffed_tauntaun", weight = 2500000},
		{itemTemplate = "hoth_decor_decorative_stuffed_wampa", weight = 2500000},
		{itemTemplate = "hoth_decor_decorative_hoth_travel_advertisement", weight = 2500000}
	}
}

addLootGroupTemplate("hoth_decor_common", hoth_decor_common)
