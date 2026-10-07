#!/usr/bin/env python3
"""실험 결과를 SQLite DB에 적재·조회한다.

DB 위치: ~/Library/Application Support/experiment/<repo-key>/experiment.db
  repo-key = <basename>-<path-hash-8> (두 레포가 같은 이름이어도 구분됨)
  EXPERIMENT_DB_PATH 환경변수로 덮어쓸 수 있음 (테스트·구버전 마이그레이션용)
"""
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

from paths import EXPERIMENT_BASE


def _repo_key(project_root: Path | None = None) -> str:
    """레포 식별 키: <basename>-<path-hash-8>"""
    if project_root is None:
        try:
            import subprocess
            out = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                text=True, stderr=subprocess.DEVNULL,
            ).strip()
            project_root = Path(out)
        except Exception:
            project_root = Path.cwd()
    name = project_root.name
    h = hashlib.sha256(str(project_root).encode()).hexdigest()[:8]
    return f"{name}-{h}"


def _db_path(project_root: Path | None = None) -> Path:
    override = os.environ.get("EXPERIMENT_DB_PATH")
    if override:
        return Path(override)
    key = _repo_key(project_root)
    base = EXPERIMENT_BASE / key
    base.mkdir(parents=True, exist_ok=True)
    return base / "experiment.db"


def _data_dir(project_root: Path | None = None) -> Path:
    return _db_path(project_root).parent


# 호출 시점의 레포 기준 DB (모듈 로드 후 최초 1회)
DB_PATH = _db_path()


def _conn(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=3000")
    con.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at       TEXT    NOT NULL DEFAULT (datetime('now')),
            session_id        TEXT    NOT NULL,
            runner            TEXT    NOT NULL,
            branch            TEXT,
            model             TEXT,
            input_tokens      INTEGER DEFAULT 0,
            output_tokens     INTEGER DEFAULT 0,
            cache_write       INTEGER DEFAULT 0,
            cache_read        INTEGER DEFAULT 0,
            thinking_tokens   INTEGER DEFAULT 0,
            turn_count        INTEGER DEFAULT 0,
            billing_usd       REAL    DEFAULT 0,
            wall_clock_sec    INTEGER DEFAULT 0,
            compile_ok        INTEGER DEFAULT 0,
            test_pass_rate    REAL    DEFAULT NULL,
            test_summary      TEXT,
            changed_files_cnt INTEGER DEFAULT 0,
            added_lines       INTEGER DEFAULT 0,
            deleted_lines     INTEGER DEFAULT 0,
            claude_md_hash    TEXT,
            rating            INTEGER DEFAULT NULL,
            notes             TEXT
        );

        CREATE TABLE IF NOT EXISTS claude_md_snapshots (
            hash        TEXT PRIMARY KEY,
            recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
            content     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS config_versions (
            root_hash     TEXT PRIMARY KEY,
            recorded_at   TEXT NOT NULL DEFAULT (datetime('now')),
            manifest_json TEXT NOT NULL,
            compressed    BLOB NOT NULL,
            size_before   INTEGER NOT NULL DEFAULT 0,
            size_after    INTEGER NOT NULL DEFAULT 0,
            file_count    INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS quality_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL UNIQUE,
            task_id TEXT NOT NULL,
            accuracy REAL,
            first_pass INTEGER,
            revision_count INTEGER,
            complexity_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES runs(session_id)
        );
    """)
    con.commit()

    # 기존 DB 마이그레이션 (컬럼 누락 시 추가)
    existing = {r[1] for r in con.execute("PRAGMA table_info(runs)").fetchall()}
    for col, definition in [
        ("test_pass_rate",    "REAL    DEFAULT NULL"),
        ("changed_files_cnt", "INTEGER DEFAULT 0"),
        ("added_lines",       "INTEGER DEFAULT 0"),
        ("deleted_lines",     "INTEGER DEFAULT 0"),
        ("claude_md_hash",    "TEXT"),
        ("rating",            "INTEGER DEFAULT NULL"),
    ]:
        if col not in existing:
            con.execute(f"ALTER TABLE runs ADD COLUMN {col} {definition}")
    con.commit()
    return con


def save_claude_md_snapshot(hash_val: str, content: str):
    con = _conn()
    con.execute(
        "INSERT OR IGNORE INTO claude_md_snapshots (hash, content) VALUES (?,?)",
        (hash_val, content),
    )
    con.commit()
    con.close()


def insert(
    session_id: str,
    runner: str,
    tokens: dict,
    branch: str = "",
    wall_clock: int = 0,
    compile_ok: bool = False,
    test_pass_rate: float | None = None,
    test_summary: str = "",
    changed_files_cnt: int = 0,
    added_lines: int = 0,
    deleted_lines: int = 0,
    claude_md_hash: str = "",
    notes: str = "",
) -> int:
    con = _conn()
    cur = con.execute(
        """
        INSERT INTO runs (
            session_id, runner, branch, model,
            input_tokens, output_tokens, cache_write, cache_read,
            thinking_tokens, turn_count, billing_usd,
            wall_clock_sec, compile_ok, test_pass_rate, test_summary,
            changed_files_cnt, added_lines, deleted_lines,
            claude_md_hash, notes
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            session_id, runner, branch,
            tokens.get("model", ""),
            tokens.get("input_tokens", 0),
            tokens.get("output_tokens", 0),
            tokens.get("cache_creation_tokens", 0),
            tokens.get("cache_read_tokens", 0),
            tokens.get("thinking_tokens", 0),
            tokens.get("turn_count", 0),
            tokens.get("billing_cost_usd", 0.0),
            wall_clock, int(compile_ok),
            test_pass_rate, test_summary,
            changed_files_cnt, added_lines, deleted_lines,
            claude_md_hash, notes,
        ),
    )
    con.commit()
    row_id = cur.lastrowid
    con.close()
    return row_id


