#!/usr/bin/env python3
"""experiment tool 버전 관리 및 업데이트 확인.

업스트림: https://github.com/JHKoder/jhk_claude
  - raw VERSION: https://raw.githubusercontent.com/JHKoder/jhk_claude/main/.experiment/VERSION

캐시 전략:
  - 캐시 위치: ~/Library/Application Support/experiment/version_cache.json
    (레포 공통 — 여러 레포에서 같은 날 각각 체크하지 않음)
  - TTL: 24h — 하루 1회만 GitHub에 요청
  - 네트워크 실패 시: 캐시의 마지막 known 값 반환 (배지 유지)
  - 캐시/네트워크 모두 없으면: has_update=False (기능 차단 안 함)
"""
import json
import time
import urllib.request
from pathlib import Path

from paths import EXPERIMENT_BASE

VERSION_FILE = Path(__file__).parent.parent / "VERSION"
UPSTREAM_URL = (
    "https://raw.githubusercontent.com/JHKoder/jhk_claude/main/.experiment/VERSION"
)
RELEASES_URL = "https://github.com/JHKoder/jhk_claude/releases"
CACHE_TTL = 86400  # 24h
TIMEOUT = 3

_CACHE_DIR = EXPERIMENT_BASE
_CACHE_FILE = _CACHE_DIR / "version_cache.json"


def local_version() -> str:
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "0.0.0"


def _parse_semver(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.lstrip("v").split(".")[:3])
    except Exception:
        return (0, 0, 0)


def _load_cache() -> dict | None:
    try:
        data = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        if time.time() - data.get("checked_at", 0) < CACHE_TTL:
            return data
    except Exception:
        pass
    return None


def _save_cache(latest: str) -> None:
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _CACHE_FILE.write_text(
            json.dumps({"checked_at": time.time(), "latest": latest}),
            encoding="utf-8",
        )
    except Exception:
        pass


def _last_known() -> str | None:
    """캐시가 만료됐어도 마지막 저장된 latest 반환 (네트워크 실패 폴백)."""
    try:
        return json.loads(_CACHE_FILE.read_text(encoding="utf-8")).get("latest")
    except Exception:
        return None


def check_update(timeout: int = TIMEOUT) -> dict:
    """업데이트 여부 반환.

    Returns:
        {
          "local": "1.2.0",
          "latest": "1.3.0" | None,
          "has_update": True | False,
          "releases_url": "...",
          "from_cache": True | False,
        }
    """
    local = local_version()
    result = {
        "local": local,
        "latest": None,
        "has_update": False,
        "releases_url": RELEASES_URL,
        "from_cache": False,
    }

    # 1. 캐시 유효하면 네트워크 건너뜀
    cached = _load_cache()
    if cached:
        result["latest"] = cached["latest"]
        result["has_update"] = _parse_semver(cached["latest"]) > _parse_semver(local)
        result["from_cache"] = True
        return result

    # 2. 네트워크 요청
    try:
        req = urllib.request.Request(UPSTREAM_URL, headers={"User-Agent": "experiment-tool/1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latest = resp.read().decode("utf-8").strip()
        _save_cache(latest)
        result["latest"] = latest
        result["has_update"] = _parse_semver(latest) > _parse_semver(local)
    except Exception:
        # 3. 네트워크 실패 — 만료 캐시의 마지막 값으로 폴백
        fallback = _last_known()
        if fallback:
            result["latest"] = fallback
            result["has_update"] = _parse_semver(fallback) > _parse_semver(local)
            result["from_cache"] = True

    return result


if __name__ == "__main__":
    print(json.dumps(check_update(), indent=2))
