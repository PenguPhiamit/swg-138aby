# Player Cities in Core3 (SWGEmu)

## 1. Short Answer

In Core3, a player city is founded by using a City Hall deed that creates a new CityRegion object with OUTPOST rank as the starting point. The mayor must have citizens join the city within a grace period (`newCityGracePeriod` minutes from Lua config), or the zoning permit is rejected and the City Hall destroyed. Cities rank up when citizen count meets thresholds defined in `CitizensPerRank` from `scripts/managers/city_manager.lua`, and rank down via `contractCity` when citizens fall below minimums. Players join/leave as citizens through city terminal interactions. Taxes are managed by the mayor at the City Management terminal, requiring the `manage_taxes` ability and city rank 2+. Cities are only allowed on planets listed in the `CitiesAllowed` Lua table; Hoth and Ossus have no entry, so they forbid all cities.

## 2. How It Works

### City Founding
- The server creates a new `CityRegion` via `createCity(CreatureObject* mayor, const String& cityName, float x, float y)` (line 196).
- The city starts at rank OUTPOST (line 204).
- A grace period is scheduled: `city->scheduleCitizenAssessment(newCityGracePeriod * 60)` (line 210), where `newCityGracePeriod` is loaded from Lua config (line 115).
- During the grace period, citizens must register. The assessment runs via `assessCitizens(CityRegion* city)` (line 688): if `citizens < citizensPerRank.get(0)` (line 711), the City Hall is destroyed and a "Zoning Permits Rejected" mail is sent (lines 713-717). If approved, a "New City Approved!" mail is sent (lines 733-737).
- The mayor receives a "New City Established!" mail (line 218).

### Citizens Joining and Leaving
- `registerCitizen(CityRegion* city, CreatureObject* creature)` (line 1411) adds the player to the city's CitizenList via `city->addCitizen(creature->getObjectID())` (line 1439).
- The mayor receives a "City Growth: Added Citizen" mail (lines 1423-1428).
- The new citizen receives a "Welcome, Citizen!" mail (lines 1430-1436).
- `unregisterCitizen(CityRegion* city, CreatureObject* creature)` (line 1442) removes the player via `city->removeCitizen(creature->getObjectID())` (line 1461).
- The mayor receives a "Lost Citizen!" mail (lines 1454-1458).

### City Ranking Up and Down
- Ranks are: OUTPOST, VILLAGE, TOWNSHIP, CITY, METROPOLIS (inferred from rank comparisons in code).
- `expandCity(CityRegion* city)` (line 1321) advances the city if `citizens >= citizensPerRank.get(cityRank)` (line 799).
- If the planet's `CitiesAllowed` table caps at that rank, expansion is blocked and structures are destroyed for the new rank (lines 1348-1358).
- `contractCity(CityRegion* city)` (line 1263) reduces rank when citizens fall below `citizensPerRank.get(cityRank - 1)` (line 792).
- If citizens drop below `citizensPerRank.get(0)`, the city reverts to OUTPOST and a new assessment starts with `oldCityGracePeriod` (lines 1267-1272).
- Radius changes via `radiusPerRank` from Lua config (line 50, loaded at line 140).
- Maintenance discount is applied: `maintenanceDiscount * structureTemplate->getCityMaintenanceAtRank(city->getCityRank() - 1)` (line 867).

### City Terminal and Taxes
- Mayors adjust taxes via `promptAdjustTaxes` (line 1852), which requires the `manage_taxes` ability (line 1858) and city rank >= VILLAGE (line 1863).
- A SuiListBox shows available tax types from `cityTaxes` Lua config (lines 1875-1878).
- `setTax(CityRegion* city, CreatureObject* mayor, int selectedTax, int value)` (line 1921) validates the value against `cityTax->getMinValue()` and `cityTax->getMaxValue()` (line 1927), then applies it via `city->setTax(selectedTax, value)` (line 1934).
- A system message confirms the tax change (lines 1938-1941), and an email is sent to all citizens (lines 1945-1948).
- Income tax is collected via `processIncomeTax` (line 820), sending mail to each citizen.
- Maintenance is deducted in `deductCityMaintenance` (line 851), paying for City Hall, civic structures, decorations, trainers, mission terminals, map registration (5000 credits if registered), and specialization costs.

### Planets Allowing Cities
- `isCityRankCapped(const String& planetName, byte rank)` (line 225) checks the `CitiesAllowed` Lua table loaded at line 72.
- If a planet has no entry in `CitiesAllowed`, it allows no cities (inferred from comment at line 228-229 and the guard check).
- The test galaxy forbids cities on Hoth and Ossus because they lack a `CitiesAllowed` row.

