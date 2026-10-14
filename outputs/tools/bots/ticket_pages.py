"""Select fresh collector lists; never answer a purchase confirmation as a ticket list."""
import json


def newest_ticket_list(pages, before=()):
    old = {json.dumps(p, sort_keys=True) for p in before}
    candidates = [p for p in pages if 'msgSelected' in json.dumps(p)
                  and json.dumps(p, sort_keys=True) not in old]
    return max(candidates, key=lambda p: p.get('page_id', 0), default=None)


def answer_coupon(bot, before=()):
    """A character carrying the new-player travel coupon gets a question instead of a ticket (PurchaseTicketCommand:
    "use the coupon or pay credits?") and nothing else happens until it is answered. Answer OK (use the coupon; the
    callback then makes the ticket). Returns True when a coupon question was answered.
    Correction (14 Oct 13:40): this was NOT the cause of the silent failures it was written for; no bot has met the
    coupon question yet. Those purchases came within minutes of a galaxy start, while Core3 still holds its shuttles
    (ShuttleZoneComponent BootDelay, 5 min; a travel point without a shuttle fails silently). tools/test_galaxy.py now
    sets a 30 s delay on the test galaxy. Kept because the coupon question is real Core3 behaviour."""
    old = {json.dumps(p, sort_keys=True) for p in before}
    pages = [p for p in bot.sui_pages().get('pages', [])
             if 'travel_coupon' in json.dumps(p) and json.dumps(p, sort_keys=True) not in old]
    page = max(pages, key=lambda p: p.get('page_id', 0), default=None)
    if page:
        bot.sui_respond(page['page_id'], 0, [], wait=3)
    return page is not None
