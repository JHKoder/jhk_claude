#!/usr/bin/env python3
"""Claude Code 세션 JSONL → turn별 usage 추출."""
import json
import sys
from pathlib import Path

P_IN    = 3.0   / 1_000_000
P_OUT   = 15.0  / 1_000_000
P_WRITE = 3.75  / 1_000_000
P_READ  = 0.30  / 1_000_000


def _proj_log_dir(project_root: str | None = None) -> Path:
    """프로젝트 경로 → Claude Code 세션 로그 디렉터리.

    Claude Code는 project_root의 '/' 와 '.' 을 '-' 로 치환한 경로를
    ~/.claude/projects/ 아래에 만든다.
    """
    if project_root is None:
        import subprocess
        try:
            project_root = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], text=True
            ).strip()
        except Exception:
            project_root = str(Path.cwd())

    slug = project_root.replace("/", "-").replace(".", "-")
    return Path.home() / ".claude" / "projects" / slug


def parse_session(session_id: str, project_root: str | None = None,
                  transcript_path: str | None = None) -> dict:
    """세션 JSONL 파싱. transcript_path 가 주어지면 그걸 직접 사용."""
    if transcript_path:
        log_file = Path(transcript_path)
    else:
        log_file = _proj_log_dir(project_root) / f"{session_id}.jsonl"

    if not log_file.exists():
        return {}

    totals = dict(input_tokens=0, output_tokens=0,
                  cache_creation_tokens=0, cache_read_tokens=0,
                  thinking_tokens=0, turn_count=0, model="")

    for line in log_file.read_text(errors="ignore").splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "assistant":
            continue
        msg = d.get("message", {})
        u = d.get("usage") or msg.get("usage") or {}
        if not u:
            continue
        totals["input_tokens"]           += u.get("input_tokens", 0)
        totals["output_tokens"]          += u.get("output_tokens", 0)
        totals["cache_creation_tokens"]  += u.get("cache_creation_input_tokens", 0)
        totals["cache_read_tokens"]      += u.get("cache_read_input_tokens", 0)
        totals["thinking_tokens"]        += u.get("thinking_tokens", 0)
        totals["turn_count"]             += 1
        if not totals["model"] and msg.get("model"):
            totals["model"] = msg["model"]

    totals["billing_cost_usd"] = (
        totals["input_tokens"]          * P_IN    +
        totals["cache_creation_tokens"] * P_WRITE +
        totals["cache_read_tokens"]     * P_READ  +
        totals["output_tokens"]         * P_OUT
    )
    return totals


def latest_session_id(project_root: str | None = None) -> str | None:
    log_dir = _proj_log_dir(project_root)
    files = sorted(log_dir.glob("*.jsonl"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0].stem if files else None


if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else latest_session_id()
    if not sid:
        print("{}")
        sys.exit(1)
    print(json.dumps(parse_session(sid)))
