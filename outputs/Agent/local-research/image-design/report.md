# Image Designer Session Report

## 1. Short Answer

The Image Designer skill lets a player modify another player's appearance through a dual-window session initiated by targeting them. Both designer and target see an identical window with customization options for body shape, colors, hair style, and optionally a holo-emote or stat migration. The designer accepts changes to commit them; payment is taken from the target's credits. Stat migrations require both parties to be inside a SALONBUILDING and enforce a 4-minute minimum timer, while cross-player appearance changes get a 2-minute acceptance window. The session can be cancelled by timeout (default 30 seconds) or if either party leaves the salon tent.

## 2. How It Works

### Conditions to Start
- Designer must have `social_entertainer_novice` skill; otherwise they receive "@ui_imagedesigner:noskill" (ImagedesignCommand.h:30-31).
- Target cannot be dead ("@image_designer:target_dead", ImagedesignCommand.h:49-51) or invisible ("You can't image design an invisible player.", ImagedesignCommand.h:54-56).
- If designer and target differ, they must share the same group ID; otherwise "@image_designer:not_in_same_group" is shown (ImagedesignCommand.h:60-70).
- Target cannot already have an outstanding Image Design offer (ImagedesignCommand.h:91-98).
- Designer cannot already be image designing (ImagedesignCommand.h:101-107).

### Starting the Session
The command creates a new `ImageDesignSession` and calls `startImageDesign(designer, targetPlayer)` (ImagedesignCommand.h:110-112). This function:
- Records `sessionStartTime` (ImageDesignSessionImplementation.cpp:51).
- Checks if both designer and target are inside a `SALONBUILDING`; if so, enables stat migration eligibility and registers position observers to detect when either leaves (lines 56-75).
- Adds the session to both creatures' active sessions (lines 82, 95).
- Sends an `ImageDesignStartMessage` to each side with tent ID and current holoemote (lines 91-98).
- Schedules a timeout event for 30 seconds by default (ImageDesignSession.idl:108).

### The Window Both Sides See
Both designer and target receive `ImageDesignStartMessage` packets containing the same session data (designer/target object IDs, tent ID, holoemote) (ImageDesignSessionImplementation.cpp:91-98). The server does not define the window layout; that is client-side.

### What Can Change
- **Body attributes**: A VectorMap of String-to-float values sent to `updateCustomization`, which applies skill-mod checks and clamps values (ImageDesignManager.cpp:26-121, ImageDesignSessionImplementation.cpp:243-254).
- **Color attributes**: A VectorMap of String-to-uint32 values applied via `updateColorCustomization` (ImageDesignManager.cpp:219-288, ImageDesignSessionImplementation.cpp:256-261).
- **Hair style**: When `type == 1`, the server creates a new hair object from the template and customization string, validates it against the target's creature type, removes the old hair slot, and transfers the new one (ImageDesignSessionImplementation.cpp:222-241; ImageDesignManager.cpp:396-478).
- **Holo-emote**: If `holoEmote` is non-empty in ImageDesignData, it is installed via `setInstalledHoloEmote`, which also resets uses (ImageDesignSessionImplementation.cpp:284-297). The target receives "@image_designer:new_holoemote" system message.
- **Stat migration**: Only when both are inside a SALONBUILDING (`designerTentID` and `targetTentID` non-zero). A `MigrateStatsSession` is started on the target and `migrateStats()` is called (ImageDesignSessionImplementation.cpp:198-210).

### Skill Mods and Numbers
- Each customization entry has a required skill mod value stored in `customization_data.iff` (ImageDesignManager.cpp:334). The designer's current skill mod must meet or exceed it, or the change is silently skipped (ImageDesignManager.cpp:41-42, 231-232).
- XP awarded to the designer: minimum 100 for cosmetic/holo-emote changes, 300 for physical changes, 2000 for stat migration. If designer and target are the same person, XP is halved (ImageDesignSessionImplementation.cpp:268-308).

### Costs
- Payment amount comes from `requiredPayment` and `offeredPayment` in ImageDesignData; the lower of the two is charged (ImageDesignSessionImplementation.cpp:328-331).
- Credits are deducted from target's cash first, then bank if needed (lines 343-358).
- If target lacks sufficient credits, both receive error messages and the session cancels (lines 334-341).

### Timers
- **Stat migration timer**: Designer must wait at least 4 minutes from `sessionStartTime` before accepting if stat migration is requested; attempting earlier sends a bypass warning and terminates the session (ImageDesignSessionImplementation.cpp:138-171).
- **Cross-player acceptance timer**: When designer accepts but target has not, a 2-minute timeout event is scheduled (line 185: `schedule(120000)`).
- **Default session timeout**: 30 seconds from ImageDesignSession.idl line 108. If triggered and neither party left the salon nor designer accepted, both receive "Image Design session has timed out. Changes aborted." (ImageDesignSessionImplementation.cpp:393, 406).

