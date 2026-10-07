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
