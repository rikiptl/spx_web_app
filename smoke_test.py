"""
Lightweight smoke test runner for a running GEX dashboard server.

Examples:
  python smoke_test.py --base-url http://localhost:8000 --symbol SPX --strike-count 20
"""
import argparse
import json
import sys
from urllib import error, parse, request


def fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
    req = request.Request(url, headers={"Accept": "application/json"})
    with request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (external URL is user-provided)
        body = resp.read()
        content_type = resp.headers.get("Content-Type", "")
        return resp.status, body, content_type


def check_home(base_url: str, timeout: float) -> tuple[bool, str]:
    url = base_url.rstrip("/") + "/"
    try:
        status, body, _ = fetch(url, timeout)
        ok = status == 200 and b"GEX Dashboard" in body
        return ok, f"GET / (status {status})"
    except error.URLError as exc:  # pragma: no cover - network failure path
        return False, f"GET / failed: {exc}"


def check_expiries(base_url: str, symbol: str, timeout: float) -> tuple[bool, str]:
    params = parse.urlencode({"symbol": symbol})
    url = base_url.rstrip("/") + f"/api/expiries?{params}"
    try:
        status, body, content_type = fetch(url, timeout)
        ok = status == 200
        if ok and "json" in content_type:
            data = json.loads(body)
            ok = isinstance(data, dict) and bool(data.get("expiries"))
        return ok, f"GET /api/expiries (status {status})"
    except (error.URLError, json.JSONDecodeError) as exc:  # pragma: no cover - network failure path
        return False, f"GET /api/expiries failed: {exc}"


def check_mvp(base_url: str, symbol: str, strike_count: int, timeout: float) -> tuple[bool, str]:
    params = parse.urlencode({"symbol": symbol, "strike_count": strike_count})
    url = base_url.rstrip("/") + f"/api/mvp?{params}"
    try:
        status, body, content_type = fetch(url, timeout)
        ok = status == 200
        if ok and "json" in content_type:
            data = json.loads(body)
            ok = isinstance(data, dict) and "spot" in data and "live" in data
        return ok, f"GET /api/mvp (status {status})"
    except (error.URLError, json.JSONDecodeError) as exc:  # pragma: no cover - network failure path
        return False, f"GET /api/mvp failed: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test a running GEX dashboard server")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Server base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--symbol",
        nargs="?",
        default="SPX",
        const="SPX",
        help="Symbol to query (default: SPX)",
    )
    parser.add_argument("--strike-count", type=int, default=20, help="Strike count for MVP call")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout (seconds) per request")
    args = parser.parse_args()

    checks = [
        ("Home", check_home, (args.base_url, args.timeout)),
        ("Expiries", check_expiries, (args.base_url, args.symbol, args.timeout)),
        ("MVP", check_mvp, (args.base_url, args.symbol, args.strike_count, args.timeout)),
    ]

    overall_ok = True
    for name, fn, fn_args in checks:
        ok, msg = fn(*fn_args)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {msg}")
        overall_ok = overall_ok and ok

    if not overall_ok:
        print("One or more smoke tests failed. Ensure the server is running and reachable.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
