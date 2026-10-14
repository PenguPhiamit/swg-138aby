-- Mission terminals at Hoth's Scavenger Starport. Sandbox: Fable batch C (14 Oct 2026).
-- MTG's snapshot has no terminals at the outpost, so two general mission terminals stand east of the starport on
-- the flattened pad ground (0 m), facing the building. Style: screenplays/poi/dathomir_crash_site.lua; the tutorial
-- spawns its terminal with spawnSceneObject the same way. 7-argument spawnSceneObject takes the heading in radians
-- (DirectorManager::spawnSceneObject -> Quaternion::setHeadingDirection).

HothOutpostTerminalsScreenPlay = ScreenPlay:new {
	numberOfActs = 1,
	screenplayName = "HothOutpostTerminalsScreenPlay"
}

registerScreenPlay("HothOutpostTerminalsScreenPlay", true)

function HothOutpostTerminalsScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnSceneObjects()
	end
end

function HothOutpostTerminalsScreenPlay:spawnSceneObjects()
	spawnSceneObject("hoth", "object/tangible/terminal/terminal_mission.iff", 48.0, 0.0, -1996.0, 0, math.rad(-90))
	spawnSceneObject("hoth", "object/tangible/terminal/terminal_mission.iff", 48.0, 0.0, -2002.0, 0, math.rad(-90))
end
