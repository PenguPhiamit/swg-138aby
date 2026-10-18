# Vendor Mechanics Report (Core3 / Pre-CU)

## 1. Short Answer

Based on VendorManager.cpp and VendorDataComponent.cpp, a vendor is a TangibleObject that uses the AuctionManager system to track items for sale. The owner registers it on the planetary map by selecting a category from a SUI list box (VendorManager.cpp:362-388). Maintenance is paid via an SUI input box where the player enters a credit amount; the server deducts from bank/cash credits and adds to the vendor's maintenance pool (VendorDataComponent.cpp:453-516). When the maintenance pool empties, the vendor's condition degrades at 15 cr/hr base rate (reduced by merchant skills), and after 100 days on strike it is destroyed (VendorDataComponent.cpp:393-411). The files do not show how to initially place a vendor, stock items with prices, or how another player buys from it.

## 2. How It Works

### Registration on the Planetary Map

**Server initiates:**
- `VendorManager::sendRegisterVendorTo` (line 362) sends a SUI list box (`SuiWindowType::STRUCTURE_VENDOR_REGISTER`) with prompt title `@player_structure:vendor_mapcat_t` and text `@player_structure:vendor_mapcat_d`.
- The list contains 13 category items: armor, clothing, components, droids, equipment, food, housing, medical, pets, resources, ships, tools, weapons (lines 371-383).

**Client responds:**
- Player selects a category index from the SUI list box.

**Server processes (`handleRegisterVendorCallback`, line 390):**
1. Checks vendor has a zone (line 394).
2. Validates vendor has VendorDataComponent (lines 397-406).
3. **Refusal check:** If `vendorData->isEmpty()` returns true, sends system message `"You cannot register an empty vendor."` and returns (lines 409-412).
4. Looks up planet map category "vendor" and subcategory `"vendor_" + selectedCategoryName` via TemplateManager (lines 414-415). If either is null, silently returns (line 417-418).
5. Sets vendor's planet map category and subcategory (lines 422-423).
6. Sets `vendorData->registered = true` (line 424).
7. Calls `zone->registerObjectWithPlanetaryMap(vendor)` to register on the map (line 426).
8. Sends system message `@player_structure:register_vendor_not` (line 428).

**Bot confirmation:** Check that vendor's planet map category/subcategory are set, `vendorData->registered` is true, and the system message appears.

### Paying Maintenance

**Server initiates:**
- `VendorDataComponent::payMaintanence` (line 453) sends a SUI input box (`SuiWindowType::STRUCTURE_VENDOR_PAY`) with prompt title `@player_structure:pay_vendor_t` and text `@player_structure:pay_vendor_d`. The input has a force-close distance of 5m (line 466).

**Client responds:**
- Player enters an integer amount in the SUI input box.

**Server processes (`handlePayMaintanence`, line 474):**
1. **Refusal check:** If value > 100,000, sends `@player_structure:vendor_maint_invalid` (lines 483-486).
2. **Refusal check:** If value <= 0, sends `@player_structure:amt_greater_than_zero` (lines 488-491).
3. Checks if owner has enough credits (`bankCredits + cashCredits >= value`) (line 493).
4. If sufficient:
   - Deducts from bank first if bank > value, otherwise deducts all bank then cash (lines 494-506).
   - Adds to `maintAmount` (lines 496, 501, 506).
   - Sends system message `@player_structure:vendor_maint_accepted` with the new maint amount as %DI (lines 509-511).
5. If insufficient credits: sends `@player_structure:vendor_maint_denied` (line 514).

**Bot confirmation:** Check owner's credit balance decreased by the paid amount, vendor's `maintAmount` increased, and the success system message appears.

### Withdrawing Maintenance

**Server initiates:**
- `VendorDataComponent::withdrawMaintanence` (line 518) sends a SUI input box (`SuiWindowType::STRUCTURE_VENDOR_WITHDRAW`) with prompt title `@player_structure:withdraw_vendor_t` and text `@player_structure:withdraw_vendor_d`.