## 3. What a Bot Test Should Check

### Setup
- Ensure the test planet has an entry in `CitiesAllowed` Lua config (not Hoth/Ossus).
- Have the bot character use a City Hall deed at a valid location (not within 1024 meters of another city, per line 369).

### Observable Results
1. **City creation**: After using the deed, check for:
   - A "New City Established!" mail to the mayor (line 218).
   - A new CityRegion object created and persisted (line 198).
   - The city at OUTPOST rank (line 204).

2. **Citizen registration**: After citizens register:
   - Mayor receives "City Growth: Added Citizen" mail (lines 1423-1428).
   - New citizen receives "Welcome, Citizen!" mail (lines 1430-1436).
   - `city->getCitizenCount()` increases.

3. **City approval**: After grace period expires with enough citizens:
   - Mayor receives "New City Approved!" mail (lines 733-737).
   - `city->hasAssessmentPending()` becomes false (line 739).

4. **Rank advancement**: When citizen count meets next rank threshold:
   - During next city update, mayor receives "City Expansion!" mail (lines 1342-1354).
   - City radius increases per `radiusPerRank` (line 1361).
   - New structures become available at higher ranks.

5. **Tax management**: Mayor uses City Management terminal:
   - SuiListBox with tax options appears (lines 1868-1878).
   - After setting a tax, system message confirms the value (lines 1938-1941).
   - All citizens receive an email about the tax change (lines 1945-1948).

### Checks That Refuse Actions
- **Too close to another city**: "city_too_close" system message (line 370-373).
- **Invalid city name**: `validateCityName` returns false if name already exists (lines 386-393).
- **No manage_taxes ability**: "You lack the knowledge to manage the city's taxes." (line 1859).
- **City rank < VILLAGE for taxes**: "Your city must be at least rank 2 to levy taxes." (line 1864).
- **Treasury too low for withdrawal**: "There isn't any money to transfer!" (line 550).
- **Withdrawal cooldown**: "You may only withdraw from the city treasury once per day." (line 528).
- **No zoning skill**: "You must be a Politician to enable city zoning." (line 2421).

### Log/Bot Confirmation Line
- Check `city->getCitizenCount()` after registration.
- Verify `city->getCityRank()` after expansion/contraction.
- Confirm treasury balance via `city->getCityTreasury()`.
- Check mayor's cooldowns: `mayor->checkCooldownRecovery("city_withdrawal")` (line 527).

## 4. Likely Reasons a Test Sees No Effect

1. **Wrong planet**: Testing on Hoth or Ossus, which lack `CitiesAllowed` entries and forbid all cities (inferred from line 228-229).
2. **Grace period not elapsed**: The city assessment hasn't run yet; `newCityGracePeriod` minutes must pass before approval/rejection.
3. **Insufficient citizens**: City starts at OUTPOST rank requiring `citizensPerRank.get(0)` minimum citizens to survive assessment (line 711).
4. **Cooldown on withdrawal**: Mayor has a `city_withdrawal` cooldown preventing treasury access (line 527).
5. **Missing abilities**: Player lacks `manage_taxes`, `city_map`, or `social_politician_novice` skills required for specific actions.
6. **Planet rank cap reached**: `isCityRankCapped` returns true if the planet's max cities at that rank is reached (line 253).
7. **Treasury insufficient for maintenance**: City treasury drops below required amount, causing structures to decay or city to unregister (lines 913-919, 928-936).

## 5. Open Questions

1. **City Hall deed handling**: The file shows `createCity` is called but not the deed's radial menu trigger or inventory item logic. Missing: which deed template triggers this and what client actions (radial id, packet) initiate it.
2. **Lua config values**: `scripts/managers/city_manager.lua` defines `CitizensPerRank`, `RadiusPerRank`, `CitiesAllowed`, `CityTaxes`, `CitySpecializations`, and timing constants, but the actual values are not in this file. Need that Lua script for exact numbers.
3. **Client-side city terminal interaction**: The file shows SUI windows opened by the server (e.g., `SuiListBox` at line 1868), but not which radial menu IDs or client packets trigger `promptAdjustTaxes`, `registerCitizen`, etc. Missing: callback mappings in AgentControl.cpp or radial menu definitions.
4. **City region radius calculation**: `radiusPerRank.get(OUTPOST - 1)` (line 206) uses rank-1 as index; need to confirm OUTPOST = 1 and the actual radius values from Lua config.
5. **How citizens register via client**: The server function `registerCitizen` exists, but the client action (terminal interaction, command, or radial option) that calls it is not in this file.
