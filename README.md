# Claude Code Quality Metrics & Experiment Analysis System

**자동화된 코드 품질 측정 + 실험 분석 리포팅 시스템**

토큰 효율 vs 코드 품질을 정량화하고, 자동으로 분석 리포트를 생성하는 완전 자동화 시스템입니다.

---

## 🎯 기능 개요

### Part 1: Code Quality Metrics System
Claude Code 세션에서 **정확도(Accuracy)**, **한 번 완성도(First Pass)**, **복잡도(Complexity)** 를 자동으로 측정하고 대시보드에 시각화합니다.

- **Accuracy**: 테스트 통과율 (%)
- **First Pass**: 첫 응답에서 완성했는지 여부 (1/0)
- **Complexity Score**: 작업 난이도 (1-10)
- **Quality/Token Ratio**: 토큰 대비 품질 효율성

### Part 2: Automated Experiment Analysis
매일 자동으로 실험 데이터를 수집하고 분석하여 Markdown 리포트를 생성합니다.

- 일일 토큰 소모 추적
- 모델별 성능 비교 (Sonnet vs Opus vs Haiku)
- 품질 트렌드 분석
- GitHub Actions 자동 리포팅

---

## 📊 시스템 구조

```
┌─────────────────────────────────────────┐
│    Claude Code 세션                     │
│    (Task A/B/C 실행)                    │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ Stop Hook 자동 수집  │
        │ (quality_metrics)   │
        └──────────┬──────────┘
                   │
        ┌──────────▼─────────────────┐
        │ SQLite DB                  │
        │ (quality_metrics table)    │
        └──────────┬─────────────────┘
                   │
        ┌──────────┴───────┬──────────────┐
        │                  │              │
    ┌───▼───┐     ┌───────▼──────┐  ┌───▼────┐
    │Dashboard    │ GitHub Actions│  │CLI     │
    │(Web UI)     │(Daily Report) │  │compare │
    └───────┘     └───────────────┘  └────────┘
```

---

## 🚀 빠른 시작

### 1. 품질 메트릭 수집 설정

```bash
# ~/.claude/hooks/collect-experiment-quality.sh 생성 (이미 있음)
# ~/.claude/settings.json에 Stop hook 등록 (참고: .experiment/STOP_HOOK_SETUP.md)
```

### 2. Task 실행

Claude Code에서 Task A/B/C 중 하나를 선택하여 실행:

```bash
# Claude Code에서
Task A를 구현해줘
```

### 3. 대시보드 확인

```bash
cd .experiment
exp serve
# 브라우저: http://localhost:7788 → Quality Comparison 탭
```

### 4. 일일 리포트 확인

```bash
cat docs/experiments/2026-10-07-full-report.md
```

---

## 📁 프로젝트 구조

```
.experiment/
├── quality_metrics.py              # 품질 평가 핵심 로직
├── test_quality_metrics.py         # 정확도 계산 테스트
├── test_e2e_quality.py            # E2E 파이프라인 검증
├── QUALITY_METRICS_GUIDE.md        # 사용자 가이드
├── STOP_HOOK_SETUP.md              # 자동 수집 설정
├── templates/
│   └── quality_comparison.html     # 대시보드 UI (Chart.js)
├── test_cases/
│   ├── task_a_simple_refactor.md   # 간단한 리팩토링 (복잡도 3)
│   ├── task_b_feature_implementation.md  # 기능 구현 (복잡도 6)
│   └── task_c_architecture_refactor.md   # 아키텍처 변경 (복잡도 9)
├── export/
│   ├── analyzer.py                 # 실험 데이터 분석
│   └── reports.py                  # Markdown 리포트 생성
└── config/tasks.json               # 테스트 작업 정의

docs/experiments/
├── README.md                        # 실험 시스템 개요
├── 2026-10-07-full-report.md       # 전체 분석 리포트
├── 2026-10-07-quality.md           # 품질 지표
├── 2026-10-07-models.md            # 모델 비교
└── 2026-10-07-trends.md            # 트렌드 분석

.github/workflows/
└── experiment-report.yml            # 일일 자동 리포팅
```

---

## 📈 주요 지표

### Task A (간단한 리팩토링)
- **복잡도**: 3 (간단)
- **예상 시간**: 25분
- **테스트**: 4개
- **목표**: 중복 함수 통합

### Task B (기능 구현)
- **복잡도**: 6 (중간)
- **예상 시간**: 50분
- **테스트**: 4개
- **목표**: 캐싱 레이어 추가

### Task C (아키텍처 변경)
- **복잡도**: 9 (복잡)
- **예상 시간**: 90분
- **테스트**: 8개
- **목표**: 서비스 계층 분리

---

