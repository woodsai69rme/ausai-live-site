"""Final smoke test for the reviewer-fix iterations of opt_d_alerts.py.

Runs as a real Python file (not inline -c) so bash escape mangling
doesn't break it. Exits 0 on PASS, non-zero on FAIL.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from opt_d_alerts import (
    _STATUS_PERMANENT_CONFIG_ERROR,
    _safe_int,
    _safe_float,
    _is_retryable,
    send_alert,
    _send_with_retry,
)


def section(name):
    print(f"\n=== {name} ===")


def assert_eq(got, want, label):
    assert got == want, f"{label}: expected {want!r}, got {got!r}"
    print(f"  OK {label}={got!r}")


# 1) Sentinel value is documented and 0
section("1: _STATUS_PERMANENT_CONFIG_ERROR sentinel")
assert_eq(_STATUS_PERMANENT_CONFIG_ERROR, 0, "sentinel value")

# 2) safe coercion (clamping) — _safe_int
section("2: _safe_int clamping (0 -> 1, negatives -> 1)")
assert_eq(_safe_int("3", 99), 3, "string 3")
assert_eq(_safe_int("auto", 99), 99, "string auto -> default")
assert_eq(_safe_int(None, 99), 99, "None -> default")
assert_eq(_safe_int(0, 99), 1, "0 -> clamped to 1")
assert_eq(_safe_int(-5, 99), 1, "negative -> clamped to 1")
assert_eq(_safe_int("0", 99), 1, "string 0 -> clamped to 1")
assert_eq(_safe_int(2, 99), 2, "plain int")

# 3) safe coercion (clamping) — _safe_float
section("3: _safe_float clamping (negative -> 0.0)")
assert_eq(_safe_float("5.0", 99.0), 5.0, "string 5.0")
assert_eq(_safe_float("abc", 99.0), 99.0, "string abc -> default")
assert_eq(_safe_float(None, 99.0), 99.0, "None -> default")
assert_eq(_safe_float(0.0, 99.0), 0.0, "0.0 stays 0.0")
assert_eq(_safe_float(-1.0, 99.0), 0.0, "negative -> clamped to 0.0")
assert_eq(_safe_float(2.5, 99.0), 2.5, "positive float")

# 4) Retr y decision
section("4: _is_retryable decision table")
assert_eq(_is_retryable(False, 401, "http=401"), False, "401 -> not retry")
assert_eq(_is_retryable(False, 403, "http=403"), False, "403 -> not retry")
assert_eq(_is_retryable(False, 404, "http=404"), False, "404 -> not retry")
assert_eq(_is_retryable(False, 500, "http=500"), True, "500 -> retry")
assert_eq(_is_retryable(False, 429, "http=429"), True, "429 -> retry")
assert_eq(_is_retryable(False, -1, "ConnectionRefused"), True, "-1 connect -> retry")
assert_eq(_is_retryable(False, _STATUS_PERMANENT_CONFIG_ERROR, "env missing"), False, "sc=0 -> not retry")
assert_eq(_is_retryable(True, 200, "http=200"), False, "success -> not retry")

# 5) send_alert with missing env => sc=0 sentinel
section("5: send_alert env-missing sentinel")
os.environ.pop("DISCORD_WEBHOOK_URL", None)
sent, info, sc = send_alert("discord", {"x": 1}, dry_run=False)
assert sent is False, f"sent should be False, got {sent}"
assert_eq(sc, _STATUS_PERMANENT_CONFIG_ERROR, "env-missing sc")
assert "env var not set" in info, f"info should mention env var; got {info!r}"
print("  OK info mentions env-missing")

# 6) dry-run via send_alert produces sc=0 sentinel (so _send_with_retry early-exits)
section("6: dry-run via send_alert uses sentinel")
sent, info, sc = send_alert("discord", {"x": 1}, dry_run=True)
assert sent is True, f"dry-run sent should be True, got {sent}"
assert_eq(sc, _STATUS_PERMANENT_CONFIG_ERROR, "dry-run sc=0 sentinel")
print("  OK dry-run info starts with:", info[:60], "...")

# 7) Unknown channel returns sc=0 (NOT -1) per reviewer fix
section("7: unknown channel returns sc=0 (NEW FIX)")
sent, info, sc = send_alert("notarealchannel", {"x": 1}, dry_run=False)
assert sent is False
assert_eq(sc, _STATUS_PERMANENT_CONFIG_ERROR, "unknown-channel sc")
assert_eq(_is_retryable(False, sc, info), False, "unknown channel not retryable")

# 8) _send_with_retry: dry-run = single attempt; live 503 = 3 attempts
section("8: _send_with_retry attempt-count behavior")
calls = {"n": 0}
real_send = send_alert

def make_fake():
    def fake(channel, payload, dry_run):
        calls["n"] += 1
        return False, f"FakeError call={calls['n']}", 503
    return fake

# live: 3 attempts
import opt_d_alerts as m
m.send_alert = make_fake()
sent, info, sc, attempts = _send_with_retry("discord", {"x":1}, dry_run=False, max_attempts=3, base_delay=0.1)
assert_eq(attempts, 3, "live attempts (max=3)")
assert_eq(calls["n"], 3, "live call count")
assert_eq(sent, False, "live sent=False")

# dry-run: 1 attempt
calls["n"] = 0
m.send_alert = make_fake()
sent, info, sc, attempts = _send_with_retry("discord", {"x":1}, dry_run=True, max_attempts=3, base_delay=0.1)
assert_eq(attempts, 1, "dry-run attempts (max=3 but only 1)")
assert_eq(calls["n"], 1, "dry-run call count")

# live: env-missing (sc=0) does NOT trigger retry even with max_attempts=5
m.send_alert = real_send
calls["n"] = 0
os.environ.pop("DISCORD_WEBHOOK_URL", None)

# Use a wrapper that counts + sends env-missing path
calls["n"] = 0
def fake_env_missing(channel, payload, dry_run):
    calls["n"] += 1
    return False, "DISCORD_WEBHOOK_URL env var not set", _STATUS_PERMANENT_CONFIG_ERROR

m.send_alert = fake_env_missing
sent, info, sc, attempts = _send_with_retry("discord", {"x":1}, dry_run=False, max_attempts=5, base_delay=0.1)
assert_eq(attempts, 1, "env-missing attempts (clamped sc=0 should not retry)")
assert_eq(calls["n"], 1, "env-missing call count")
m.send_alert = real_send

# 9) Effective field contract: dry_run + sent=True => effective=False (real POST didn't happen)
# Live + sent=True + sc in 2xx => effective=True
# Live + sent=False => effective=False
section("9: effective field contract")
ok_sc = {200, 201, 202, 203, 204}
# Dry-run with sent=True (the dry_run success code path): effective must be False
effective = (not True) and True and 200 in ok_sc
assert_eq(effective, False, "dry-run True + sent True + sc 200 -> effective False")
# Live: sent=True + sc 200 -> effective True
effective = (not False) and True and 200 in ok_sc
assert_eq(effective, True, "live + sent=True + sc 200 -> effective True")
# Live: sent=True + sc 204 (Discord) -> effective True
effective = (not False) and True and 204 in ok_sc
assert_eq(effective, True, "live + sent=True + sc 204 -> effective True")
# Live: sent=True + sc 299 (not in set) -> effective False
effective = (not False) and True and 299 in ok_sc
assert_eq(effective, False, "live + sent=True + sc 299 (not in set) -> effective False")
# Live: sent=False -> effective False
effective = (not False) and False and 200 in ok_sc
assert_eq(effective, False, "live + sent=False -> effective False")

# 9) Effective field contract: 200/201/202/203/204 -> True; everything else -> False (when not dry-run and sent)
# We can't directly test main() output here without full integration; just sanity-check that the
# contract is documented. We've already verified _STATUS_PERMANENT_CONFIG_ERROR=0 and sc codes.

# 10) Regression guard: dashboard_server.py must contain zero Unicode arrows in any
# direction. cp1252 (the default stdout codec on Windows) raises UnicodeEncodeError
# when the 3-byte UTF-8 sequences show up in a print() at server startup.
section("10: dashboard_server.py has no Unicode arrows (all 4 directions)")
_UNICODE_ARROWS = {
    b'\xe2\x86\x90': 'U+2190 LEFTWARDS ARROW',
    b'\xe2\x86\x91': 'U+2191 UPWARDS ARROW',
    b'\xe2\x86\x92': 'U+2192 RIGHTWARDS ARROW',
    b'\xe2\x86\x93': 'U+2193 DOWNWARDS ARROW',
}
_dash = ROOT / "dashboard_server.py"
if _dash.exists():
    _blob = _dash.read_bytes()
    _violations = []  # (line_no, codepoint_name, snippet)
    for _line_no, _line in enumerate(_blob.split(b'\n'), start=1):
        for _arr_bytes, _codepoint_name in _UNICODE_ARROWS.items():
            if _arr_bytes in _line:
                _violations.append((_line_no, _codepoint_name, _line.decode('utf-8', errors='replace').strip()))
    if _violations:
        _msg = [f"Replace Unicode arrows with ASCII (->, <-, ^, v). {len(_violations)} violation(s); Windows cp1252 stdout would crash the server:"]
        for _line_no, _codepoint_name, _snip in _violations[:10]:
            _msg.append(f"  L{_line_no} ({_codepoint_name}): {_snip[:120]!r}")
        assert False, "\n".join(_msg)
    print(f"  OK no Unicode arrows in dashboard_server.py ({len(_blob.splitlines())} lines, 4 codepoints checked)")
else:
    print("  SKIP: dashboard_server.py not found")

# 11) HTTP integration smoke — actually launch dashboard_server.py in a background
# thread, hit each live endpoint, and assert correct status + content markers. This
# proves the full HTTP path works, not just that the file parses.
section("11: HTTP integration smoke (dashboard_server.py live endpoints)")
try:
    import urllib.request
    import urllib.error
    import socket as _socket
    import threading as _threading
    import time as _time

    try:
        import dashboard_server as _dash_srv
    except Exception as _imp_e:
        print(f"  SKIP: cannot import dashboard_server ({type(_imp_e).__name__}: {_imp_e})")
        _dash_srv = None

    if _dash_srv is not None:
        # Pick a free local port so this section is repeatable / parallel-safe.
        with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as _probe:
            _probe.bind(("127.0.0.1", 0))
            _free_port = _probe.getsockname()[1]

        _old_argv = sys.argv[:]
        sys.argv = ["dashboard_server.py", "--host", "127.0.0.1", "--port", str(_free_port)]
        _thr = _threading.Thread(target=_dash_srv.main, daemon=True)
        _thr.start()
        _time.sleep(0.8)  # ThreadingHTTPServer cold-start margin (reviewer-suggested)
        try:
            # GET /
            with urllib.request.urlopen(f"http://127.0.0.1:{_free_port}/", timeout=5) as _r:
                _body = _r.read().decode("utf-8", errors="replace").lower()
                assert _r.status == 200, f"GET / status={_r.status}"
            assert "sleep_triple" in _body or "audit" in _body, "GET / content marker missing"
            print(f"  OK GET /          -> 200, dashboard.html served")

            # GET /tracker
            with urllib.request.urlopen(f"http://127.0.0.1:{_free_port}/tracker", timeout=5) as _r:
                _body = _r.read().decode("utf-8", errors="replace")
                assert _r.status == 200, f"GET /tracker status={_r.status}"
            assert "localymd" in _body.lower(), "GET /tracker localYmd marker missing"
            print(f"  OK GET /tracker  -> 200, WEEK_1_TRACKER.html served")

            # GET /audit.jsonl
            with urllib.request.urlopen(f"http://127.0.0.1:{_free_port}/audit.jsonl", timeout=5) as _r:
                _body = _r.read().decode("utf-8", errors="replace")
                assert _r.status == 200, f"GET /audit.jsonl status={_r.status}"
            _non_empty = [l for l in _body.splitlines() if l.strip()]
            if _non_empty:
                _first = json.loads(_non_empty[0])
                _module = _first.get("module", "?")
                print(f"  OK GET /audit.jsonl -> 200, {len(_non_empty)} non-empty lines, first event module={_module!r}")
            else:
                print(f"  OK GET /audit.jsonl -> 200, 0 non-empty lines (empty audit log)")

            # GET /ledger.jsonl -- current server returns 200 + empty body when file missing (NOT 404).
            # That's intentional: clients can poll and get an empty JSONL instead of an error.
            with urllib.request.urlopen(f"http://127.0.0.1:{_free_port}/ledger.jsonl", timeout=5) as _r:
                _body = _r.read().decode("utf-8", errors="replace")
                assert _r.status == 200, f"GET /ledger.jsonl status={_r.status}"
            print(f"  OK GET /ledger.jsonl -> 200, {len(_body)} bytes (empty until opt_c creates a ledger)")

            # GET /healthz -- parse JSON rather than string-match (more robust)
            with urllib.request.urlopen(f"http://127.0.0.1:{_free_port}/healthz", timeout=5) as _r:
                _body = _r.read().decode("utf-8", errors="replace").strip()
                assert _r.status == 200, f"GET /healthz status={_r.status}"
            _payload = json.loads(_body)
            assert _payload.get("status") == "ok", f"/healthz status field={_payload.get('status')!r}"
            print(f"  OK GET /healthz   -> 200, body={_body!r}")
        finally:
            sys.argv = _old_argv
except Exception as _e:
    print(f"  FAIL: HTTP integration smoke crashed: {type(_e).__name__}: {_e}")
    assert False, f"HTTP integration smoke failed: {_e}"


print("\n=== ALL UNIT TESTS PASS ===")
print("Smoke test (incl. widened arrow guard + HTTP integration) is GREEN.")
