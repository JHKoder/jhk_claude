#!/usr/bin/env python3
"""
.claude/ + CLAUDE.md 의 규칙 파일을 content-addressed 스냅샷으로 저장한다.
- 제외: settings.local.json (로컬 권한), agent/agent_live.md (라이브 상태), .experiment/
- 루트 해시: SHA-256(sorted manifest) → 16자 짧은 태그 (git short-hash 유사)
"""
import hashlib
import json
import os
import zlib
from pathlib import Path


def _repo_root() -> Path:
    """git rev-parse --show-toplevel; 실패 시 이 파일 기준 3단계 위."""
    try:
        import subprocess
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        return Path(out)
    except Exception:
        return Path(__file__).parent.parent.parent


REPO_ROOT = _repo_root()

INCLUDE_DIRS = [
    REPO_ROOT / ".claude" / "rules",
    REPO_ROOT / ".claude" / "hooks",
    REPO_ROOT / ".claude" / "skills",
]
INCLUDE_FILES = [
    REPO_ROOT / "CLAUDE.md",
    REPO_ROOT / ".claude" / "settings.json",
    REPO_ROOT / ".claude" / "README.md",
]

EXCLUDE_NAMES = {"settings.local.json", "agent_live.md"}


def _should_include(path: Path) -> bool:
    if path.name in EXCLUDE_NAMES:
        return False
    if not path.is_file():
        return False
    try:
        path.relative_to(REPO_ROOT / ".experiment")
        return False
    except ValueError:
        pass
    return True


def collect_files() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for f in INCLUDE_FILES:
        if _should_include(f):
            key = f.relative_to(REPO_ROOT).as_posix()
            result[key] = f.read_bytes()
    for d in INCLUDE_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.rglob("*")):
            if _should_include(f):
                key = f.relative_to(REPO_ROOT).as_posix()
                result[key] = f.read_bytes()
    return dict(sorted(result.items()))


def compute_snapshot() -> dict:
    files = collect_files()
    manifest: dict[str, str] = {}
    raw_parts: list[bytes] = []

    for rel, content in files.items():
        file_hash = hashlib.sha256(content).hexdigest()
        manifest[rel] = file_hash
        raw_parts.append(f"=== {rel} ===\n".encode() + content + b"\n")

    manifest_json = json.dumps(manifest, sort_keys=True, ensure_ascii=False)
    root_hash = hashlib.sha256(manifest_json.encode()).hexdigest()[:16]

    raw_bytes = b"\n".join(raw_parts)
    blob = zlib.compress(raw_bytes, level=9)

    return {
        "root_hash": root_hash,
        "manifest": manifest,
        "blob": blob,
        "size_before": len(raw_bytes),
        "size_after": len(blob),
        "file_count": len(files),
    }


def diff_manifests(prev: dict[str, str], cur: dict[str, str]) -> dict:
    added    = sorted(set(cur) - set(prev))
    removed  = sorted(set(prev) - set(cur))
    modified = sorted(k for k in (set(prev) & set(cur)) if prev[k] != cur[k])
    return {"added": added, "modified": modified, "removed": removed}


def save_snapshot() -> dict:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from store import save_config_version
    snap = compute_snapshot()
    is_new = save_config_version(
        root_hash=snap["root_hash"],
        manifest_json=json.dumps(snap["manifest"], sort_keys=True, ensure_ascii=False),
        compressed=snap["blob"],
        size_before=snap["size_before"],
        size_after=snap["size_after"],
        file_count=snap["file_count"],
    )
    snap["is_new"] = is_new
    return snap


if __name__ == "__main__":
    snap = compute_snapshot()
    print(f"root_hash  : {snap['root_hash']}")
    print(f"files      : {snap['file_count']}")
    print(f"size before: {snap['size_before']:,} bytes")
    print(f"size after : {snap['size_after']:,} bytes  ({snap['size_after']/snap['size_before']*100:.1f}%)")
    print("\nmanifest:")
    for k, v in snap["manifest"].items():
        print(f"  {v[:12]}  {k}")
