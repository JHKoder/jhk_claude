#!/usr/bin/env python3
"""
저비용 모델(Haiku)을 사용한 실험 데이터 분석 및 프롬프트 최적화 전략 생성.
- claude -p --model haiku 로 분석 (약 20× 저렴)
- config_version(root_hash) 기준으로 캐시 — 규칙 변경 시에만 재분석
- 결과는 analyses 테이블에 저장
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from store import _conn, get_config_versions, all_runs

ANALYSIS_MODEL = "haiku"


def _ensure_table():
    con = _conn()
    con.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at  TEXT NOT NULL DEFAULT (datetime('now')),
            config_hash  TEXT NOT NULL,
            model        TEXT NOT NULL,
            prompt_hash  TEXT,
            analysis_json TEXT NOT NULL,
            error        TEXT
        )
    """)
    con.commit()
    con.close()


def _get_cached(config_hash: str, run_count: int) -> dict | None:
    """config_hash + run_count 둘 다 일치할 때만 캐시 반환."""
    _ensure_table()
    cache_key = f"{config_hash}:n={run_count}"
    con = _conn()
    row = con.execute(
        "SELECT analysis_json, recorded_at, model FROM analyses "
        "WHERE config_hash=? AND error IS NULL ORDER BY id DESC LIMIT 1",
        (cache_key,)
    ).fetchone()
    con.close()
    if not row:
        return None
    try:
        return {"result": json.loads(row[0]), "recorded_at": row[1], "model": row[2], "cached": True}
    except Exception:
        return None


def _save_analysis(config_hash: str, model: str, analysis_json: str, error: str | None = None):
    _ensure_table()
    con = _conn()
    con.execute(
        "INSERT INTO analyses (config_hash, model, analysis_json, error) VALUES (?,?,?,?)",
        (config_hash, model, analysis_json, error)
    )
    con.commit()
    con.close()


def _build_prompt(runs: list[dict], config_versions: list[dict]) -> str:
    # 최근 10개로 제한 (30→10), 필드도 최소화
    recent = sorted(runs, key=lambda r: r.get("id", 0), reverse=True)[:10]

    run_rows = [
        f"{r.get('id')} turns={r.get('turn_count',0)} out={r.get('output_tokens',0)} "
        f"cache={r.get('cache_read',0)} cost=${r.get('billing_usd') or 0:.5f} "
        f"ok={int(bool(r.get('compile_ok')))} cfg={( r.get('claude_md_hash') or '')[:8]}"
        for r in recent
    ]

    # config: 파일 목록 제거, 해시+날짜+파일수만
    cfg_rows = [
        f"{v.get('root_hash','')[:8]} {(v.get('recorded_at') or '')[:10]} "
        f"files={v.get('file_count',0)} ratio={v.get('size_after',0)*100//max(v.get('size_before',1),1)}%"
        for v in config_versions[:3]
    ]

    avg_cost   = sum(r.get("billing_usd") or 0 for r in recent) / max(len(recent), 1)
    avg_output = sum(r.get("output_tokens") or 0 for r in recent) / max(len(recent), 1)
    total_cost = sum(r.get("billing_usd") or 0 for r in runs)

    prompt = (
        f"Analyze Claude Code session data. Reply ONLY valid JSON, no prose.\n"
        f"stats: runs={len(runs)} avg_out={avg_output:.0f} avg_cost=${avg_cost:.5f} total=${total_cost:.4f}\n"
        f"runs(id turns out cache cost compile cfg):\n" + "\n".join(run_rows) + "\n"
        f"configs(hash date files ratio):\n" + "\n".join(cfg_rows) + "\n"
        f'Output JSON: {{"summary":"2문장 한국어","efficiency":{{"score":1-10,"note":"한국어 1문장"}},'
        f'"top3":[{{"p":"high|mid|low","title":"한국어","save_pct":0-50}}],'
        f'"rules":[{{"f":"path","rec":"keep|trim|merge|remove"}}],'
        f'"next":"한국어 다음실험 제안 1문장"}}'
    )
    return prompt