def rate_run(run_id: int, score: int):
    con = _conn()
    con.execute("UPDATE runs SET rating=? WHERE id=?", (score, run_id))
    con.commit()
    con.close()


def _rows_to_dicts(cur, rows) -> list[dict]:
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def all_runs() -> list[dict]:
    con = _conn()
    cur = con.execute("SELECT * FROM runs ORDER BY id DESC")
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    con.close()
    return result


def list_runs(limit: int = 50) -> list[dict]:
    con = _conn()
    cur = con.execute(
        "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    con.close()
    return [dict(zip(cols, r)) for r in rows]


def compare_runs(id_a: int, id_b: int) -> tuple[dict, dict]:
    con = _conn()
    def fetch(rid):
        cur = con.execute("SELECT * FROM runs WHERE id=?", (rid,))
        row = cur.fetchone()
        if not row:
            return {}
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))
    a, b = fetch(id_a), fetch(id_b)
    con.close()
    return a, b


def get_claude_md_snapshots() -> list[dict]:
    con = _conn()
    rows = con.execute(
        "SELECT hash, recorded_at FROM claude_md_snapshots ORDER BY recorded_at"
    ).fetchall()
    con.close()
    return [{"hash": r[0], "recorded_at": r[1]} for r in rows]


def save_config_version(root_hash: str, manifest_json: str, compressed: bytes,
                        size_before: int, size_after: int, file_count: int) -> bool:
    """저장 시 True, 이미 존재(중복) 시 False"""
    con = _conn()
    cur = con.execute(
        "INSERT OR IGNORE INTO config_versions "
        "(root_hash, manifest_json, compressed, size_before, size_after, file_count) "
        "VALUES (?,?,?,?,?,?)",
        (root_hash, manifest_json, compressed, size_before, size_after, file_count),
    )
    con.commit()
    is_new = cur.rowcount > 0
    con.close()
    return is_new


def get_config_versions() -> list[dict]:
    con = _conn()
    cur = con.execute(
        "SELECT root_hash, recorded_at, manifest_json, size_before, size_after, file_count "
        "FROM config_versions ORDER BY recorded_at DESC"
    )
    rows = cur.fetchall()
    result = _rows_to_dicts(cur, rows)
    con.close()
    return result


def get_config_version(root_hash: str) -> dict | None:
    con = _conn()
    cur = con.execute(
        "SELECT root_hash, recorded_at, manifest_json, compressed, size_before, size_after, file_count "
        "FROM config_versions WHERE root_hash=?", (root_hash,)
    )
    row = cur.fetchone()
    if not row:
        con.close()
        return None
    result = dict(zip([d[0] for d in cur.description], row))
    con.close()
    return result


