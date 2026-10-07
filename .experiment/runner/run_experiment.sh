#!/usr/bin/env bash
# 단일 실험 실행 — 브랜치 생성 → 실험 도구 실행 → 결과 저장
# 사용법: ./run_experiment.sh <branch> <runner: claude|opencode> <task_id>
set -euo pipefail

BRANCH="${1:?branch required}"
RUNNER="${2:?runner required (claude|opencode)}"
TASK_ID="${3:?task_id required}"

PROJECT_DIR="$(git rev-parse --show-toplevel)"
RESULT_DIR="$PROJECT_DIR/.experiment/results/$BRANCH"
TASK_FILE="$PROJECT_DIR/.experiment/config/tasks.json"

mkdir -p "$RESULT_DIR"

echo "$RUNNER" > "$RESULT_DIR/runner.txt"
echo "$TASK_ID" > "$RESULT_DIR/task_id.txt"

# 브랜치 준비
git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"
git reset --hard origin/develop 2>/dev/null || true

PROMPT=$(python3 -c "
import json, sys
tasks = json.load(open('$TASK_FILE'))
task = next((t for t in tasks if t['id'] == '$TASK_ID'), None)
if not task:
    print('task not found', file=sys.stderr)
    sys.exit(1)
print(task['prompt'])
")

START_TIME=$(date +%s)

case "$RUNNER" in
  claude)
    claude --print "$PROMPT"
    # 완료 후 최신 OTel 로그 파싱
    python3 "$PROJECT_DIR/.experiment/collectors/claude_otel_parser.py" --latest \
      > "$RESULT_DIR/tokens.json"
    ;;
  opencode)
    ~/.opencode/bin/opencode --prompt "$PROMPT" --standalone
    # 완료 후 최신 세션 ID 저장 및 토큰 추출
    SESSION_ID=$(python3 "$PROJECT_DIR/.experiment/collectors/opencode_parser.py" \
      --latest "$PROJECT_DIR")
    echo "$SESSION_ID" > "$RESULT_DIR/session_id.txt"
    python3 "$PROJECT_DIR/.experiment/collectors/opencode_parser.py" "$SESSION_ID" \
      > "$RESULT_DIR/tokens.json"
    ;;
  *)
    echo "unknown runner: $RUNNER" >&2
    exit 1
    ;;
esac

END_TIME=$(date +%s)
WALL_CLOCK=$((END_TIME - START_TIME))

# 코드 품질 지표 수집
COMPILE_OK="false"
./gradlew compileJava -q 2>/dev/null && COMPILE_OK="true" || true

TEST_SUMMARY=$(./gradlew test -q 2>&1 | grep -E "tests|failures|errors" | tail -1 || echo "test not run")

python3 -c "
import json
summary = {
    'branch': '$BRANCH',
    'runner': '$RUNNER',
    'task_id': '$TASK_ID',
    'sha': '$(git rev-parse HEAD)',
    'compile': $COMPILE_OK,
    'test_summary': '$TEST_SUMMARY',
    'wall_clock_sec': $WALL_CLOCK,
}
print(json.dumps(summary, indent=2))
" > "$RESULT_DIR/summary.json"

echo "✓ 결과 저장: $RESULT_DIR"
