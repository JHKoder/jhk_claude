# Task 7: 문서 및 사용 가이드

**Files:**
- Create: `.experiment/QUALITY_METRICS_GUIDE.md`
- Modify: `.experiment/README.md` - 품질 비교 섹션 추가

**Interfaces:**
- Consumes: 모든 기능 (완성된 시스템)
- Produces: 사용자 가이드, 설정 예시

## Step 1: 품질 메트릭 가이드 작성

`.experiment/QUALITY_METRICS_GUIDE.md` 파일 생성:

```markdown
# Quality Metrics Guide

## 개요
코드 품질을 토큰 효율과 함께 측정하는 시스템입니다.

## 주요 지표

### Accuracy (정확도)
- 통과한 테스트 / 전체 테스트 × 100
- 범위: 0-100%
- 의미: 코드가 요구사항을 얼마나 충족하는가

### First Pass (한 번에 완성)
- 1: 첫 응답에서 모든 테스트 통과
- 0: 수정이 필요했음
- 의미: 정확도와 효율성

### Revision Count (수정 횟수)
- 정확도 100%에 도달할 때까지 필요한 수정 수
- 의미: 반복 비용

### Complexity Score (복잡도)
- 1-10 범위 (작은 작업 → 큰 작업)
- Task A: 3, Task B: 6, Task C: 9
- 의미: 작업의 난이도

### Quality/Token Ratio
- Accuracy ÷ (Tokens / 1000)
- 의미: 토큰 대비 품질 효율성

## 사용 방법

### 1. 작업 실행
Claude Code에서 Task A/B/C 중 하나를 선택하여 실행:
```
"Task A를 구현해줘"
```

### 2. 메트릭 자동 수집
- Stop Hook에서 자동으로 `quality_metrics` 저장
- 토큰은 Claude API 로그에서, 품질은 테스트에서 추출

### 3. 대시보드 확인
```bash
exp serve
# http://localhost:7788 → Quality Comparison 탭
```

## 해석

**우수한 결과:**
- Accuracy: 100%
- First Pass: 1
- Tokens: 낮음
- Quality/Token Ratio: 높음 (5 이상)

**개선이 필요한 결과:**
- Accuracy < 80%: 요구사항 이해 부족
- First Pass: 0이 많음: 첫 응답의 정확도 향상 필요
- Tokens: 높음: 프롬프트 최적화 필요

## 모델 비교 (참조)
- Sonnet (기준): Quality/Token = X
- Opus: Quality/Token = ?
- Haiku: Quality/Token = ?
```

## Step 2: README.md에 품질 비교 섹션 추가

`.experiment/README.md`에서 기존 "명령어" 섹션 다음에 다음 내용 추가:

```markdown
---

## 품질 비교 (새로운 기능)

### 시작하기
```bash
# 1. 측정할 작업 선택 (Task A/B/C)
exp list  # 사용 가능한 작업 목록

# 2. Claude Code 세션에서 작업 실행
# "Task A를 구현해줘" 등

# 3. 대시보드에서 결과 확인
exp serve
# http://localhost:7788/quality-comparison
```

### 지표 설명
- **Accuracy**: 테스트 통과율 (%)
- **First Pass**: 첫 응답에서 완성 (1=yes, 0=no)
- **Complexity**: 작업 난이도 (1-10)
- **Quality/Token**: 토큰 대비 품질 효율

### 비교 전략
Task A (간단) → Task B (중간) → Task C (복잡) 순으로 실행하여 난이도별 효율 추적.
```

## Step 3: Commit

```bash
git add .experiment/QUALITY_METRICS_GUIDE.md .experiment/README.md
git commit -m "docs: add quality metrics guide and dashboard documentation"
```