# ─────────────────────────────────────────────────────────────
# 멀티 레포 집계 (dashboard server용)
# ─────────────────────────────────────────────────────────────

def _all_repo_dbs() -> list[tuple[str, Path]]:
    """~/Library/Application Support/experiment/ 아래 모든 레포 DB를 반환.
    반환값: [(repo_label, db_path), ...]
    """
    base = EXPERIMENT_BASE
    if not base.exists():
        return []
    results = []
    for d in sorted(base.iterdir()):
        db = d / "experiment.db"
        if db.exists():
            results.append((d.name, db))
    return results


def all_runs_multi() -> list[dict]:
    """모든 레포의 runs를 합쳐 반환. 각 row에 'project' 키 추가."""
    repos = _all_repo_dbs()
    if not repos:
        # fallback: 현재 레포만
        rows = all_runs()
        label = _repo_key()
        for r in rows:
            r.setdefault("project", label)
        return rows

    merged = []
    for label, db_path in repos:
        try:
            con = _conn(db_path)
            cur = con.execute("SELECT * FROM runs ORDER BY id DESC")
            rows = _rows_to_dicts(cur, cur.fetchall())
            con.close()
            for r in rows:
                r["project"] = label
            merged.extend(rows)
        except Exception:
            pass
    merged.sort(key=lambda r: r.get("recorded_at", ""), reverse=True)
    return merged


def repo_labels() -> list[str]:
    """집계 가능한 레포 키 목록."""
    repos = _all_repo_dbs()
    if not repos:
        return [_repo_key()]
    return [label for label, _ in repos]


def init_quality_metrics_table():
    """품질 메트릭 테이블 초기화"""
    con = _conn()
    migrations_dir = Path(__file__).parent.parent / "schema_migrations"
    migration_file = migrations_dir / "001_add_quality_metrics.sql"
    if migration_file.exists():
        with open(migration_file) as f:
            con.executescript(f.read())
        con.commit()
    con.close()


def insert_quality_metric(session_id: str, task_id: str, accuracy: float | None = None,
                         first_pass: int | None = None, revision_count: int | None = None,
                         complexity_score: float | None = None) -> int:
    """품질 메트릭 저장"""
    con = _conn()
    cur = con.execute("""
        INSERT OR REPLACE INTO quality_metrics
        (session_id, task_id, accuracy, first_pass, revision_count, complexity_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, task_id, accuracy, first_pass, revision_count, complexity_score))
    con.commit()
    row_id = cur.lastrowid
    con.close()
    return row_id


def save_quality_metrics_on_stop(session_id: str, task_id: str) -> int | None:
    """Stop 시점에 품질 메트릭 저장"""
    import importlib.util
    from pathlib import Path as _Path

    _qm_path = _Path(__file__).parent.parent / "quality_metrics.py"
    spec = importlib.util.spec_from_file_location("quality_metrics", _qm_path)
    qm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qm)

    tasks_path = _Path(__file__).parent.parent / "config" / "tasks.json"
    with open(tasks_path) as f:
        task_config = next(
            (t for t in json.load(f)["tasks"] if t["id"] == task_id),
            None,
        )

    if not task_config:
        return None

    quality = qm.evaluate_session(
        session_id,
        task_id,
        task_config["repo"],
        "python -m pytest tests/ -v",
        task_config["test_count"],
    )
    return insert_quality_metric(
        quality["session_id"],
        quality["task_id"],
        quality["accuracy"],
        quality["first_pass"],
        quality["revision_count"],
        quality["complexity_score"],
    )


def get_quality_metrics(session_id: str) -> dict | None:
    """세션별 품질 메트릭 조회"""
    con = _conn()
    cur = con.execute("SELECT * FROM quality_metrics WHERE session_id = ?", (session_id,))
    row = cur.fetchone()
    if not row:
        con.close()
        return None
    cols = [d[0] for d in cur.description]
    result = dict(zip(cols, row))
    con.close()
    return result


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        for r in list_runs():
            print(json.dumps(r, ensure_ascii=False))
    elif cmd == "compare" and len(sys.argv) == 4:
        a, b = compare_runs(int(sys.argv[2]), int(sys.argv[3]))
        print(json.dumps({"a": a, "b": b}, ensure_ascii=False, indent=2))
    elif cmd == "repos":
        for label, path in _all_repo_dbs():
            print(f"{label}  →  {path}")
