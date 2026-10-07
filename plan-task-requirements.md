# Claude 하네스 엔지니어링 — 모든 Task 통일 요구사항

> 6개 Task는 동일한 요구사항 프레임워크를 따릅니다

---

## 📋 모든 Task 공통 요구사항

### 1️⃣ 입력 (Input)
**각 Task는 동일한 입력을 받습니다**

```json
{
  "input_files": [
    "/Users/kang/.claude/CLAUDE.md",
    "/Users/kang/.claude/settings.json"
  ],
  "task_context": {
    "baseline_metrics": ".claude-harness-analysis/baseline-metrics.json",
    "previous_variant": "N/A (Task 1) 또는 .claude-harness-analysis/variant-X-*.md"
  },
  "config": {
    "token_baseline": 3640,
    "clarity_baseline": 72,
    "target_reduction": "≥1.5%"
  }
}
```

### 2️⃣ 프로세스 (Process)
**모든 Task는 5단계를 따릅니다**

| 단계 | 작업 | 산출물 | 시간 |
|------|------|--------|------|
| **P1** | 분석 | 문제/기회 식별 | 20% |
| **P2** | 설계 | 솔루션 설계 | 20% |
| **P3** | 구현 | 코드/설정 작성 | 40% |
| **P4** | 테스트 | 검증 및 측정 | 15% |
| **P5** | 문서화 | 보고서 + 메트릭 | 5% |

### 3️⃣ 산출물 (Output)
**모든 Task는 동일한 산출물 구조를 생성합니다**

```
.claude-harness-analysis/
├── logs/task-N.log                    # 실행 로그
├── metrics/task-N-metrics.json        # 메트릭 JSON
├── reports/task-N-report.md           # 완료 보고서
├── variant-N-claude.md (또는 settings.json)  # 결과물
└── variant-N-notes.md                 # 상세 설명
```

### 4️⃣ 검증 (Validation)
**모든 Task는 동일한 검증을 통과해야 합니다**

```bash
# V1: 파일 존재
[ -f "logs/task-N.log" ] && \
[ -f "metrics/task-N-metrics.json" ] && \
[ -f "reports/task-N-report.md" ] || exit 1

# V2: JSON 유효성
jq . metrics/task-N-metrics.json > /dev/null || exit 1

# V3: 메트릭 존재
jq '.metrics.token_cost' metrics/task-N-metrics.json > /dev/null || exit 1

# V4: Markdown 렌더링
grep -q "^#" "reports/task-N-report.md" || exit 1

# V5: Git 커밋
git log --oneline | grep "task-N" > /dev/null || exit 1
```

### 5️⃣ 메트릭 (Metrics)
**모든 Task는 동일한 메트릭을 보고합니다**

```json
{
  "task_id": "task-N",
  "timestamp": "2026-10-07T10:30:00Z",
  "duration_minutes": 45,
  "status": "completed",
  
  "metrics": {
    "token_cost": 3640,
    "token_change": -54,
    "token_percent": -1.5,
    "clarity_score": 86,
    "clarity_change": 14,
    "lines_of_code": 24,
    "lines_change": -2,
    "word_count": 354,
    "word_change": -31,
    "undefined_terms": 0,
    "undefined_change": -7
  },
  
  "quality_scores": {
    "completeness": 100,
    "correctness": 100,
    "performance": 95,
    "documentation": 100
  },
  
  "deliverables": {
    "log": ".claude-harness-analysis/logs/task-N.log",
    "metrics": ".claude-harness-analysis/metrics/task-N-metrics.json",
    "report": ".claude-harness-analysis/reports/task-N-report.md",
    "artifact": ".claude-harness-analysis/variant-N-claude.md",
    "notes": ".claude-harness-analysis/variant-N-notes.md"
  },
  
  "git_info": {
    "commit_hash": "abc1234",
    "commit_message": "feat: task-N description",
    "files_changed": 5,
    "insertions": 200,
    "deletions": 50
  }
}
```

### 6️⃣ 보고서 (Report)
**모든 Task는 동일한 보고서 포맷을 사용합니다**

