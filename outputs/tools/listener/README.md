# Input listener for the owner's client

Built by Claude, 15 Oct 2026, at the owner's request: *a listener for my character/client that the main chat can tell what
to do, tracking my inputs on my keys and in game, only while I'm logged into the client.* Owner's choices: the gate is
"server says I'm online and the client is in front"; keys and clicks are recorded with **typed text hidden**.

It is a plain Windows script (Python standard library, nothing installed, no network). The "low-effort model" part is the
helper agent `swg-listener` (Haiku), which only runs the commands below for the main chat and reports their output. A model
polling keys all day would burn plan usage for nothing, so no model watches the keyboard.

## Use

```
cd outputs/tools/listener
python -I listener.py setup      # once; reads your character names from SWG-client/characterlist_owner.txt
python -I listener.py start      # background, no window; stop with: stop
python -I listener.py status | pause | resume | stop
python -I listener.py summary --minutes 10      # keys, clicks, typing counts, position, notes
python -I listener.py tail 20 | mark "boss fight" | forget
```

The main chat can ask the `swg-listener` helper to do any of that ("start the listener", "what did I just do?"); it needs a
restart of the main chat before the helper's name is known (agent files load at session start). Nothing starts by itself:
there is no autostart or scheduled task. `start` is the only thing that begins listening.

## When it listens

The recorder reads **no key or mouse state at all** unless every one of these holds, checked about every quarter second:

1. `SWGEmu.exe` is the front window (any other program in front: nothing is read);
2. a fresh `log/who.json` (the test galaxy's or the live one's, which Core3 rewrites on every login and logout) lists one of
   your characters online;
3. no `PAUSE` or `STOP` file in `Agent/listener/`.

Anything unreadable closes the gate. At the login and character-select screens no character of yours is online, so nothing
is read there and a password is not recorded. `status` says which condition is missing. Bots with your characters' first
names are left out by `setup`, so a bot being online never opens the gate.

## What is written

`Agent/listener/events-<day>-<hour>.jsonl` (gitignored, local to this PC, files older than 48 hours are deleted):

| Event | Contents |
|---|---|
| key press | key name and how long it was held, for example `{"k":"W","ms":1840}` |
| mouse button | which button, how long, and the position inside the client window |
| position | your character's zone and x, y from the player list (every 2 s on the test galaxy, every 5 min on the live one) |
| typing | how many characters and how long, never which: after Enter (chat) or `/` (a slash command), and for any typing-like run of letters (four presses, three different keys, under 1.2 s apart) |
| gate | when listening opened and closed, and why |

Never written: window titles, other programs, screenshots, anything typed, or the player list's account numbers and
addresses. Letters wait 7 s before being written so a typing-like run can be recognised first (so `tail` runs a few seconds
behind for letter keys). Digits, F-keys, arrows, Space and mouse buttons are written straight away, so hotbar use is kept.

**Limits, said plainly**
- A fast run of four W/A/S/D/E/R-type letter taps with three different keys can look like typing and be counted instead of written. If that
  bothers you, list keys in `"movement_keys"` in `listener-config.json` to exempt them (a password made of only those letters
  would then show, which the closed gate prevents).
- Outside chat, a word of one to three letters, or typing slower than 1.2 s per key, is written key by key. The gate is what
  protects there. (On 15 Oct the first live run wrote a five-letter word typed into a game text field because the rule then
  needed six presses; it now needs four.)
- Keys are sampled 50 times a second; a tap shorter than 20 ms can be missed.
- In-game events other than your position (combat, commands you ran, chat) are not captured: that would need a server-side
  feed, which is a separate piece of work under the server lock.
- Live galaxy positions are as old as its player list (up to 5 minutes).

This is a deliberate exception to `live_map.py`'s rule that the owner is never logged. To delete everything: `forget`. To
turn it off for good: `stop`, then delete `tools/listener/` and the helper `.claude/agents/swg-listener.md`.

## Tested

34 offline tests (`python -I test_listener.py`; fake keyboard and window, so no key is read): the gate and what it never reads,
the typing rules (chat, slash commands, escape, idle, typing-like runs, the gate closing mid-sentence, a whole chat message
left as a count), the player-list reader including Core3's delete-and-rename of `who.json`, files, pruning, `setup`,
`summary`. A live check on 15 Oct confirmed `setup`, `start`, `status`, `stop` and that the gate opened with the client in
front and the character online. **Not tested:** capturing real keystrokes and clicks in the game: please try
`start`, play for a minute, then `summary` and `tail`, and tell the main chat what looks wrong.
