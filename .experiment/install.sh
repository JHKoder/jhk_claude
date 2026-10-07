#!/usr/bin/env bash
# .experiment/install.sh — 클론 후 1회 실행으로 모든 설정 완료
#
# 수행 작업:
#   1. python3 존재 확인
#   2. .claude/hooks/collect_experiment.sh 배치
#   3. .claude/settings.json 에 Stop hook 등록 (idempotent)
#   4. exp CLI를 PATH에 등록 (~/.zshrc 또는 ~/.bashrc)
#   5. runner_config.json 이미 있으면 건드리지 않음
set -euo pipefail

EXP_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$EXP_DIR/.." && pwd)"
HOOK_SRC="$EXP_DIR/hooks/collect_experiment.sh"
HOOK_DST="$PROJECT_DIR/.claude/hooks/collect_experiment.sh"
SETTINGS="$PROJECT_DIR/.claude/settings.json"

# ── 색상 출력 ───────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GREEN}  ✓${NC} $1"; }
warn() { echo -e "${YELLOW}  !${NC} $1"; }
fail() { echo -e "${RED}  ✗${NC} $1"; exit 1; }

echo ""
echo "  experiment tool 설치"
echo "  프로젝트: $PROJECT_DIR"
echo ""

# ── 1. python3 확인 ─────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    fail "python3 를 찾을 수 없습니다. 설치 후 다시 실행하세요."
fi
ok "python3 $(python3 --version 2>&1 | awk '{print $2}')"

# ── 2. .claude 디렉터리 ─────────────────────────────────────────────
mkdir -p "$PROJECT_DIR/.claude/hooks"
ok ".claude/hooks 디렉터리 확인"

# ── 3. Stop hook 스크립트 배치 ──────────────────────────────────────
# hook 소스는 .claude/hooks/collect_experiment.sh 에 이미 있음
# (이 repo를 클론하면 바로 존재)
if [[ -f "$HOOK_DST" ]]; then
    ok "Stop hook 이미 존재: .claude/hooks/collect_experiment.sh"
else
    # .experiment/hooks/ 에 복사본이 있으면 사용, 없으면 에러
    if [[ -f "$EXP_SRC_HOOK" ]]; then
        cp "$EXP_SRC_HOOK" "$HOOK_DST"
        chmod +x "$HOOK_DST"
        ok "Stop hook 배치: .claude/hooks/collect_experiment.sh"
    else
        warn "Stop hook을 찾을 수 없습니다. .claude/hooks/collect_experiment.sh 를 수동 생성하세요."
    fi
fi
chmod +x "$HOOK_DST" 2>/dev/null || true

# ── 4. Stop hook 등록 — 프로젝트 + 전역 양쪽 ──────────────────────
HOOK_CMD="\$CLAUDE_PROJECT_DIR/.claude/hooks/collect_experiment.sh"
GLOBAL_SETTINGS="$HOME/.claude/settings.json"

_register_hook() {
    local target="$1"
    local cmd="$2"
    if [[ ! -f "$target" ]]; then
        mkdir -p "$(dirname "$target")"
        cat > "$target" <<JSON
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$cmd",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
JSON
        return 0
    fi
    python3 - "$target" "$cmd" <<'PYEOF'
import json, sys
from pathlib import Path
target, cmd = Path(sys.argv[1]), sys.argv[2]
try:
    s = json.loads(target.read_text())
except Exception:
    s = {}
stop = s.setdefault("hooks", {}).setdefault("Stop", [])
already = any(
    any("collect_experiment" in h.get("command","") for h in e.get("hooks",[]))
    for e in stop
)
if not already:
    stop.append({"hooks":[{"type":"command","command":cmd,"timeout":120}]})
    target.write_text(json.dumps(s, indent=2, ensure_ascii=False))
    print("added")
else:
    print("exists")
PYEOF
}

# 프로젝트 로컬 settings.json
RESULT=$(_register_hook "$SETTINGS" "$HOOK_CMD" 2>&1)
ok "프로젝트 settings.json Stop hook 등록 ($RESULT)"

# 전역 ~/.claude/settings.json — 어느 레포에서도 수집 가능
GLOBAL_HOOK_CMD="$EXP_DIR/collectors/../collect_experiment_global.sh"
# 전역 훅은 EXP_DIR 절대경로를 쓰는 래퍼를 생성
GLOBAL_HOOK_FILE="$HOME/.claude/hooks/collect_experiment_global.sh"
mkdir -p "$HOME/.claude/hooks"
cat > "$GLOBAL_HOOK_FILE" <<SH
#!/usr/bin/env bash
# 전역 Stop Hook — 어느 레포에서든 .experiment/ 가 있으면 수집
set -euo pipefail
INPUT=\$(cat)
PROJECT_DIR="\$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
LOCAL_HOOK="\$PROJECT_DIR/.claude/hooks/collect_experiment.sh"
if [[ -f "\$LOCAL_HOOK" ]]; then
    echo "\$INPUT" | bash "\$LOCAL_HOOK"
fi
SH
chmod +x "$GLOBAL_HOOK_FILE"

GLOBAL_RESULT=$(_register_hook "$GLOBAL_SETTINGS" "$GLOBAL_HOOK_FILE" 2>&1)
ok "전역 ~/.claude/settings.json Stop hook 등록 ($GLOBAL_RESULT)"

# ── 5. exp CLI PATH 등록 ────────────────────────────────────────────
SHELL_RC=""
if [[ -f "$HOME/.zshrc" ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -f "$HOME/.bashrc" ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

EXP_PATH_LINE="export PATH=\"\$PATH:$EXP_DIR\""

if [[ -n "$SHELL_RC" ]]; then
    if grep -q "experiment" "$SHELL_RC" 2>/dev/null; then
        ok "exp PATH 이미 등록됨 ($SHELL_RC)"
    else
        echo "" >> "$SHELL_RC"
        echo "# experiment tool" >> "$SHELL_RC"
        echo "$EXP_PATH_LINE" >> "$SHELL_RC"
        ok "exp PATH 등록: $SHELL_RC"
        warn "  → 반영: source $SHELL_RC  (또는 터미널 재시작)"
    fi
else
    warn "쉘 설정 파일을 찾지 못했습니다. 수동으로 PATH에 추가하세요:"
    echo "    $EXP_PATH_LINE"
fi

# ── 6. runner_config.json 안내 ──────────────────────────────────────
echo ""
if [[ -f "$EXP_DIR/runner_config.json" ]]; then
    COMPILE_CMD=$(python3 -c "
import json, os
cfg = json.load(open('$EXP_DIR/runner_config.json'))
v = cfg.get('compile')
print(v if v else 'SKIP (null)')
" 2>/dev/null || echo "확인 불가")
    TEST_CMD=$(python3 -c "
import json, os
cfg = json.load(open('$EXP_DIR/runner_config.json'))
v = cfg.get('test')
print(v if v else 'SKIP (null)')
" 2>/dev/null || echo "확인 불가")
    ok "runner_config.json 현재 설정:"
    echo "     compile : $COMPILE_CMD"
    echo "     test    : $TEST_CMD"
    echo ""
    echo "  다른 팀/언어 예시는 runner_config.json 의 _examples 참고"
fi

echo ""
echo "  설치 완료. 이제 Claude Code 세션이 끝날 때마다 자동 수집됩니다."
echo ""
echo "  대시보드 실행:"
echo "    exp serve"
echo ""