## 🔍 사용 예시

### 1. 정확도 확인

```bash
# 데이터베이스에서 조회
sqlite3 ~/Library/Application\ Support/experiment/jhk_claude-*/experiment.db \
  "SELECT task_id, accuracy, first_pass FROM quality_metrics ORDER BY created_at DESC LIMIT 5;"
```

### 2. 모델 비교

```bash
# 리포트에서 모델 성능 비교 보기
grep -A 20 "## Model Comparison" docs/experiments/2026-10-07-models.md
```

### 3. 트렌드 분석

```bash
# 일주일 데이터 집계
cat docs/experiments/2026-10-07-trends.md
```

---

## 🛠️ 기술 스택

| 컴포넌트 | 기술 |
|---------|------|
| DB | SQLite (experiment.db) |
| Quality Evaluator | Python (QualityEvaluator class) |
| Dashboard | HTML + Chart.js (scatter plot) |
| Analysis | Python (pandas-like) |
| Reporting | Markdown + GitHub Actions |
| Automation | Stop Hook (session end trigger) |

---

## 📊 현재 상태

### Commits
```
6fd5e98 feat: add code quality metrics measurement and experiment analysis system
        (squash: 10개 커밋 통합)
        - 24개 파일 생성/수정
        - 2287 insertions, 15 deletions
```

### Test Results
- ✅ Quality Metrics: DB schema + CRUD (PASS)
- ✅ E2E Pipeline: 3/3 tests passing
- ✅ Dashboard: Chart.js rendering verified
- ✅ Auto-collection: Stop hook setup documented

### Test Coverage
| 영역 | 테스트 | 상태 |
|------|--------|------|
| 정확도 계산 | test_accuracy_calculation_perfect | ✅ |
| 부분 통과 | test_accuracy_calculation_partial | ✅ |
| 복잡도 점수 | test_complexity_score_task_a/c | ✅ |
| E2E 파이프라인 | test_full_pipeline | ✅ |
| DB 통합 | test_quality_evaluation_integration | ✅ |

---

## 🔧 Configuration

### runner_config.json
```json
{
  "compile": null,
  "test": "python -m pytest tests/ -v",
  "test_parser": "pytest",
  "min_turns": 5,
  "min_output_tokens": 500
}
```

### tasks.json
```json
{
  "tasks": [
    {
      "id": "task_a",
      "complexity": 3,
      "expected_duration_minutes": 25,
      "test_count": 4
    },
    {
      "id": "task_b",
      "complexity": 6,
      "expected_duration_minutes": 50,
      "test_count": 4
    },
    {
      "id": "task_c",
      "complexity": 9,
      "expected_duration_minutes": 90,
      "test_count": 8
    }
  ]
}
```

---

## 📚 문서

- [Quality Metrics Guide](.experiment/QUALITY_METRICS_GUIDE.md) — 지표 설명 & 해석
- [Stop Hook Setup](.experiment/STOP_HOOK_SETUP.md) — 자동 수집 설정
- [Experiment Setup](EXPERIMENT_SETUP.md) — 전체 시스템 구조
- [Daily Report](docs/experiments/2026-10-07-full-report.md) — 실험 분석 리포트

---

## 🎓 학습 흐름

1. **Task A (간단)** 실행 → 기본 품질 지표 학습
2. **Task B (중간)** 실행 → 한 번 완성도 개선
3. **Task C (복잡)** 실행 → 복잡한 작업에서 효율성 최적화

---

## 🚨 알려진 제한사항

| 항목 | 상태 | 개선 계획 |
|------|------|---------|
| `revision_count` | Stub (항상 1) | 추후 git log 분석으로 구현 |
| Chart.js 차트 | scatter 타입 | bubble 타입으로 변경 예정 |
| pytest | 환경에서 선택사항 | 기본 제공 예정 |

---

## 🤖 생성 정보

- **Framework**: Subagent-driven Development → Inline Execution
- **Execution**: superpowers:executing-plans (native mode)
- **Review**: code-reviewer agent (self-review)
- **Merge**: Squash merge (1 commit)
- **Total Commits**: 10개 (1개로 통합)
- **Generation Date**: 2026-10-07

---

## 📞 Support

### 데이터 조회
```bash
# 모든 품질 메트릭 보기
cd .experiment
python3 -c "from collectors.store import all_runs; import json; [print(json.dumps(r)) for r in all_runs()]"
```

### 대시보드 시작
```bash
cd .experiment
exp serve 7788
# http://localhost:7788 접속
```

### 리포트 재생성
```bash
cd .experiment/export
python3 analyzer.py
```

---

**지속적 개선을 위한 자동화 시스템 — 코드 품질 측정과 분석을 한 곳에서!** 🚀
