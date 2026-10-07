"""공유 경로 상수 — 표준 라이브러리만 사용 (순환 임포트 방지)."""
from pathlib import Path

EXPERIMENT_BASE = Path.home() / "Library" / "Application Support" / "experiment"
