#!/usr/bin/env python3
"""두 실험 run을 DB에서 꺼내 비교한다. LLM 0 토큰."""
import json
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "collectors"))
from store import list_runs, compare_runs

METRICS = [
    ("input_tokens",   "Input Tokens",   "{:>13,}",   int),
    ("output_tokens",  "Output Tokens",  "{:>13,}",   int),
    ("cache_write",    "Cache Write",    "{:>13,}",   int),
    ("cache_read",     "Cache Read",     "{:>13,}",   int),
    ("turn_count",     "Turns",          "{:>13,}",   int),
    ("billing_usd",    "Cost (USD)",     "{:>13.5f}", float),
    ("wall_clock_sec", "Wall Clock (s)", "{:>13,}",   int),
]


def compare(id_a: int, id_b: int):
    da, db = compare_runs(id_a, id_b)
    if not da or not db:
        print(f"run {id_a} 또는 {id_b} 를 찾을 수 없습니다. 'exp list' 로 확인하세요.")
        sys.exit(1)

    W = 68
    print(f"\n{'=' * W}")
    print(f"  비교: run #{id_a} vs run #{id_b}")
    print(f"  A: {da.get('runner','?')} / {da.get('model','?')} / branch={da.get('branch','?')}")
    print(f"  B: {db.get('runner','?')} / {db.get('model','?')} / branch={db.get('branch','?')}")
    print(f"{'=' * W}")
    print(f"{'지표':<26} {'A':>13} {'B':>13} {'Delta':>14}")
    print(f"{'-' * W}")

    for key, label, fmt, cast in METRICS:
        va = cast(da.get(key) or 0)
        vb = cast(db.get(key) or 0)
        delta = vb - va
        pct = f"{delta / va * 100:+.1f}%" if va else "n/a"
        print(f"{label:<26} {fmt.format(va)} {fmt.format(vb)}  {delta:>+10.4g} ({pct})")

    print(f"{'-' * W}")
    print(f"  Compile:  A={da.get('compile_ok')}  B={db.get('compile_ok')}")
    print(f"  Tests:    A={da.get('test_summary','?')}")
    print(f"            B={db.get('test_summary','?')}")

    cost_a = float(da.get("billing_usd") or 0)
    cost_b = float(db.get("billing_usd") or 0)
    if cost_a > 0:
        pct = (cost_a - cost_b) / cost_a * 100
        label = "절감" if pct > 0 else "증가"
        print(f"\n  비용 {label}: {abs(pct):.1f}%  (${cost_a:.5f} → ${cost_b:.5f})")
    print(f"{'=' * W}\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python compare.py <run-id-a> <run-id-b>")
        sys.exit(1)
    compare(int(sys.argv[1]), int(sys.argv[2]))