**Client responds:**
- Player enters an integer amount.

**Server processes (`handleWithdrawMaintanence`, line 539):**
1. **Refusal check:** If value > maintAmount, sends `@player_structure:vendor_withdraw_fail` with the attempted amount as %DI (lines 548-553).
2. **Refusal check:** If value <= 0, sends `@player_structure:amt_greater_than_zero` (lines 555-558).
3. If valid: deducts from maintAmount, adds to owner's bank credits, sends `@player_structure:vendor_withdraw` with the withdrawn amount as %DI (lines 560-568).

**Bot confirmation:** Check maintAmount decreased, owner's bank credits increased, and the success system message appears.

### Vendor Status Display

**Server initiates:**
- `VendorManager::handleDisplayStatus` (line 68) sends a SUI list box (`SuiWindowType::STRUCTURE_VENDOR_STATUS`) with title `@player_structure:vendor_status` and text "Vendor Status".

**Menu items displayed (lines 100-172):**
- Owner name
- Condition percentage
- Maintenance pool amount in credits and time remaining
- Maintenance rate in cr/hr
- Number of items for sale (counted from AuctionsMap)
- Whether vendor search is enabled/disabled (`@player_structure:vendor_search_enabled` or `vendor_search_disabled`)
- If not on strike and not empty: green text "Vendor Operating Normally."

**Bot confirmation:** Check the SUI list box content matches expected values.

### Maintenance Rate Calculation

`VendorDataComponent::getMaintenanceRate` (line 429):
- Base rate: 15 cr/hr (line 435).
- Skill reduction: if owner has `crafting_merchant_master`, multiply by 0.60; if `crafting_merchant_sales_02`, multiply by 0.80 (lines 440-443).
- If registered on map, add 6 cr/hr (lines 447-448).

**Example:** Registered vendor with no merchant skills: 15 + 6 = 21 cr/hr. Master merchant, not registered: 15 * 0.60 = 9 cr/hr.

### Vendor Condition and Destruction

`VendorDataComponent::runVendorUpdate` (line 319) runs periodically:
- Deducts maintenance from maintAmount based on hours since last update (line 347).
- If maintAmount < 0, sets condition damage to `-maintAmount` (lines 349-350); vendor is "on strike".
- If maintAmount >= 0, resets condition damage and max condition to 1000 (lines 351-354).

**Empty vendor handling:**
- If `isEmpty()` returns true:
  - After `EMPTYWARNING` days without items, sends mail `@auction:vendor_status_endangered` (lines 362-368).
  - After `EMPTYDELETE` (28 days) without items, sends mail `@auction:vendor_status_deleted` and calls `VendorManager::destroyVendor` (lines 380-386).

**On-strike vendor handling:**
- If on strike: unregisters from map if registered, disables vendor search (lines 394-398).
- After `DELETEWARNING` (100 days) on strike: sends mail and destroys vendor (lines 400-411).

### Destroying a Vendor

**Server initiates:**
- `VendorManager::promptDestroyVendor` (line 207) sends a SUI message box (`SuiWindowType::STRUCTURE_DESTROY_VENDOR_CONFIRM`) with title `@player_structure:destroy_vendor_t` and text `@player_structure:destroy_vendor_d`, with Yes/No buttons.

**Client responds:**
- Player clicks Yes or No.

**Server processes (`destroyVendor`, line 250):**
1. Validates vendor has VendorDataComponent (lines 251-261).
2. Exports transaction log with vendor state (lines 281-343).
3. If registered, unregisters from planetary map (lines 345-347).
4. Sets `destroyStartedTime` and destroys the object from world and database (lines 352-355).
5. Deletes terminal items from AuctionsMap (line 359).

**Bot confirmation:** Check vendor is no longer in the world, items are returned to owner's inventory or deleted, and transaction log exists.

