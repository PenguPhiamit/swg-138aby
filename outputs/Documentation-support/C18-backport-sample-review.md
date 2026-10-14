# C18 — reduced backport review, 14 October 2026

Reviewed by ChatGPT: dev commits `0c44d431` and `5c7ae017`. **No new P1/P2 defect established in the reduced sample.** This is a source/data review of 30 objects and their supporting files, not acceptance of every file or approval to promote live.

## Sample and evidence

Selection is deterministic in `review-C18-sample.py`; per-object paths, client-file SHA256, staged-file SHA256, applied-commit comparisons and checks are in `C18-sample-evidence.json`:

- All 13 new wearables: eight necklaces, three pants and two rings.
- Three client-path repairs: Kashyyyk adventurer remains, Hoth elevator and Avatar technical-readout terminal.
- Four server-path repairs: an Aurebesh collection tile, NPC aero junk, a cube-loot entry and cave driftwood.
- All ten new batch-2 objects: eight Tatooine walls, Mustafar mining facility and Y-8 chair.

Each sampled client shared template exists and is in the merged object CRC table. Sampled staged files match the respective applied commit byte-for-byte. The four server registration repairs reproduce exactly as a single quoted-path replacement in the original bytes, retaining line endings. The two client-only repairs keep their server definitions in supporting files; the Kashyyyk server registration is also repaired by batch 1a.

Read the complete batch-2 diff, batch-1 generator sections for path/shared-path repairs and wearables, both stored check summaries, include traversal and apply scripts. The apply script checks destination hashes before copying and refuses conflicting current files. Its all-checks-before-copy design prevents conflict-based partial application, but is not transactional against disk/copy failure; that is an operational limitation rather than a new content defect. It was not executed.

The new wearables carry stock-style pre-CU race lists and experimental fields; rings retain RingObjectMenuComponent. New shared registrations follow the matching tangible/static template class, and shared includes precede server instantiation through the existing object roots. Batch 2 wires previously unreachable component/construction/content/static groups without adding recipes, house deed chains or encounters. Registering those objects does not implement their later-era systems.

Fable's stored whole-batch checks report 1,090 batch-1 and 55 batch-2 objects, 1,100/22 Lua files parsed, no introduced missing includes or collisions. Those are supporting author evidence, not independently repeated whole-batch acceptance. This review independently re-read the sample's client data and committed bytes. It did not rebuild, launch a client, spawn/equip objects, change a server file or restart a galaxy.

## Required follow-up before promotion/use

1. Real-client smoke test: create representative junk, necklaces/rings, all three pants; equip supported male/female species, inspect rendering/slots, remove, persist/relog. The single SAT used by the pants has not been proven suitable for every allowed body. Additional species remain outside this batch.
2. Place one wall and the mining facility using the appropriate world/static placement route; test collision and visibility. Ordinary createitem is not a static-placement test. Test the Y-8 chair's furniture behavior separately.
3. Verify startup template loading on a fresh test galaxy using the required archive order; no missing-parent/registration errors. CRC presence alone does not prove transitive appearance assets or runtime behavior.
4. Before live path renames, audit old-path references and any persisted objects against the full 1,074-path mapping. The sample proves mechanical replacement, not that a live database contains no older objects or that every outside consumer was migrated. Keep rollback/migration decisions with Claude and the owner.
5. Keep the documented 315 missing batch-1 client names visible as an existing usability gap. Supply original labels/custom names before exposing affected objects to players. No loot/vendor source is wired by this batch, so no new economy behavior was accepted.
6. Retain MTG source credit/licences and per-asset provenance. The README distinguishes repacked SOE data from creator-original art; it is not blanket permission for unrelated store/KOTOR assets. No excluded/leaked source was read for this review. Outbound publication must also follow the owner's name-redaction rule, preserving required licence credits.

Open owner choices (paths, junk/collection distribution, species extension, prison-guard pants) remain on the board. Review complete within the requested reduced scope; gameplay and live gates remain open.
