#!/usr/bin/env python3
"""C17: manual, one-way Discord digests. Default is read-only dry run.

No dependency outside Python's standard library. See discord-plan.md before use.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime
import hashlib
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

OUTPUTS = Path(__file__).resolve().parents[2]
MAX_UNITS = 1800  # UTF-16 units, comfortably below Discord's 2,000 character cap
INTERVAL = 60
SECRET_LINE = re.compile(
    r"password|passwd|\bpwd\b|secret|token|credential|\baccount\b|\baccounts\b|"
    r"\blogin\b|config-local|swg-login|agent-account|authorization|"
    r"\b(?:api[_ -]?key|username|user_name|salt|hash)\b|\b[A-Za-z0-9_+/=-]{40,}\b", re.I)
URL = re.compile(r"(?:https?|ftp)://[^\s<>]+", re.I)
PATH = re.compile(r"(?<!\w)(?:[A-Za-z]:[\\/]|\\\\|/|~/|\.\.?[\\/])[^\s<>`\"']+")
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b", re.I)
IPV6 = re.compile(r"\[[0-9a-f:.%]+\](?::\d+)?|(?<![\w:])[0-9a-f:]*:[0-9a-f:.%]+(?![\w:])", re.I)
PORT = re.compile(r"\b(?:ports?\s*[=:]?\s*\d[\w,-]*|localhost(?::\d+)?)\b|:\d{4,5}\b", re.I)


class SafeError(Exception):
    """Messages must be fixed text, never source data, paths or HTTP exceptions."""


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def ipv6_filter(match):
    value = match.group()
    candidate = value[1:value.index("]")] if value.startswith("[") else value
    try:
        ipaddress.IPv6Address(candidate)
        return "[address removed]"
    except ValueError:
        return value


def sanitize(text, names=()):
    """Drop risky lines; remove paths/addresses, all mentions and link targets.

    Names are owner-supplied exact private literals, not discovered from account files.
    Unknown unlabelled secrets cannot reliably be detected: review every preview.
    """
    result = []
    for line in unicodedata.normalize("NFKC", text).splitlines():
        line = "".join(c for c in line if unicodedata.category(c)[0] != "C")
        if SECRET_LINE.search(line):
            result.append("[private line removed]")
            continue
        # Whole-line removal also covers paths containing spaces or unusual quoting.
        if PATH.search(URL.sub("[link removed]", line)):
            result.append("[path line removed]")
            continue
        for name in sorted(names, key=len, reverse=True):
            line = re.sub(re.escape(name), "[private name]", line, flags=re.I)
        line = URL.sub("[link removed]", line)
        line = IPV6.sub(ipv6_filter, line)
        line = IP.sub("[address removed]", line)
        line = PATH.sub("[path removed]", line)
        line = PORT.sub("[port removed]", line)
        line = re.sub(r"<[@#][^>]+>", "[mention removed]", line)
        line = line.replace("@", "[at]")
        if line.strip():
            result.append(line.strip())
    return "\n".join(result)


def payload(text, names=()):
    text = sanitize(text, names)
    # Encode by UTF-16 units so astral characters cannot exceed the API limit.
    raw = text.encode("utf-16-le")
    if len(raw) > MAX_UNITS * 2:
        text = raw[:(MAX_UNITS - 16) * 2].decode("utf-16-le", errors="ignore") + "\n[truncated]"
    return {"content": text, "allowed_mentions": {"parse": []}, "flags": 4}


def read_source(root, relative):
    file = root / relative
    if not file.resolve().is_relative_to(root.resolve()):
        raise SafeError("Source leaves outputs; refused.")
    return file.read_text(encoding="utf-8-sig")


def sections(text):
    return [(m.group(1).strip(), m.group(2).strip()) for m in
            re.finditer(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", text, re.M | re.S)]


def collect(root, source, now, names=()):
    """Only four allowlisted sources; never walk directories or read login/config files."""
    events = []

    def add(kind, key, text):
        body = payload(text, names)
        events.append({"id": digest([kind, key]), "payload": body})

    board = overnight = None
    if source in ("board", "morning", "all"):
        board = sections(read_source(root, "SWG-handoff.md").split("## Log\n", 1)[1])
    if source in ("overnight", "morning", "all"):
        overnight = sections(read_source(root, "Bot-reports/OVERNIGHT.md"))
    if source in ("board", "all"):
        for heading, body in board[:4]:
            # Stable heading identity: edits to an already-posted entry do not repost.
            lines = [s.strip() for s in body.splitlines() if s.strip()][:3]
            add("board", heading, "Dev log: " + heading + "\n" + "\n".join(lines))
    if source in ("overnight", "all"):
        for heading, body in overnight[-1:]:
            for line in [s for s in body.splitlines() if s.startswith("- ")][-5:]:
                if line.startswith("- "):
                    add("overnight", [heading, line], "Overnight: " + heading + "\n" + line)
    if source in ("morning", "all"):
        day = now.strftime("%Y-%m-%d")
        lines = ["Morning summary: " + day,
                 "Latest recorded notes (may predate today; no new checks run):"]
        if board:
            lines += ["Dev: " + board[0][0]]
        if overnight:
            heading, body = overnight[-1]
            lines += ["Overnight: " + heading] + [s for s in body.splitlines() if s.startswith("- ")][:3]
        add("morning", day, "\n".join(lines))
    if source in ("status", "all"):
        data = json.loads(read_source(root, "Agent/live/status.json"))
        stamp = datetime.strptime(data["written"], "%Y-%m-%d %H:%M:%S")
        # Snapshot clock is local to WSL; skew/future values are unknown, never UP/DOWN.
        fresh = 0 <= (now - stamp).total_seconds() <= 15 * 60
        processes = data.get("processes", {})
        servers = processes.get("servers", [])
        for galaxy in ("test", "live"):
            running = any(s.get("which") == galaxy for s in servers)
            if not fresh or "servers" not in processes:
                value = "UNKNOWN (stale or incomplete snapshot)"
            elif galaxy == "live" and not running:
                value = "DOWN" if processes.get("live_galaxy") == "inactive" else "UNKNOWN"
            else:
                value = "UP" if running else "DOWN"
            # State compares transitions, so UP -> DOWN -> UP emits all three.
            events.append({"id": "status:" + galaxy, "value": value,
                           "payload": payload(f"{galaxy.title()} galaxy: {value}\nSnapshot: {data['written']}", names)})
    return events


def empty_state():
    return {"version": 1, "sent": [], "status": {}, "next_at": 0, "inflight": None}


def load_state(path):
    if not path.exists():
        return empty_state()
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("version") != 1 or not isinstance(data.get("sent"), list)
            or not all(isinstance(s, str) for s in data["sent"])
            or not isinstance(data.get("status"), dict)
            or not isinstance(data.get("next_at"), (int, float))
            or not math.isfinite(data["next_at"])):
        raise SafeError("Invalid state; refused. Restore the saved state before retrying.")
    return data


def pending(events, state, limit):
    if state.get("inflight"):
        raise SafeError("Unconfirmed previous send; reconcile the state before retrying.")
    items = []
    for event in events:
        if "value" in event:
            if state["status"].get(event["id"]) == event["value"]:
                continue
        elif event["id"] in state["sent"]:
            continue
        if event["id"] not in {s["id"] for s in items}:
            items.append(event)
    return items[:limit]


def save_state(path, state):
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(canonical(state) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


@contextmanager
def send_lock(path):
    lock = path.with_suffix(path.suffix + ".lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise SafeError("Another sender or stale lock exists; refused.") from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink()


def private_file(path):
    path = path.resolve(strict=True)
    if path.is_relative_to(OUTPUTS.parent):
        raise SafeError("Private files must live outside the project folder.")
    if os.name != "nt" and path.stat().st_mode & 0o077:
        raise SafeError("Private file needs owner-only permissions (0600).")
    return path


def read_webhook(path):
    value = private_file(path).read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"https://discord\.com/api(?:/v10)?/webhooks/[0-9]+/[A-Za-z0-9_-]+", value):
        raise SafeError("Private webhook file has an invalid endpoint.")
    return value + "?wait=true"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http_post(endpoint, body):
    request = urllib.request.Request(endpoint, data=canonical(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json",
                                              "User-Agent": "SWG-private-digest/1.0"}, method="POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=20) as response:
            response.read(4096)  # Deliberately discard response content.
            return response.status, dict(response.headers.items()), b""
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers.items()), error.read(4096)
    except Exception:
        # Includes certificate, proxy and URL errors; never echo exceptions or endpoint.
        raise SafeError("Network result unknown; reconcile before retrying.") from None


def retry_seconds(headers, body):
    values = [INTERVAL]
    for key, value in headers.items():
        if key.lower() in ("retry-after", "x-ratelimit-reset-after"):
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                pass
    try:
        values.append(float(json.loads(body).get("retry_after", INTERVAL)))
    except (ValueError, TypeError, AttributeError):
        pass
    return max(v for v in values if math.isfinite(v) and v >= 0)


def send_one(event, state, path, endpoint, post=http_post, clock=time.time):
    if clock() < state["next_at"]:
        raise SafeError("Local or Discord cooldown active; try again later.")
    # Write intent BEFORE the network. Crash/timeout cannot trigger blind duplicate retries.
    state["inflight"] = event["id"]
    save_state(path, state)
    code, headers, body = post(endpoint, event["payload"])
    state["next_at"] = clock() + retry_seconds(headers, body)
    if 200 <= code < 300:
        if "value" in event:
            state["status"][event["id"]] = event["value"]
        else:
            state["sent"].append(event["id"])
        state["inflight"] = None
        save_state(path, state)
        return
    if 400 <= code < 500:
        state["inflight"] = None  # Confirmed rejection, safe to retry after correcting/cooldown.
    save_state(path, state)
    raise SafeError("Discord rate limited the send; cooldown saved." if code == 429
                    else "Discord rejected or could not confirm the send; inspect state before retrying.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("board", "overnight", "morning", "status", "all"), default="all")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Default; no secret/network/state writes")
    mode.add_argument("--send", action="store_true")
    parser.add_argument("--owner-approved", action="store_true", help="Only after the owner's explicit go")
    parser.add_argument("--approved-digest", help="Digest of the exact reviewed preview")
    parser.add_argument("--webhook-file", type=Path)
    parser.add_argument("--privacy-file", type=Path, help="Private JSON: account_names and private_literals lists")
    parser.add_argument("--state", type=Path, default=OUTPUTS / "Agent/discord-state.json")
    parser.add_argument("--limit", type=int, default=1, help="Preview size, 1 to 5; send requires 1")
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.limit <= 5:
            raise SafeError("Limit must be between 1 and 5.")
        if args.send and (not args.owner_approved or not args.approved_digest
                          or not args.webhook_file or not args.privacy_file or args.limit != 1):
            raise SafeError("Send requires owner go, approved digest, both private files and limit 1.")
        names = []
        if args.privacy_file:
            privacy = json.loads(private_file(args.privacy_file).read_text(encoding="utf-8"))
            for key in ("account_names", "private_literals"):
                values = privacy[key]
                if not isinstance(values, list) or not all(isinstance(v, str) and v.strip() for v in values):
                    raise SafeError("Invalid private redaction list.")
                names += values
        # Dry runs never open the webhook file, even if supplied.
        def prepare():
            state = load_state(args.state)
            events = collect(OUTPUTS, args.source, datetime.now(), names)
            items = pending(events, state, args.limit)
            preview = [e["payload"] for e in items]
            return state, items, preview

        if not args.send:
            _, _, preview = prepare()
            print(canonical(preview))
            print("Preview SHA256: " + digest(preview), file=sys.stderr)
            return 0
        with send_lock(args.state):
            state, items, preview = prepare()
            if not items:
                raise SafeError("No new digest to send.")
            if digest(preview) != args.approved_digest:
                raise SafeError("Preview changed; dry-run and review again.")
            endpoint = read_webhook(args.webhook_file)
            send_one(items[0], state, args.state, endpoint)
        print("Digest confirmed; de-duplication state saved.")
        return 0
    except SafeError as error:
        print(str(error), file=sys.stderr)
    except Exception:
        print("Input, state or I/O error; refused. No private detail is printed.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
