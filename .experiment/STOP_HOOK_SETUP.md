# Stop Hook Setup for Quality Metrics Collection

## 개요

Claude Code 세션이 종료될 때 자동으로 품질 메트릭을 수집하려면, Stop hook을 설정해야 합니다.

## 설정 단계

### 1. Hook 스크립트 복사

```bash
mkdir -p ~/.claude/hooks
cp .experiment/hooks/collect-experiment-quality.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/collect-experiment-quality.sh
```

### 2. settings.json에 hook 등록

`~/.claude/settings.json`의 `hooks` 섹션에 다음 추가:

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "/Users/kang/.claude/hooks/collect-experiment-quality.sh",
          "async": true,
          "ignoreErrors": true
        }
      ]
    }
  ]
}
```

### 3. 검증

다음 환경변수로 Claude Code 세션 시작:

```bash
SESSION_ID="test-001" TASK_ID="task_a" claude
```

세션 종료 시 hook이 실행되고 `quality_metrics` 테이블에 데이터가 저장됩니다.

## Hook 변수

- `SESSION_ID`: Claude 세션 ID (자동 제공)
- `TASK_ID`: 테스트 작업 ID (`task_a`, `task_b`, `task_c`)

## 동작 원리

1. Claude Code 세션이 종료되면 Stop hook 트리거
2. `collect-experiment-quality.sh` 실행
3. Python 스크립트에서 `save_quality_metrics_on_stop()` 호출
4. 품질 메트릭을 `quality_metrics 테이블에 저장

## Troubleshooting

**Hook이 실행되지 않는 경우:**
1. Hook 파일이 실행 권한 있는지 확인: `chmod +x ~/.claude/hooks/collect-experiment-quality.sh`
2. settings.json 문법 검증: JSON 유효성 확인
3. `.experiment/collectors/` 경로 확인: 스크립트 내 경로 수정 필요 가능
