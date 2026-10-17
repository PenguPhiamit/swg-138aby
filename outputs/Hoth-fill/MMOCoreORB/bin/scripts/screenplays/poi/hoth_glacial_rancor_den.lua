-- Hoarfang's den: the glacial rancor in one fixed place with a respawn timer (owner, 15 Oct, Hoth Q4).
-- Site: the Glacial Rancor Grounds, a flat glacial valley south of the outpost (outputs/Fable-hoth-mapnames/sites.tsv,
-- ground 11-28 m within 100 m; terrain height 26.4 m at the spawn point). The owner picks the final site; see
-- outputs/Hoth-leftovers/LEFTOVERS-INSTALL.md. Claude, 17 Oct 2026.
-- Owner, 17 Oct (Hoth fill): keep this site and the Chiss blue, respawn 2 hours (7200 s), and lower drop rates.

HothGlacialRancorDenScreenPlay = ScreenPlay:new {
	numberOfActs = 1,

	screenplayName = "HothGlacialRancorDenScreenPlay",

	x = 600, z = 26.4, y = -4600, heading = 180,
	respawn = 7200,
}

registerScreenPlay("HothGlacialRancorDenScreenPlay", true)

function HothGlacialRancorDenScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		spawnMobile("hoth", "hoth_glacial_rancor", self.respawn, self.x, self.z, self.y, self.heading, 0)
	end
end
