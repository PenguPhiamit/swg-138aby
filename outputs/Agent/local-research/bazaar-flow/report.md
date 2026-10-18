# Report: Selling and Buying on the Bazaar (Core3)

## 1. Short Answer

In Core3, a player sells an item by sending a CreateImmediateAuctionMessage to a bazaar terminal with the item ID, vendor terminal ID, price, duration, description, and a premium flag; the server validates the vendor and calls `addSaleItem` (CreateImmediateAuctionMessageCallback.h:60). To search listings, the client sends an AuctionQueryHeadersMessage with location type, search type, item category bitmask, filters, and pagination; the server responds with AuctionQueryHeadersResponseMessage containing item names, prices, expiration times, owner/buyer info, and access fees (AuctionQueryHeadersMessageCallback.h:65, AuctionQueryHeadersResponseMessage.h:142-152). Buying an instant-sale item uses BidAuctionMessageCallback with the item ID and price; retrieving a bought item or seller credits uses RetrieveAuctionItemMessageCallback with the item ID and bazaar terminal ID (BidAuctionMessageCallback.h:47, RetrieveAuctionItemMessageCallback.h:42).

## 2. How It Works

### Selling an Item (Instant Sale)
- **Client sends** (CreateImmediateAuctionMessageCallback.h:30-41):
  - `objectID` (parseLong) – the item to sell (line 32)
  - `vendorID` (parseLong) – the bazaar terminal ID (line 33)
  - `price` (parseInt) – sale price in credits (line 35)
  - `duration` (parseInt) – how long to sell for, in seconds (line 36)
  - `description` (parseUnicode) – item description string (line 38)
  - `premium` (parseByte) – premium sale flag (line 40)

- **Server checks** (CreateImmediateAuctionMessageCallback.h:47-53):
  - Player must exist; if `player == nullptr`, the callback returns silently (line 47-48)
  - Vendor must be a valid TangibleObject that is either a vendor or bazaar terminal (`vendor->isVendor() || vendor->isBazaarTerminal()`); otherwise returns silently (line 52-53)

- **Server action** (CreateImmediateAuctionMessageCallback.h:57-60):
  - Calls `auctionManager->addSaleItem(player, objectID, vendor, description, price, duration, false, premium)` – the `false` parameter indicates this is an instant sale, not a bid auction

### Searching Listings
- **Client sends** (AuctionQueryHeadersMessageCallback.h:35-50):
  - `locationType` (parseInt) – location type identifier (line 36)
  - `counter` (parseInt) – counter value (line 37)
  - `searchType` (parseInt) – search type (line 38)
  - `itemCategory` (parseInt) – bitmask for item categories (line 39)
  - `unk1` (parseInt) – unknown field (line 41)
  - `filterText` (parseUnicode) – text filter string (line 42)
  - `unk2` (parseInt) – unknown field (line 43)
  - `minPrice` (parseInt) – minimum price filter (line 44)
  - `maxPrice` (parseInt) – maximum price filter (line 45)
  - `includeEntranceFee` (parseByte) – whether to include access fee in results (line 46)
  - `vendorID` (parseLong) – vendor terminal ID (line 48)
  - `isVendor` (parseByte) – becomes 1 when using a vendor (line 49)
  - `offset` (parseShort) – pagination offset (line 50)

- **Server action** (AuctionQueryHeadersMessageCallback.h:62-65):
  - Calls `auctionManager->getData(player, locationType, vendorID, searchType, itemCategory, filterText, minPrice, maxPrice, includeEntranceFee, counter, offset)`

- **Server response** (AuctionQueryHeadersResponseMessage.h:142-152):
  - Sends opcode `0xFA500E52` with counter and screen number (lines 24-28)
  - Location list containing vendor UIDs, owner names, and bidder names (lines 37-56)
  - Item name list as Unicode strings (lines 59-69)
  - Item info list per item (lines 72-139):
    - `itemID` (insertLong, line 94)
    - `priceStringIndex` (insertByte, line 95)
    - `price` (insertInt, line 97)
    - `expireTime` in seconds remaining: `getExpireTime() - currentTime`, clamped to 0 (lines 99-101)
    - `isAuction` flag: byte 0 for auction, byte 1 for instant sale (lines 103-106)
    - Vendor index in location list (line 108)
    - `ownerID` and owner name index (lines 110-112)
    - For auctions with status FORSALE: buyer ID is 0, bidder name index is empty string; otherwise buyer ID and bidder name index (lines 114-120)
    - Proxy value (line 122)
    - Bid/default price (line 123)
    - `itemType` (line 125)
    - `auctionOptions`: includes 0x800 (withdraw flag) if owner is viewing their own FORSALE/OFFERED items (lines 130-135)
    - `accessFee` from the building containing the vendor, or 0 (lines 83-92, 138)
  - Pagination: `offset` and `continues` flag (lines 149-151)

### Buying an Item
- **Client sends** (BidAuctionMessageCallback.h:28-31):
  - `objectid` (parseLong) – the auction item ID to buy (line 29)
  - `price1` (parseInt) – first price value (line 30)
  - `price2` (parseInt) – second price value (line 31)

