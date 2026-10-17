# Ghostfire crystal quest on Ossus: brief

Claude, 17 Oct 2026, for the Ossus content session to build. Design only so far: nothing is built, installed or tested.

## The owner's request and decisions (17 Oct)

> "how about that ghost fire color crystal? can we make that happen and have the hidden jedi actually be hidden in a
> cave and reward the player for following some kind of quest or having certain badges to finish and get the crystal.
> have it be linked so one of the famous jedi of the era finding and stow it away from the vong and krayt."

From the owner's answers on a decision card the same morning:

- **Who builds it:** the Ossus content session. A local model (WaifuGemma4) drafts the dialogue; Claude reviews it.
- **The Jedi:** T'ra Saa.
- **The gate:** a short quest **plus** exploration badges.
- **The crystal's look:** simple first, a dim pearly blade colour. The opalescent trails come later
  ([darksaber-ghostfire-feasibility.md](darksaber-ghostfire-feasibility.md)).

Gates that still apply: Ossus is closed for the friends launch, and the owner's 16 Oct rule puts an end-to-end test pass
before new content. So build this in dev and on the test galaxy only, with the server lock. Nothing goes live without
the owner's OK.

## Lore (checked 17 Oct on Wookieepedia, Legends: https://starwars.fandom.com/wiki/T%27ra_Saa/Legends)

These are facts, in our own words. Write all game text fresh, never copied from the wiki (CC BY-SA).

- T'ra Saa was a **Neti** (a long-lived, tree-like species that can take root like a tree) and a Jedi Master for
  centuries. She was one of Mace Windu's teachers and a Jedi General in the Clone Wars.
- She survived Order 66, hid on Kashyyyk, and later joined the New Jedi Order.
- In Krayt's era she sat on the **Jedi High Council** (137 ABY) at the Hidden Temple on Taivas, with K'Kruhk and Tili Qua.
  She held all life sacred and opposed assassinating Krayt.
- She **died in 138 ABY** at the Hidden Temple, turning the Temple's energy into a beam that opened a path through the
  Sith fleet so the others could escape.

**Consequence:** our server year is 138-139 ABY, so she is dead and cannot be the NPC. The hidden Jedi (the existing
"robed stranger" at the Sanctuary) becomes **her keeper**, an original character who never gives a name.

**Our own invention (not canon; say so in any notes):** she found a ghostfire crystal during the Yuuzhan Vong War,
kept it from the Vong, and hid it in a cave on Ossus when Krayt's Sith came for the academy (130 ABY). She left a
keeper to wait for someone worthy. The wiki says nothing about her in the Vong war, so none of this contradicts it.

## Quest outline (a proposal for the build session)

1. **The lead:** the existing Archivist (Senn Oduro, Memorial Road / Vault dig) mentions an old Jedi light kept hidden.
   This sets a quest state.
2. **The sites:** the player visits several Jedi sites on Ossus, shown as exploration badges. Find out which Ossus
   badges exist. If there are none, new badge areas need client badge strings (client work) or a server-side
   "visited" flag shown as a quest step. Bring the choice back to the owner.
3. **The keeper:** found in the deepest cave chamber (today: Sanctuary, cell 11), appearing only part of the time as
   now. They won't speak to Imperials. They give a hint while the badges are missing.
4. **The test:** one conversation choice. Mercy or patience passes; force or greed fails, and the player can try again
   later.
5. **The reward:** the ghostfire colour crystal, **once per character**. It's a colour crystal only, with no stats.
6. **Afterwards:** a farewell line, and a short line on later visits.

Crystal, simple look: a new lightsaber colour crystal object with a new colour entry. That needs a client palette or
table change (`palette/wp_lightsaber.pal` was found in the 14 Oct probe), which goes into the friends' client patch,
plus a server item template. Prove that it renders in the owner's client before promising it.

## Dialogue draft

[Agent/local-research/ghostfire-quest/draft.md](../Agent/local-research/ghostfire-quest/draft.md) was written by
WaifuGemma4 on Miniverse, 17 Oct (8K, non-thinking). It is **not reviewed**. Notes for the reviewer:

- The holo-record's last line ("life finds a way to endure") is close to a canon quote by Cade Skywalker. Reword it.
- Test answers B and C are blunt. Keep the idea and soften the wording if wanted.
- Check every line against the content rules: teen-rated, nothing sexual or graphic, no real-world references.
