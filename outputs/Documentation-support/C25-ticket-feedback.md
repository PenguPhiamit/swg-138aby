# C25 — ticket failure feedback

Source commit `5c41ed62` on `/opt/swg/Core3-gpt`, branch `gpt/work`; Agent: ChatGPT. Clean starting worktree; only PurchaseTicketCommand.h changed (eight added lines); diff whitespace check passed. **Unbuilt and untested in game; Claude review/cherry-pick/build pending.** No dev/live merge or service changes.

Arrival without a shuttle now tells the player destination travel is temporarily unavailable. The departure travel point is checked for null/missing shuttle too and reports departure travel unavailable. Both return before credit subtraction, coupon UI or ticket generation. Plain original sentences avoid relying on an unverified stock travel STF key. Existing invalid-point/route messages, fares and transaction paths otherwise remain.

Requested validation: no departure shuttle; no destination shuttle; normal departure/destination after boot delay; no charge or ticket on blocked cases; normal single/round-trip tickets and coupon UI unchanged. Test new source in Claude's dev build, never build in the GPT worktree.

`tools/hoth/prepare_ticket_feedback.py` records the guarded edit recipe and refuses a dirty/wrong-branch worktree. It was run once as swgemu against the assigned worktree. Do not rerun it after the commit without adapting/reviewing its clean-tree preconditions. No credentials or game assets were copied.
