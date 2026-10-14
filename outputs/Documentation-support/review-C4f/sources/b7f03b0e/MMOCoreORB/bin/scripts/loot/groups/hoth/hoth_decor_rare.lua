-- Adapted from Bellum Gero (github.com/Miphstoe/BellumGero-Live, revision 1f4438a1, AGPL-3.0),
-- MMOCoreORB/bin/scripts/loot/groups/bellum/hoth/hoth_decor_rare.lua. Ported to this server 14 Oct 2026 (Claude; see outputs/Documentation-support/hoth-port-log.md).
-- Cut to the 3 of 13 items whose objects our client has; equal weights.

hoth_decor_rare = {
	description = "",
	minimumLevel = 0,
	maximumLevel = 0,
	lootItems = {
		{itemTemplate = "hoth_decor_col_reward_hoth_tauntaun_head", weight = 3333333},
		{itemTemplate = "hoth_decor_diorama_atat_attack", weight = 3333333},
		{itemTemplate = "hoth_decor_tauntaun_armored_statue", weight = 3333334}
	}
}

addLootGroupTemplate("hoth_decor_rare", hoth_decor_rare)