### What Cancels the Session
- Timeout event fires (ImageDesignSessionImplementation.cpp:385-413).
- Either party leaves the SALONBUILDING; `checkDequeueEvent` detects this and cancels (lines 363-383).
- Early stat migration acceptance attempt (lines 147-170).
- Insufficient credits (lines 334-341).
- Explicit cancel by either side via `cancelSession()` (lines 27-48), which drops active sessions, removes position observers, and dequeues the timeout event.

### Messages the Player Sees
- **Start**: `ImageDesignStartMessage` to both sides (ImageDesignSessionImplementation.cpp:91-98).
- **Update**: `ImageDesignChangeMessage` sent to the "other" party on each change (line 314-317).
- **Cancel/Reject**: `ImageDesignRejectMessage` sent to both when cancelled (lines 427-433).
- **System messages**: Various text messages for errors, bypass warnings, new holo-emote congratulations, and timeout notices as cited above.

## 3. What a Bot Test Should Check

### Setup Required
1. Designer creature must have `social_entertainer_novice` skill (ImagedesignCommand.h:30).
2. Target creature must be alive and visible (lines 49-57).
3. Both creatures must be in the same group if they differ (lines 60-70).
4. For stat migration testing, both must be inside a `SALONBUILDING` (ImageDesignSessionImplementation.cpp:56-75, 198).

### Observable Results to Verify
- **System messages**: Confirm correct messages appear for skill check failure, group mismatch, dead/invisible target, insufficient credits, bypass warning, timeout, and new holo-emote.
- **Session state**: Both creatures should have `SessionFacadeType::IMAGEDESIGN` active during the session (ImageDesignSessionImplementation.cpp:82, 95). After completion or cancel, it should be dropped (lines 32, 39).
- **Inventory/attributes**: If hair changes are made, verify the old hair slot is removed and new hair object is transferred (ImageDesignManager.cpp:453, 469-475). Body/color customization variables should update on the target creature.
- **Credits**: Target's cash/bank credits decrease by the payment amount; designer's cash increases by the same (lines 343-358).
- **XP**: Designer receives XP via `PlayerManager::awardExperience` with skill "imagedesigner" (line 307). Verify correct amounts based on modification type.
- **Holo-emote**: Target's `PlayerObject` should have the new holo-emote installed (line 290).

## 4. Likely Reasons a Test Sees No Effect

1. **Missing skill**: Designer lacks `social_entertainer_novice`; command returns early with no session created (ImagedesignCommand.h:30-32).
2. **Group mismatch**: Designer and target are not in the same group; command rejects silently (lines 65-69).
3. **Target state**: Target is dead or invisible at time of targeting (lines 49-57).
4. **Salon building requirement for stat migration**: If testing stat migration but one or both parties are not inside a `SALONBUILDING`, the `designerTentID` or `targetTentID` will be zero and stat migration is disabled (lines 56-80, 198).
5. **Timer bypass protection**: Attempting to accept a stat migration before 4 minutes elapsed causes immediate cancellation with a warning (lines 138-171).
6. **Skill mod insufficient**: Designer's skill mod for the requested customization is below the required value; the change is silently skipped without error (ImageDesignManager.cpp:41-42, 231-232).
7. **Hair template incompatibility**: Hair template's `serverPlayerTemplate` does not match target's creature type; old hair is retained and no error is sent to client (ImageDesignManager.cpp:419-422).

## 5. Open Questions

1. **Meaning of the `type` parameter**: The .idl comments it as "unknown atm" (ImageDesignSession.idl:65). In implementation, `type == 1` triggers hair changes (ImageDesignSessionImplementation.cpp:225), but other values are not documented or tested.
2. **Building requirement enforcement**: ImagedesignCommand.h contains commented-out code that would require both designer and target to be inside a salon building (lines 72-89). This check is disabled, so the current behavior allows image design anywhere. It is unclear if this was intentional or incomplete.
3. **`getSkillLevel` function**: ImageDesignManager.cpp contains a fully commented-out `getSkillLevel` function (lines 291-329) that maps skill names to levels. It is not called anywhere; the current code checks individual skill mods directly. This suggests either a planned feature or leftover debugging code.
4. **Palette validation logic**: The `validatePalette` function in ImageDesignManager.cpp has commented-out palette data retrieval and skill-level-based index limits (lines 508-521). It is unclear whether palette colors are validated server-side or left entirely to the client.
5. **Missing file for palette data**: The commented code references `CustomizationIdManager::instance()->getPaletteData(paletteName)` (line 509), but there is no evidence in these files that palette data is loaded or used. The actual palette validation behavior is unclear without access to `CustomizationIdManager`.
6. **Default timeout rationale**: The 30-second default timeout (ImageDesignSession.idl:108) seems very short for a session where the client may take longer to configure changes. It is unclear if this is a safety measure, a placeholder, or if the client resets it during interaction.
