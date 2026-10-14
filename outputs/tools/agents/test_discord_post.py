"""Offline only: no Discord account, endpoint, secret file or socket is used."""
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timedelta
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import discord_post as dp


class DiscordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "Bot-reports").mkdir()
        (self.root / "Agent/live").mkdir(parents=True)
        self.statefile = self.root / "state.json"
        self.now = datetime(2026, 10, 14, 8, 0)
        (self.root / "SWG-handoff.md").write_text(
            "## Task board\n### Not a log\nprivate planning\n## Log\n\n"
            "### 2026-10-14 07:50 ChatGPT\nBuild passed.\nOffline only.\nNext review.\nFourth line.\n"
            "### 2026-10-13 Claude\nOlder note.\n", encoding="utf-8")
        (self.root / "Bot-reports/OVERNIGHT.md").write_text(
            "### 01:00\n- Old line.\n### 07:30\n- Squads 3/4.\n- FAIL: reachability.\n", encoding="utf-8")
        (self.root / "Agent/discord-feed.json").write_text(json.dumps([
            dict(date="2026-10-14", topic="telemetry", state="prepared", checks=14)]), encoding="utf-8")
        self.write_status()

    def test_raw_send_refused_before_private_files(self):
        with patch.object(dp, "private_file", side_effect=AssertionError("private file read")):
            code, out, err = self.invoke("--send", "--source", "board")
        self.assertEqual(code, 2)
        self.assertIn("local previews only", err)

    def test_curated_projection_rejects_names_and_extra_fields(self):
        event = self.events("curated")[0]
        self.assertIn("Acceptance telemetry", event["payload"]["content"])
        record = dict(date="2026-10-14", topic="telemetry", state="prepared", checks=14)
        for bad in (record | {"author": "PrivatePerson"}, record | {"topic": "PrivatePerson"},
                    record | {"state": "PrivateAlias"}, record | {"checks": True}):
            (self.root / "Agent/discord-feed.json").write_text(json.dumps([bad]), encoding="utf-8")
            with self.assertRaises(dp.SafeError):
                self.events("curated")

    def write_status(self, live="inactive", servers=None, age=0, extra=None):
        data = {"written": (self.now - timedelta(minutes=age)).strftime("%Y-%m-%d %H:%M:%S"),
                "processes": {"live_galaxy": live, "servers": servers if servers is not None else [{"which": "test"}]},
                "console_tail": ["password=DO_NOT_COPY"], "bots": "account=DO_NOT_COPY"}
        if extra:
            data.update(extra)
        (self.root / "Agent/live/status.json").write_text(json.dumps(data), encoding="utf-8")

    def events(self, source="board"):
        return dp.collect(self.root, source, self.now)

    def invoke(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(dp, "OUTPUTS", self.root), redirect_stdout(out), redirect_stderr(err):
            code = dp.main(["--state", str(self.statefile), *args])
        return code, out.getvalue(), err.getvalue()

    def test_all_sources_are_projected_and_not_console_or_task_board(self):
        events = self.events("all")
        text = dp.canonical(events)
        self.assertNotIn("DO_NOT_COPY", text)
        self.assertNotIn("private planning", text)
        self.assertNotIn("Fourth line", text)
        self.assertNotIn("Old line", text)
        self.assertIn("Squads 3/4", text)
        self.assertIn("Morning summary", text)

    def test_redacts_sensitive_lines_names_addresses_paths_mentions(self):
        samples = ["password=hunter", "PASSWORD: hunter", "account testuser", "config-local.lua dump",
                   "SWG-login.txt contents", "token: privatevalue", "hash abc", "api_key = xyz",
                   r"Read C:\Users\Some Person\private.txt now", "/opt/swg/private file.txt",
                   "Connect 192.168.1.5:44453 or [2001:db8::1]:46453 port 44453",
                   "Connect ::1 and localhost:44453", "https://example.invalid/private",
                   "@everyone @here <@12345> <@&12345>", "Owner is TestOwner and testowner."]
        text = dp.sanitize("\n".join(samples), ["TestOwner"])
        for forbidden in ("hunter", "testuser", "privatevalue", "xyz", "Some Person", "private.txt",
                          "192.168", "2001:db8", "44453", "46453", "::1", "example.invalid", "@", "TestOwner", "testowner"):
            self.assertNotIn(forbidden, text)

    def test_unicode_obfuscated_mentions_and_secret_labels(self):
        text = dp.sanitize("＠everyone\npas\u200bsword: hidden\nｔｏｋｅｎ: hidden")
        self.assertNotIn("@", text)
        self.assertNotIn("hidden", text)

    def test_non_bmp_limit_and_mentions(self):
        body = dp.payload("😀" * 4000)
        self.assertLessEqual(len(body["content"].encode("utf-16-le")) // 2, dp.MAX_UNITS)
        self.assertEqual(body["allowed_mentions"], {"parse": []})
        self.assertEqual(body["flags"], 4)

    def test_dry_run_exact_payloads_without_secret_or_state_or_network(self):
        with patch.object(dp, "read_webhook", side_effect=AssertionError("secret accessed")), \
             patch.object(dp, "http_post", side_effect=AssertionError("network accessed")):
            code, out, err = self.invoke("--dry-run", "--source", "board", "--webhook-file", "nonexistent")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out), [self.events()[0]["payload"]])
        self.assertIn(dp.digest(json.loads(out)), err)
        self.assertFalse(self.statefile.exists())
        self.assertFalse(self.statefile.with_suffix(".json.lock").exists())

    def test_dry_run_does_not_change_existing_state(self):
        state = dp.empty_state()
        state["sent"].append(self.events()[0]["id"])
        dp.save_state(self.statefile, state)
        before = self.statefile.read_bytes()
        code, out, _ = self.invoke("--source", "board")
        self.assertEqual(code, 0)
        self.assertIn("Older note", out)
        self.assertEqual(before, self.statefile.read_bytes())

    def test_send_without_go_refuses_before_reading_secret(self):
        with patch.object(dp, "read_webhook", side_effect=AssertionError):
            code, _, err = self.invoke("--send", "--source", "curated")
        self.assertEqual(code, 2)
        self.assertIn("owner go", err)

    def test_success_records_only_confirmed_event_and_saves_cooldown(self):
        state = dp.empty_state()
        event = self.events()[0]
        calls = []
        def post(endpoint, body):
            self.assertEqual(dp.load_state(self.statefile)["inflight"], event["id"])
            calls.append(body)
            return 200, {}, b""
        dp.send_one(event, state, self.statefile, None, post, lambda: 100)
        saved = dp.load_state(self.statefile)
        self.assertEqual(calls, [event["payload"]])
        self.assertEqual(saved["sent"], [event["id"]])
        self.assertEqual(saved["next_at"], 160)
        self.assertIsNone(saved["inflight"])
        self.assertEqual(len(dp.pending(self.events(), saved, 5)), 1)

    def test_cooldown_prevents_request_even_across_processes(self):
        state = dp.empty_state()
        state["next_at"] = 500
        dp.save_state(self.statefile, state)
        with self.assertRaises(dp.SafeError):
            dp.send_one(self.events()[0], dp.load_state(self.statefile), self.statefile, None,
                        lambda *_: self.fail("network called"), lambda: 499)

    def test_429_honours_header_and_json_without_automatic_retry(self):
        state = dp.empty_state()
        calls = []
        def post(*args):
            calls.append(args)
            return 429, {"Retry-After": "90"}, b'{"retry_after": 125}'
        with self.assertRaises(dp.SafeError):
            dp.send_one(self.events()[0], state, self.statefile, None, post, lambda: 100)
        saved = dp.load_state(self.statefile)
        self.assertEqual(len(calls), 1)
        self.assertEqual(saved["sent"], [])
        self.assertEqual(saved["next_at"], 225)
        self.assertIsNone(saved["inflight"])

    def test_timeout_and_server_error_leave_intent_for_manual_reconciliation(self):
        for reply in (None, 503):
            with self.subTest(reply=reply):
                state = dp.empty_state()
                def post(*_):
                    if reply is None:
                        raise dp.SafeError("Network result unknown.")
                    return reply, {}, b"private error response"
                with self.assertRaises(dp.SafeError):
                    dp.send_one(self.events()[0], state, self.statefile, None, post, lambda: 100)
                saved = dp.load_state(self.statefile)
                self.assertTrue(saved["inflight"])
                with self.assertRaises(dp.SafeError):
                    dp.pending(self.events(), saved, 5)

    def test_status_transitions_and_stale_or_future_snapshots(self):
        state = dp.empty_state()
        events = self.events("status")
        for e in events:
            state["status"][e["id"]] = e["value"]
        self.assertEqual(dp.pending(events, state, 5), [])
        self.write_status(servers=[])
        change = dp.pending(self.events("status"), state, 5)
        self.assertEqual(len(change), 1)
        self.assertEqual(change[0]["value"], "DOWN")
        state["status"]["status:test"] = "DOWN"
        self.write_status()
        self.assertEqual(dp.pending(self.events("status"), state, 5)[0]["value"], "UP")
        for age in (16, -60):
            self.write_status(age=age)
            self.assertTrue(all("UNKNOWN" in e["value"] for e in self.events("status")))

    def test_morning_once_per_date_but_next_day_posts(self):
        state = dp.empty_state()
        first = self.events("morning")[0]
        state["sent"] = [first["id"]]
        self.assertEqual(dp.pending(self.events("morning"), state, 5), [])
        next_day = dp.collect(self.root, "morning", self.now + timedelta(days=1))
        self.assertEqual(len(dp.pending(next_day, state, 5)), 1)

    def test_corrupt_state_does_not_reset_and_repost(self):
        self.statefile.write_text("broken", encoding="utf-8")
        code, _, err = self.invoke("--source", "board")
        self.assertEqual(code, 2)
        self.assertNotIn("broken", err)

    def test_lock_excludes_parallel_sender(self):
        with dp.send_lock(self.statefile):
            with self.assertRaises(dp.SafeError):
                with dp.send_lock(self.statefile):
                    self.fail("second sender acquired lock")
        self.assertFalse(self.statefile.with_suffix(".json.lock").exists())

    def test_private_file_inside_project_and_source_escape_refused(self):
        with patch.object(dp, "OUTPUTS", self.root):
            with self.assertRaises(dp.SafeError):
                dp.private_file(self.statefile.parent)
        with self.assertRaises(dp.SafeError):
            dp.read_source(self.root, "../outside-file")

    def test_transport_never_echoes_exception_or_follows_redirect(self):
        with patch.object(dp.urllib.request, "Request", return_value=object()), \
             patch.object(dp.urllib.request, "build_opener") as opener:
            opener.return_value.open.side_effect = OSError("private endpoint contents")
            with self.assertRaises(dp.SafeError) as error:
                dp.http_post(None, dp.payload("Safe note."))
        self.assertNotIn("private endpoint", str(error.exception))
        self.assertIsNone(dp.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.invalid"))

    def test_approved_preview_change_blocks_before_webhook_read(self):
        with patch.object(dp, "private_file", side_effect=lambda p: p), \
             patch.object(dp, "read_webhook", side_effect=AssertionError("secret accessed")):
            privacy = self.root / "privacy.json"
            privacy.write_text('{"account_names": [], "private_literals": []}', encoding="utf-8")
            code, _, err = self.invoke("--send", "--owner-approved", "--source", "curated",
                                       "--approved-digest", "incorrect", "--webhook-file", "unused",
                                       "--privacy-file", str(privacy))
        self.assertEqual(code, 2)
        self.assertIn("Preview changed", err)

    def test_cli_reviewed_payload_reaches_mock_transport_exactly_once(self):
        privacy = self.root / "privacy.json"
        privacy.write_text('{"account_names": ["TestOwner"], "private_literals": []}', encoding="utf-8")
        with patch.object(dp, "private_file", side_effect=lambda p: p):
            code, out, err = self.invoke("--source", "curated", "--privacy-file", str(privacy))
        self.assertEqual(code, 0, err)
        preview = json.loads(out)
        original = dp.send_one
        requests = []
        def mock_send(event, state, path, endpoint):
            def post(_, body):
                requests.append(body)
                return 200, {}, b""
            return original(event, state, path, endpoint, post, lambda: 100)
        with patch.object(dp, "private_file", side_effect=lambda p: p), \
             patch.object(dp, "read_webhook", return_value=None), \
             patch.object(dp, "send_one", side_effect=mock_send):
            code, _, err = self.invoke("--send", "--source", "curated", "--owner-approved",
                                       "--approved-digest", dp.digest(preview), "--privacy-file", str(privacy),
                                       "--webhook-file", "unused")
        self.assertEqual(code, 0, err)
        self.assertEqual(requests, preview)
        self.assertEqual(dp.load_state(self.statefile)["sent"], [self.events("curated")[0]["id"]])

    def test_4xx_never_prints_private_response_or_marks_sent(self):
        state = dp.empty_state()
        with self.assertRaises(dp.SafeError) as error:
            dp.send_one(self.events()[0], state, self.statefile, None,
                        lambda *_: (403, {}, b"private URL and response"), lambda: 100)
        self.assertNotIn("private URL", str(error.exception))
        self.assertEqual(state["sent"], [])
        self.assertIsNone(state["inflight"])

    def test_retry_parsing_rejects_nonfinite_and_negative_values(self):
        self.assertEqual(dp.retry_seconds({"Retry-After": "nan"}, b'{"retry_after": -20}'), dp.INTERVAL)
        self.assertEqual(dp.retry_seconds({"X-RateLimit-Reset-After": "70.5"}, b"not json"), 70.5)

    def test_timestamps_are_preserved_while_ipv6_is_removed(self):
        text = dp.sanitize("Snapshot: 2026-10-14 05:04:28\nAddress: 2001:db8::1\nAddress: 2001:db8:0:0:0:0:0:1")
        self.assertIn("2026-10-14 05:04:28", text)
        self.assertNotIn("2001:db8", text)


if __name__ == "__main__":
    unittest.main()
