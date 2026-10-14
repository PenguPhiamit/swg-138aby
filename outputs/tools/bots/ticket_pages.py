"""Select fresh collector lists; never answer a purchase confirmation as a ticket list."""
import json


def newest_ticket_list(pages, before=()):
    old = {json.dumps(p, sort_keys=True) for p in before}
    candidates = [p for p in pages if 'msgSelected' in json.dumps(p)
                  and json.dumps(p, sort_keys=True) not in old]
    return max(candidates, key=lambda p: p.get('page_id', 0), default=None)
