"""Select fresh collector lists; never answer a purchase confirmation as a ticket list."""
import json


def newest_ticket_list(pages, before=()):
    old = {json.dumps(p, sort_keys=True) for p in before}
    candidates = [p for p in pages if 'msgSelected' in json.dumps(p)
                  and json.dumps(p, sort_keys=True) not in old]
    return max(candidates, key=lambda p: p.get('page_id', 0), default=None)


def answer_coupon(bot, before=()):
    """A character carrying the new-player travel coupon gets a question instead of a ticket (PurchaseTicketCommand:
    "use the coupon or pay credits?") and nothing else happens until it is answered; a galaxy restore hands the coupon
    back (14 Oct 09:37: three silent purchases). Answer OK (use the coupon; the callback then makes the ticket).
    Returns True when a coupon question was answered."""
    old = {json.dumps(p, sort_keys=True) for p in before}
    pages = [p for p in bot.sui_pages().get('pages', [])
             if 'travel_coupon' in json.dumps(p) and json.dumps(p, sort_keys=True) not in old]
    page = max(pages, key=lambda p: p.get('page_id', 0), default=None)
    if page:
        bot.sui_respond(page['page_id'], 0, [], wait=3)
    return page is not None