```markdown
# Task N: [이름]

## 📊 메트릭

| 항목 | 기준점 | 변경 후 | 변화 |
|------|--------|--------|------|
| Token Cost | 3640 | 3586 | -54 (-1.5%) |
| Clarity | 72/100 | 86/100 | +14 (+19%) |
| Lines | 26 | 24 | -2 (-8%) |
| Words | 385 | 354 | -31 (-8%) |

## ✅ 완료 항목

- [x] P1: 분석 완료 (문제점 7개 식별)
- [x] P2: 설계 완료 (솔루션 정의)
- [x] P3: 구현 완료 (코드 작성)
- [x] P4: 테스트 완료 (검증 통과)
- [x] P5: 문서화 완료 (보고서 작성)

## 📋 산출물

- ✅ logs/task-N.log (실행 로그)
- ✅ metrics/task-N-metrics.json (메트릭)
- ✅ reports/task-N-report.md (보고서)
- ✅ variant-N-claude.md (결과물)
- ✅ variant-N-notes.md (상세 설명)

## 🔍 주요 발견사항

[Task 특화 발견사항]

## 💡 다음 단계

- Task N+1 입력으로 이 산출물 사용
- Git I/O 대시보드 자동 업데이트
```

---

## 📊 Task별 차별화 요구사항

### Task 1 (기준점)
```yaml
특화 요구사항:
  - 토큰 측정: 5개 명령어 × ±10% 정확도
  - 분석: CLAUDE.md의 7개 이상 문제 식별
  - 성능 프로파일: Hook 시간 측정
  
검증:
  - baseline-metrics.json 존재 및 유효
  - semantic-audit.md에서 3개 이상 겹침 발견
  - token_baseline = 3640 (±364)
```

### Task 2 (Variant A)
```yaml
특화 요구사항:
  - 문법 개선: 약화 표현 완전 제거
  - 줄 수: 26 → 24 (-8% 달성)
  - 가독성: Flesch-Kincaid < 7
  
검증:
  - variant-a-claude.md에서 겹친 규칙 3개 통합
  - 모든 의미 유지 (diff 검토)
  - 단어 수 감소: 385 → 354
```

### Task 3 (Variant B)
```yaml
특화 요구사항:
  - 12개 용어 정의 (각 < 50단어)
  - 예제/NOT-예제 완전성
  - glossary.json 머신 리더블
  
검증:
  - variant-b-glossary.json이 유효한 JSON
  - jq '.glossary | keys | length' = 12
  - CLAUDE.md에서 미정의 용어 = 0
```

### Task 4 (Variant C)
```yaml
특화 요구사항:
  - 토큰 감소: -1.5% 이상 달성
  - 플러그인: 5 → 3 (정당화됨)
  - Hook 설계: 배치 + 디바운싱
  
검증:
  - variant-c-settings.json이 유효한 JSON
  - Advisor: opus → sonnet
  - Hook 호환성: 기존 시그니처 유지
```

### Task 5 (통합)
```yaml
특화 요구사항:
  - 3개 Variant 충돌 없이 병합
  - 프로덕션 배포: /Users/kang/.claude/
  - Hook 실행 테스트
  
검증:
  - CONSOLIDATION_REPORT.md 모든 결정 설명
  - Master 파일: jq/Markdown 파싱 성공
  - Hook 실행: tab-rename.sh + collect-quality.sh OK
```

### Task 6 (Hook 최적화)
```yaml
특화 요구사항:
  - 배치 Hook: 450ms → 150ms (-67%)
  - 디바운싱 Hook: -80% 호출
  - 5회 벤치마크 (stddev < 10%)
  
검증:
  - Hook 파일: /Users/kang/.claude/hooks/에 배포
  - 실행 가능 (+x 권한)
  - 기존 작업 계속 수행 (backward compat)
```

---

## 🔄 Task 간 의존성 & 입출력

