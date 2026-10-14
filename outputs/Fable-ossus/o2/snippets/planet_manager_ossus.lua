ossus = {
	-- Sandbox: Ossus (Fable batches O1/O2, 14 Oct 2026; outputs/Fable-ossus/). Our own terrain (terrain/ossus.trn) and
	-- snapshot (snapshot/ossus.ws) in local_planets.tre; the Knossa starport sits on the flattened pad at 0 -3600 (50.3 m).
	-- Reached from Corellia (datatables/travel/travel.iff, placeholder fare).
	weatherEnabled = 1,
	gcwEnabled = 1,

	planetTravelPoints = {
		-- the outpost_starport landing pad: the same offset from the building as Hoth and Yavin IV (yaw 180)
		{name = "Knossa", x = 20.3, z = 50.3, y = -3582.2, interplanetaryTravelAllowed = 1, incomingTravelAllowed = 1, landingRange = 3},
	},

	badgeAreas = {
	},

	navAreas = {
		{"ossus_knossa", 0, -3600, 150},
	},

	planetObjects = {
	}
}
