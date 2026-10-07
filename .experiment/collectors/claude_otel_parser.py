#!/usr/bin/env python3
"""Claude Code OTel JSONL 로그에서 세션 토큰 데이터 추출."""
import json
import sys
from pathlib import Path

# Sonnet 4.6 단가 (per token)
P_IN = 3.0 / 1_000_000
P_OUT = 15.0 / 1_000_000
P_WRITE = 3.75 / 1_000_000
P_READ = 0.30 / 1_000_000


def parse_session_log(log_path: str) -> dict:
    totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "thinking_tokens": 0,
        "turn_count": 0,
    }

    for line in Path(log_path).read_text(errors="ignore").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        usage = (
            event.get("usage")
            or event.get("message", {}).get("usage", {})
            or {}
        )
        if not usage:
            continue

        totals["input_tokens"] += usage.get("input_tokens", 0)
        totals["output_tokens"] += usage.get("output_tokens", 0)
        totals["cache_creation_tokens"] += usage.get("cache_creation_input_tokens", 0)
        totals["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
        totals["thinking_tokens"] += usage.get("thinking_tokens", 0)
        totals["turn_count"] += 1

    totals["billing_cost_usd"] = (
        totals["input_tokens"] * P_IN
        + totals["cache_creation_tokens"] * P_WRITE
        + totals["cache_read_tokens"] * P_READ
        + totals["output_tokens"] * P_OUT
    )
    totals["model"] = "claude-sonnet-4-6"

    print(json.dumps(totals))


def find_latest_log() -> str | None:
    log_dir = Path.home() / ".claude" / "logs"
    logs = sorted(log_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    return str(logs[0]) if logs else None


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--latest":
        log = find_latest_log()
        if not log:
            print("{}")
            sys.exit(1)
        parse_session_log(log)
    else:
        parse_session_log(sys.argv[1])
