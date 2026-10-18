# Weather System Report

## 1. Short Answer

Weather changes automatically per planet based on Lua configuration (weatherStability, averageWeatherDuration). It affects gameplay only when hasDamagingSandstorms is enabled and weather reaches EXTREMESTORM (ID 4), causing damage to HAM bars, blind state, and knockdown chance. The /server weather command (admin-only) can enable/disable/change weather or show info. Most planets default to sunny weather with varying stability values.

## 2. How It Works

### Weather IDs
- 0 = CLEAR, 1 = LIGHTSTORM, 2 = STORM, 3 = HEAVYSTORM, 4 = EXTREMESTORM (WeatherManager.idl:18-22)

### Per-Planet Configuration (weather_manager.lua)
Each planet has these settings:
- **defaultWeather**: Starting weather ID (0=sunny, 1=light storm/rain/snow; Hoth defaults to 1, Nal Hutta defaults to 1) (lua:61-64, lua:236, lua:264)
- **averageWeatherDuration**: How long each weather pattern lasts. Default is 3600 seconds (1 hour) (WeatherManagerImplementation.cpp:98). Actual duration formula: `(System::random(averageWeatherDuration) + (averageWeatherDuration / 2)) / (baseWeather + 1)` (WeatherManagerImplementation.cpp:120)
- **weatherStability**: 0-100, higher means less volatile weather. Affects probability of choosing each weather ID (lua:66-83). For example, stability 95 gives 96% chance of CLEAR, while stability 60 gives 68% CLEAR, 20% LIGHTSTORM, etc.
- **hasDamagingSandstorms**: Optional feature, only on Tatooine and Lok (lua:125, lua:178). Hoth has it set to 0 with a comment about cold text not being implemented yet (lua:242)
- **sandstormDamage**: Damage per tick when hasDamagingSandstorms is enabled. Default 70 for Tatooine, 50 for Lok (lua:96-98, lua:127, lua:180)

### Sandstorm Effects (only when hasDamagingSandstorms=1 AND currentWeather==EXTREMESTORM/4)
- **Blind state**: Player is blinded for 60 seconds (WeatherManagerImplementation.cpp:187)
- **HAM damage**: Damage applied to HEALTH, ACTION, and MIND bars equal to `sandstormDamage - totalCoverings` (WeatherManagerImplementation.cpp:193-198)
- **Knockdown chance**: 1% chance per tick (`System::random(200) > 198`) if applicableKDChance > 0 and player is not already prone/knocked down (WeatherManagerImplementation.cpp:202). If riding mount, dismounts first (WeatherManagerImplementation.cpp:203-206)
- **Messages**: 
  - When entering EXTREMESTORM: "The weather around you quickly becomes damaging, seek shelter immediately." (WeatherManagerImplementation.cpp:159)
  - When leaving EXTREMESTORM: "The storm has subsided." (WeatherManagerImplementation.cpp:153)

### Protection from Sandstorms
Players are exempt if: in a shelter (parentID != 0), camping (currentCamp != nullptr), or riding a mount (WeatherManagerImplementation.cpp:183).

Clothing protection values (WeatherManagerImplementation.cpp:213-287):
- Hat: +1 for specific helmets/armor
- Chest: +1 for jackets, +2 for Tusken Robes (covers chest+legs)
- Pants: +1 for specific pants or armor
- Gloves: +1 for specific gloves or armor
- Boots: +1 for specific boots or armor

### /server weather Command (WeatherCommand.h)
Requires admin level >= 15 (WeatherCommand.h:23). Syntax: `/server weather [enable/disable/info/change] [0-4]` (WeatherCommand.h:86)
- **enable**: Re-enables automatic weather changes (WeatherManagerImplementation.cpp:294)
- **disable**: Disables automatic weather, cancels change event (WeatherManagerImplementation.cpp:314)
- **change [0-4]**: Sets baseWeather directly; 5 = random from 0-4 (WeatherManagerImplementation.cpp:323-327)
- **info**: Prints current weather info including density and seed (WeatherManagerImplementation.cpp:338)

### Weather Map (Spatial Variation)
WeatherMap.h uses Simplex Noise to create spatial variation across the planet. The `getWeatherAt(x, y)` function returns a value based on position and time, which is added to baseWeather (WeatherManagerImplementation.cpp:138). The map has a lifecycle with startTime/endTime; when expired, a new pattern is created (WeatherMap.h:83-84, WeatherMap.h:56).

## 3. What a Bot Test Should Check

### Observable Results
- System messages: "The weather around you quickly becomes damaging, seek shelter immediately." and "The storm has subsided." (WeatherManagerImplementation.cpp:159, :153)
- Player state: blinded state set to 60 seconds (WeatherManagerImplementation.cpp:187)
- Player posture: KNOCKEDDOWN (WeatherManagerImplementation.cpp:209)
- HAM bar damage: HEALTH, ACTION, MIND attributes decreased by `sandstormDamage - totalCoverings` (WeatherManagerImplementation.cpp:193-197)
- Weather ID change visible via `/server weather info` command output (WeatherManagerImplementation.cpp:338)

### Required Setup
1. Planet with hasDamagingSandstorms=1 (Tatooine or Lok per lua config)
2. Force weather to EXTREMESTORM (ID 4) using `/server weather change 4`
3. Player must NOT be in a shelter, camping, or riding a mount
4. Player should wear no protective clothing to maximize damage
5. Admin level >= 15 to use /server weather command

## 4. Likely Reasons a Test Sees No Effect

- Planet does not have hasDamagingSandstorms enabled (most planets don't; only Tatooine and Lok have it in the lua config)
- Weather did not reach ID 4 (EXTREMESTORM); stability values make extreme storms rare on high-stability planets
- Player is inside a structure (parentID != 0), has an active camp, or is riding a mount (WeatherManagerImplementation.cpp:183)
- Player is wearing protective clothing that reduces or eliminates damage
- Admin level < 15 prevents using /server weather command to force EXTREMESTORM
- The WeatherMap may return 0 if outside its active time window (WeatherMap.h:83-84), causing currentWeather to be just baseWeather

## 5. Open Questions

- **Transition timing**: The lua comments mention "delayed by newWeatherTime" and "transitionTime" for gradual weather changes (lua:49-50), but these variables do not appear in the lua file or C++ code. It is unclear how the "slowly change one ID at a time" transition actually works.
- **sendWeatherTo() trigger**: The files show sendWeatherTo() sends ServerWeatherMessage packets to players, but none of these files show what event or interval triggers it to be called on connected players.
- **WeatherMap lifecycle**: When does the current WeatherMap expire and a new one get created? The code shows endTime is set at creation (WeatherMap.h:56), but the trigger for createNewWeatherPattern() beyond the weatherChangeEvent timer is unclear.
- **Skill mods**: No skill modifiers are mentioned in these files that affect sandstorm protection or damage mitigation beyond clothing CRC checks.