```
Task 1: Baseline Analysis
├─ 입력: CLAUDE.md, settings.json
├─ 산출물: baseline-metrics.json, semantic-audit.md
└─ 다음 Task 입력: baseline-metrics.json

Task 2: Variant A (문법)
├─ 입력: CLAUDE.md + baseline-metrics.json
├─ 산출물: variant-a-claude.md, variant-a-notes.md
└─ 다음 Task 입력: variant-a-claude.md

Task 3: Variant B (용어)
├─ 입력: CLAUDE.md + baseline-metrics.json
├─ 산출물: variant-b-claude.md, variant-b-glossary.json, variant-b-notes.md
└─ 다음 Task 입력: variant-b-glossary.json

Task 4: Variant C (효율)
├─ 입력: settings.json + baseline-metrics.json
├─ 산출물: variant-c-settings.json, variant-c-hooks/, variant-c-notes.md
└─ 다음 Task 입력: variant-c-settings.json

Task 5: 통합
├─ 입력: variant-a-*.md + variant-b-*.md + variant-c-*
├─ 산출물: /Users/kang/.claude/CLAUDE.md, /Users/kang/.claude/settings.json
└─ 다음 Task 입력: Master files

Task 6: Hook 최적화
├─ 입력: /Users/kang/.claude/hooks/ + variant-c-hooks/
├─ 산출물: Optimized hooks, hook-testing-results.md
└─ 다음 Task 입력: (없음 - 최종 Task)
```

---

## ✅ 전체 Task 체크리스트 (통일)

### 모든 Task가 완료되려면:

```
□ P1: 분석 단계 완료
  ├─ 문제/기회 식별
  ├─ 기준점 vs 목표 정의
  └─ 로그 기록: task-N.log에 기록

□ P2: 설계 단계 완료
  ├─ 솔루션 설계
  ├─ 검증 방법 정의
  └─ 로그 기록: task-N.log에 기록

□ P3: 구현 단계 완료
  ├─ 코드/설정 작성
  ├─ 테스트 작성
  └─ 로그 기록: task-N.log에 기록

□ P4: 테스트 단계 완료
  ├─ 모든 검증 통과
  ├─ 메트릭 측정 완료
  └─ 로그 기록: task-N.log에 기록

□ P5: 문서화 완료
  ├─ task-N-report.md 작성
  ├─ task-N-metrics.json 생성
  ├─ variant-N-notes.md 작성
  └─ Git I/O 대시보드 업데이트

□ 산출물 확인
  ├─ ✅ logs/task-N.log
  ├─ ✅ metrics/task-N-metrics.json (jq 파싱 OK)
  ├─ ✅ reports/task-N-report.md
  ├─ ✅ variant-N-*.md/json
  └─ ✅ Git 커밋 완료

□ 메트릭 기록
  ├─ token_cost
  ├─ clarity_score
  ├─ lines/words 변화
  ├─ duration_minutes
  └─ quality_scores

□ 다음 Task 준비
  ├─ 산출물이 다음 Task 입력으로 준비됨
  ├─ 의존성 체크 완료
  └─ Git I/O 대시보드 업데이트
```

---

## 📈 Git I/O 대시보드 자동 업데이트

```bash
#!/bin/bash
# 매 Task 완료 후 자동 실행

TASK_ID=$1

# 1. 메트릭 JSON → 대시보드 데이터 변환
python3 .claude-harness-analysis/extract-metrics.py \
  --task $TASK_ID \
  --metrics .claude-harness-analysis/metrics/task-${TASK_ID}-metrics.json \
  --output docs/harness-dashboard.json

# 2. HTML 업데이트
python3 docs/update-harness-dashboard.py \
  --dashboard docs/harness-dashboard.json \
  --output docs/index.html

# 3. Git 커밋
git add .claude-harness-analysis/ docs/
git commit -m "chore: update harness dashboard for task-${TASK_ID}"
git push
```

---

## 🎯 최종 정리

**모든 Task는 동일한 요구사항을 따릅니다:**

1. ✅ **입력 (Input)**: CLAUDE.md + settings.json + 이전 Task 산출물
2. ✅ **프로세스 (Process)**: 5단계 (분석 → 설계 → 구현 → 테스트 → 문서화)
3. ✅ **산출물 (Output)**: logs + metrics + reports + artifacts + notes
4. ✅ **검증 (Validation)**: 파일 존재, JSON 유효, 메트릭 측정
5. ✅ **메트릭 (Metrics)**: 토큰, 명확성, 줄 수, 단어 수, 용어 정의
6. ✅ **보고서 (Report)**: Task-N-report.md (메트릭 + 발견 + 다음 단계)

**이로써 6개 Task는 완벽히 동일한 프레임워크로 통일되었습니다!** 🎯
