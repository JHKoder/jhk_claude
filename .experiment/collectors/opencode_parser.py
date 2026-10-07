#!/usr/bin/env python3
"""opencode SQLite에서 세션 토큰 데이터 추출."""
import sqlite3
import json
import sys

DB = "/Users/kang/.local/share/opencode/opencode.db"


def get_session_tokens(session_id: str) -> dict:
    con = sqlite3.connect(DB)
    row = con.execute(
        """
        SELECT tokens_input, tokens_output, tokens_reasoning,
               tokens_cache_read, tokens_cache_write, cost, model
        FROM session_v2
        WHERE id = ?
        """,
        (session_id,),
    ).fetchone()
    con.close()

    if not row:
        return {}

    return {
        "input_tokens": row[0] or 0,
        "output_tokens": row[1] or 0,
        "thinking_tokens": row[2] or 0,
        "cache_read_tokens": row[3] or 0,
        "cache_creation_tokens": row[4] or 0,
        "billing_cost_usd": row[5] or 0.0,
        "model": json.loads(row[6]).get("id", "unknown") if row[6] else "unknown",
    }


def get_latest_session(project_dir: str) -> str | None:
    con = sqlite3.connect(DB)
    row = con.execute(
        """
        SELECT id FROM session_v2
        WHERE directory = ?
        ORDER BY time_updated DESC LIMIT 1
        """,
        (project_dir,),
    ).fetchone()
    con.close()
    return row[0] if row else None


def get_all_sessions(project_dir: str) -> list[dict]:
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT id, tokens_input, tokens_output, tokens_reasoning,
               tokens_cache_read, tokens_cache_write, cost, model, time_updated
        FROM session_v2
        WHERE directory = ?
        ORDER BY time_updated DESC
        """,
        (project_dir,),
    ).fetchall()
    con.close()

    return [
        {
            "session_id": r[0],
            "input_tokens": r[1] or 0,
            "output_tokens": r[2] or 0,
            "thinking_tokens": r[3] or 0,
            "cache_read_tokens": r[4] or 0,
            "cache_creation_tokens": r[5] or 0,
            "billing_cost_usd": r[6] or 0.0,
            "model": json.loads(r[7]).get("id", "unknown") if r[7] else "unknown",
            "time_updated": r[8],
        }
        for r in rows
    ]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: opencode_parser.py <session_id|--latest <dir>|--list <dir>>")
        sys.exit(1)

    if sys.argv[1] == "--latest":
        sid = get_latest_session(sys.argv[2])
        print(sid or "no session found")
    elif sys.argv[1] == "--list":
        sessions = get_all_sessions(sys.argv[2])
        print(json.dumps(sessions, indent=2))
    else:
        result = get_session_tokens(sys.argv[1])
        print(json.dumps(result))