- **Server action** (BidAuctionMessageCallback.h:44-47):
  - Calls `auctionManager->buyItem(player, objectid, price1, price2)` on the slowQueue task queue (lines 25, 44-47)

### Retrieving a Bought Item or Seller Credits
- **Client sends** (RetrieveAuctionItemMessageCallback.h:26-28):
  - `objectid` (parseLong) – the item ID to retrieve (line 27)
  - `bazaarid` (parseLong) – the bazaar terminal ID (line 28)

- **Server action** (RetrieveAuctionItemMessageCallback.h:41-42):
  - Calls `auctionManager->retrieveItem(player, objectid, bazaarid)`

## 3. What a Bot Test Should Check

### Setup needed before testing
- Player must have a valid CreatureObject reference (the callback checks `player == nullptr` at CreateImmediateAuctionMessageCallback.h:47)
- A valid bazaar terminal or vendor TangibleObject must exist and be accessible by its object ID (checked at CreateImmediateAuctionMessageCallback.h:52)

### Observable results to verify

**Selling:**
- System message confirming the item was listed (not visible in these files; inferred that addSaleItem produces a response)
- Item removed from player inventory or placed in auction state
- Credits deducted for listing fee (inferred; not shown in these files)

**Searching:**
- Response message with opcode `0xFA500E52` received (AuctionQueryHeadersResponseMessage.h:25)
- Item list contains expected entries with correct prices, expiration times, and owner names
- Pagination works correctly via offset/continues fields (AuctionQueryHeadersResponseMessage.h:149-151)

**Buying:**
- Credits deducted from buyer (inferred; buyItem implementation not in these files)
- Item transferred to buyer inventory or marked as sold (inferred)

**Retrieving:**
- Item appears in player inventory, or credits appear in player balance (inferred; retrieveItem implementation not visible)

### Key checks for bot validation
1. Verify the vendor is a bazaar terminal: `vendor->isBazaarTerminal()` must return true (CreateImmediateAuctionMessageCallback.h:52)
2. Verify response contains correct item data structure matching AuctionQueryHeadersResponseMessage.h:94-138
3. Verify pagination offset and continues flag work correctly (AuctionQueryHeadersResponseMessage.h:149-151)
4. Verify the isAuction byte distinguishes instant sale (1) from auction (0) at lines 103-106

## 4. Likely Reasons a Test Sees No Effect

1. **Invalid vendor ID**: If `vendorID` does not reference a TangibleObject that is a vendor or bazaar terminal, the callback returns silently with no error message (CreateImmediateAuctionMessageCallback.h:52-53). The bot must ensure the target object exists and has the correct type.

2. **Null player**: If `client->getPlayer()` returns nullptr, all callbacks return immediately without action (CreateImmediateAuctionMessageCallback.h:47, AuctionQueryHeadersMessageCallback.h:57, BidAuctionMessageCallback.h:37, RetrieveAuctionItemMessageCallback.h:34). The bot must ensure the client session is properly connected and authenticated.

3. **Null auctionManager**: If `server->getZoneServer()->getAuctionManager()` returns nullptr, no action is taken (CreateImmediateAuctionMessageCallback.h:59, AuctionQueryHeadersMessageCallback.h:64, BidAuctionMessageCallback.h:44, RetrieveAuctionItemMessageCallback.h:41). The auction manager must be initialized on the zone server.

4. **Wrong message format**: The client must send fields in the exact order specified by each callback's `parse()` method; mismatched field order or type will corrupt the parsed values.

5. **Empty CreateAuctionResponseMessage.h**: This file is empty (CreateAuctionResponseMessage.h:1-12), so there is no response message class defined for create auction operations in these files. The actual response may be handled elsewhere (inferred).

## 5. Open Questions

1. **What does `addSaleItem` do internally?** The implementation is not in these files; it is called at CreateImmediateAuctionMessageCallback.h:60 but the AuctionManager source is not provided.

2. **What does `getData` return exactly?** The AuctionQueryHeadersResponseMessage builds the response (AuctionQueryHeadersResponseMessage.h:142-152), but how the server sends it and what triggers its construction are not shown.

3. **What does `buyItem` do?** BidAuctionMessageCallback.h:47 calls it, but the implementation is missing. The price1/price2 semantics for instant sale vs auction bidding are unclear from these files alone.

4. **What does `retrieveItem` do?** RetrieveAuctionItemMessageCallback.h:42 calls it, but the implementation is not in these files. It is unclear whether this retrieves an item to inventory or credits to the seller.

5. **Missing AuctionManager.h source**: The actual auction logic (addSaleItem, getData, buyItem, retrieveItem) is in `server/zone/managers/auction/AuctionManager.h` which is included but not provided in the file list. Without it, the exact mechanics, fees, and success/failure conditions cannot be determined from these files alone.

6. **What is CreateAuctionResponseMessage for?** The file exists but is empty (CreateAuctionResponseMessage.h:1-12); its purpose is unclear.

7. **Skill requirements or mods**: These files do not show any skill checks or modifiers for using the bazaar. Such checks may exist in AuctionManager.h or elsewhere (inferred).

8. **System message string IDs**: The files do not show what system messages are sent to the player on success or failure; these would be in the AuctionManager implementation or other callbacks not provided.