### Renaming a Vendor

**Server initiates:**
- `VendorManager::promptRenameVendorTo` (line 237) sends a SUI input box (`SuiWindowType::STRUCTURE_NAME_VENDOR`) with title `@player_structure:name_t` and text `@player_structure:name_d`, pre-filled with current custom name.

**Client responds:**
- Player enters a new name.

**Server processes (`handleRenameVendor`, line 462):**
1. **Refusal check:** If name is invalid (via `isValidVendorName`), sends `@player_structure:obscene` and re-prompts (lines 471-475).
2. Sets custom object name to `"Vendor: " + name` (line 491).
3. If vendor was registered, unregisters it and sends `@player_structure:vendor_rename_unreg`; otherwise sends `@player_structure:vendor_rename` (lines 494-501).

**Bot confirmation:** Check vendor's custom object name changed, and the appropriate system message appears.

### Vendor Search Toggle

`VendorDataComponent::setVendorSearchEnabled` (line 571):
- Sets `vendorSearchEnabled` flag.
- Calls `auctionManager->updateVendorSearch(vendor, enabled)` to update the search index.

**Bot confirmation:** Check `vendorSearchEnabled` flag and that the vendor appears/disappears in search results.

## 3. What a Bot Test Should Check

### Setup Required Before Testing

1. **Owner must exist:** The vendor's `ownerId` must be set to a valid player object ID (VendorDataComponent.cpp:25, 438-440).
2. **Vendor must be in a zone:** Many operations check `vendor->getZone() != nullptr` and fail silently if null (e.g., VendorManager.cpp:394, 468).
3. **Owner must have credits:** Maintenance payment requires `bankCredits + cashCredits >= value` (VendorDataComponent.cpp:493).
4. **Vendor must not be empty for registration:** Registration refuses empty vendors (VendorManager.cpp:409-412).

### Observable Results to Check

**Registration:**
- System message `@player_structure:register_vendor_not` appears.
- `vendorData->registered` becomes true.
- Vendor appears on planetary map (check via server-side query if possible).
- SUI list box contains 13 category items with correct string IDs.

**Maintenance Payment:**
- Owner's bank/cash credits decrease by the paid amount.
- `vendorData->maintAmount` increases by the paid amount.
- System message `@player_structure:vendor_maint_accepted` appears with new maint amount.
- If value > 100,000: system message `@player_structure:vendor_maint_invalid`.
- If value <= 0: system message `@player_structure:amt_greater_than_zero`.
- If insufficient credits: system message `@player_structure:vendor_maint_denied`.

**Maintenance Withdrawal:**
- `vendorData->maintAmount` decreases by withdrawn amount.
- Owner's bank credits increase by withdrawn amount.
- System message `@player_structure:vendor_withdraw` appears with withdrawn amount.
- If value > maintAmount: system message `@player_structure:vendor_withdraw_fail`.

**Status Display:**
- SUI list box shows correct owner name, condition %, maintenance pool, rate, items for sale count, and search status.
- Maintenance rate calculation matches expected formula (base 15 cr/hr minus skill reduction plus 6 if registered).

**Destruction:**
- Vendor object is removed from world and database.
- Items are exported to transaction log.
- If registered, vendor is unregistered from planetary map.

### SUI Window Types Used

| Action | SuiWindowType | Prompt Title String ID | Prompt Text String ID |
|--------|---------------|------------------------|----------------------|
| Register | STRUCTURE_VENDOR_REGISTER | @player_structure:vendor_mapcat_t | @player_structure:vendor_mapcat_d |
| Pay Maintenance | STRUCTURE_VENDOR_PAY | @player_structure:pay_vendor_t | @player_structure:pay_vendor_d |
| Withdraw | STRUCTURE_VENDOR_WITHDRAW | @player_structure:withdraw_vendor_t | @player_structure:withdraw_vendor_d |
| Rename | STRUCTURE_NAME_VENDOR | @player_structure:name_t | @player_structure:name_d |
| Destroy Confirm | STRUCTURE_DESTROY_VENDOR_CONFIRM | @player_structure:destroy_vendor_t | @player_structure:destroy_vendor_d |
| Status | STRUCTURE_VENDOR_STATUS | @player_structure:vendor_status | "Vendor Status" (literal) |