def run_analysis(force: bool = False) -> dict:
    """
    최신 config_hash 기준으로 분석 실행.
    캐시 있으면 재사용(force=True 이면 항상 재분석).
    반환: {result, recorded_at, model, cached, config_hash, error?}
    """
    _ensure_table()
    config_versions = get_config_versions()
    runs = all_runs()

    if not runs:
        return {"error": "실험 데이터 없음", "cached": False}

    latest_hash = config_versions[0]["root_hash"] if config_versions else "no-config"
    run_count = len(runs)
    cache_key = f"{latest_hash}:n={run_count}"

    if not force:
        cached = _get_cached(latest_hash, run_count)
        if cached:
            cached["config_hash"] = latest_hash
            return cached

    prompt = _build_prompt(runs, config_versions)

    try:
        proc = subprocess.run(
            ["claude", "-p", "--model", ANALYSIS_MODEL, prompt],
            capture_output=True, text=True, timeout=120
        )
        if proc.returncode != 0:
            err = proc.stderr.strip() or f"exit {proc.returncode}"
            _save_analysis(cache_key, ANALYSIS_MODEL, "{}", err)
            return {"error": err, "cached": False, "config_hash": latest_hash}

        output = proc.stdout.strip()
        # JSON 추출 — 가끔 앞뒤에 텍스트가 붙을 수 있음
        start = output.find("{")
        end = output.rfind("}") + 1
        if start == -1 or end == 0:
            _save_analysis(latest_hash, ANALYSIS_MODEL, "{}", "JSON not found in output")
            return {"error": "모델 출력에서 JSON을 찾을 수 없음", "raw": output[:500], "cached": False, "config_hash": latest_hash}

        json_str = output[start:end]
        result = json.loads(json_str)
        _save_analysis(cache_key, ANALYSIS_MODEL, json.dumps(result, ensure_ascii=False))
        return {
            "result": result,
            "recorded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": ANALYSIS_MODEL,
            "cached": False,
            "config_hash": latest_hash,
            "run_count": run_count,
        }

    except subprocess.TimeoutExpired:
        _save_analysis(cache_key, ANALYSIS_MODEL, "{}", "timeout after 120s")
        return {"error": "분석 타임아웃 (120s)", "cached": False, "config_hash": latest_hash}
    except json.JSONDecodeError as e:
        _save_analysis(cache_key, ANALYSIS_MODEL, "{}", f"JSON parse error: {e}")
        return {"error": f"JSON 파싱 실패: {e}", "cached": False, "config_hash": latest_hash}
    except FileNotFoundError:
        return {"error": "claude CLI를 찾을 수 없음", "cached": False, "config_hash": latest_hash}


def get_analysis_history(limit: int = 20) -> list[dict]:
    """성공한 분석 이력 반환 (최신순)."""
    _ensure_table()
    con = _conn()
    rows = con.execute(
        "SELECT id, recorded_at, config_hash, model FROM analyses "
        "WHERE error IS NULL ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    con.close()
    result = []
    for row in rows:
        raw_key = row[2]
        config_hash = raw_key.split(":")[0]
        run_count = int(raw_key.split("n=")[1]) if "n=" in raw_key else None
        result.append({
            "id": row[0],
            "recorded_at": row[1],
            "config_hash": config_hash,
            "run_count": run_count,
            "model": row[3],
        })
    return result


def get_analysis_by_id(analysis_id: int) -> dict | None:
    """특정 분석 결과 반환."""
    _ensure_table()
    con = _conn()
    row = con.execute(
        "SELECT id, recorded_at, config_hash, model, analysis_json FROM analyses "
        "WHERE id=? AND error IS NULL", (analysis_id,)
    ).fetchone()
    con.close()
    if not row:
        return None
    try:
        raw_key = row[2]
        config_hash = raw_key.split(":")[0]
        run_count = int(raw_key.split("n=")[1]) if "n=" in raw_key else None
        return {
            "id": row[0],
            "recorded_at": row[1],
            "config_hash": config_hash,
            "run_count": run_count,
            "model": row[3],
            "result": json.loads(row[4]),
        }
    except Exception:
        return None


def get_latest_analysis() -> dict | None:
    """DB에서 가장 최근 성공 분석 결과 반환."""
    _ensure_table()
    con = _conn()
    row = con.execute(
        "SELECT analysis_json, recorded_at, model, config_hash FROM analyses "
        "WHERE error IS NULL ORDER BY id DESC LIMIT 1"
    ).fetchone()
    con.close()
    if not row:
        return None
    try:
        raw_key = row[3]  # "hash:n=N" 또는 구 포맷 "hash"
        config_hash = raw_key.split(":")[0]
        run_count = int(raw_key.split("n=")[1]) if "n=" in raw_key else None
        return {
            "result": json.loads(row[0]),
            "recorded_at": row[1],
            "model": row[2],
            "config_hash": config_hash,
            "run_count": run_count,
            "cached": True,
        }
    except Exception:
        return None


if __name__ == "__main__":
    force = "--force" in sys.argv
    print(f"[analyzer] 분석 시작 (model={ANALYSIS_MODEL}, force={force})", file=sys.stderr)
    out = run_analysis(force=force)
    if "error" in out:
        print(f"[analyzer] 오류: {out['error']}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(out["result"], ensure_ascii=False, indent=2))
    print(f"\n[analyzer] {'캐시됨' if out.get('cached') else '신규 분석'} | model={out['model']} | config={out.get('config_hash','?')}", file=sys.stderr)