## 4. Likely Reasons a Test Sees No Effect

1. **Vendor has no zone:** Many operations silently return if `vendor->getZone() == nullptr` (e.g., VendorManager.cpp:394, 468; VendorDataComponent.cpp:575). The vendor must be placed in a valid zone/cell.

2. **Owner is null or not a player creature:** Operations that access the owner check `owner == nullptr || !owner->isPlayerCreature()` and return silently (e.g., VendorManager.cpp:95; VendorDataComponent.cpp:329, 438). The ownerId must reference a valid player object.

3. **Vendor is empty during registration:** Registration refuses empty vendors with the message "You cannot register an empty vendor." (VendorManager.cpp:409-412). Items must be added to the vendor's auction terminal before registration.

4. **Insufficient credits for maintenance:** Payment fails silently if `bankCredits + cashCredits < value` (VendorDataComponent.cpp:493-515). The owner must have enough credits.

5. **Invalid name during rename:** If `isValidVendorName` returns false, the server sends `@player_structure:obscene` and re-prompts (VendorManager.cpp:471-475). The name manager may reject certain names.

6. **Planet map category/subcategory not found:** Registration silently returns if TemplateManager cannot find "vendor" category or `"vendor_" + categoryName` subcategory (VendorManager.cpp:417-418). The template must exist in the game data.

7. **Vendor already destroyed or being destroyed:** Operations check `data->get()->isVendorData()` and return if false (e.g., VendorManager.cpp:76; VendorDataComponent.cpp:210). A vendor in the process of being destroyed may fail these checks.

8. **Force-close distance exceeded:** SUI input boxes for maintenance have a 5m force-close distance (VendorDataComponent.cpp:466, 531). If the player moves too far, the SUI closes without sending a value.

## 5. Open Questions

The provided files do not answer the following:

1. **How to place/create a vendor:** Neither file shows how a player initially creates or places a vendor object in the world. This likely involves a radial menu command and server-side object creation, but the relevant code is not in these files.

2. **How to stock items with prices:** The files reference AuctionManager and AuctionsMap for managing items for sale (e.g., VendorManager.cpp:135-160), but do not show how a player adds items to the vendor's terminal or sets prices. This is likely handled by a separate auction terminal component or radial menu callback.

3. **How another player buys from a vendor:** The files show that vendors use the AuctionItem system (VendorManager.cpp:146-158), but do not show the buyer-side interaction—how a customer opens the vendor's inventory, selects items, pays credits, and receives items. This is likely in AuctionManager or a separate buying component.

4. **What `isEmpty()` checks:** VendorDataComponent.cpp:356 calls `isEmpty()` but the implementation is not in this file (likely in a base class like AuctionTerminalDataComponent).

5. **Constants values:** Several constants are used but not defined in these files: `VENDORCHECKDELAY`, `VENDORCHECKINTERVAL`, `EMPTYWARNING`, `EMPTYDELETE`, `DELETEWARNING`, `DESTROYWINDOWMS`. Their values are needed for accurate timing tests.

6. **Radial menu IDs:** The files reference SUI windows but do not show which radial menu commands or IDs trigger vendor actions (place, stock, register, pay, etc.). This is likely in a separate radial menu configuration file or Lua script.

7. **Vendor item template:** The specific template name or object type for a vendor terminal is not mentioned. The vendor must be a TangibleObject with VendorDataComponent attached, but the creation process is opaque.

8. **Transaction log verification:** While transaction logs are created (e.g., VendorManager.cpp:281-343), there is no guidance on how to verify them in a bot test or where they are stored.
