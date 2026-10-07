# Claude 하네스 엔지니어링 — 문법, 단어 선정 & 토큰 효율 최적화

> **상태**: 플랜 완성 | **실행**: Native (인라인) 또는 Subagent-driven 방식 선택 가능

**목표**: `.claude/CLAUDE.md`와 `.claude/settings.json` 하네스를 최적화하여 문법 명확성, 용어 정밀성, 모든 명령어 상호작용의 토큰 효율을 개선한다.

**아키텍처**: 3개의 독립적 개선 트랙(A: 문법 개선, B: 용어 정밀성, C: 토큰 효율)을 병렬로 평가한 후 마스터 하네스로 통합. 각 트랙은 명령어당 토큰 비용과 명확성 메트릭을 측정한다.

**기술 스택**: Bash (명령어 분석), jq (JSON 조작), 셸 스크립팅, git, Markdown (문서화)

---

## 글로벌 제약사항

- `.claude/CLAUDE.md`의 모든 변경사항은 하위 호환성을 유지해야 함 (제거 X, 향상만 가능)
- `.claude/settings.json`의 설정은 현재 모든 플러그인(superpowers, context7, understand-anything, karpathy-skills)과 호환 유지
- 품질 메트릭 수집용 Stop hook (`collect-experiment-quality.sh`)은 계속 동작해야 함
- 토큰 측정은 단일 명령어 실행 오버헤드에 집중 (세션 누적 비용 아님)
- 새로운 의존성 없음; 기존 bash/jq 도구 활용
- Claude Code CLI에서 파싱 가능한 하네스 설정 유지 (YAML/JSON 브레이킹 체인지 없음)

---

## 리뷰 포커스

1. **모호한 지시사항** — "결론 우선"과 "결과 직접 명시"가 겹치는 언어 사용; 의미 손실 없이 언어 변경이 모호함을 해결하는지 테스트.
2. **명령어당 토큰 오버헤드** — `claude code` 명령어 호출의 기준점을 측정한 후 각 변경 후 측정; 성능 저하 없음을 보장.
3. **용어 일관성** — "task", "step", "command", "directive", "hook" 등이 상호 호환적으로 사용됨; 재작성이 정밀성을 유지하는지 확인.
4. **Hook 통합 견고성** — settings.json 업데이트 후 Stop hook과 UserPromptSubmit hook이 올바르게 트리거되는지 테스트.
5. **교차 참조 정확성** — CLAUDE.md가 settings.json 동작을 참조함; 두 파일 업데이트가 동기화 상태 유지.

---

## Task 개요

| Task | 제목 | 파일 | 산출물 | 예상 시간 |
|------|------|------|--------|---------|
| 1 | 기준점 분석 | baseline-metrics.json, semantic-audit.md | 토큰 비용 기준점 + 명확성 감시 | 30분 |
| 2 | Variant A — 문법 개선 | variant-a-claude.md, variant-a-notes.md | 문법 개선된 하네스 | 45분 |
| 3 | Variant B — 용어 정밀성 | variant-b-claude.md, variant-b-glossary.json, variant-b-notes.md | 12개 용어 용어집 + 정확한 표현 | 60분 |
| 4 | Variant C — 토큰 효율 | variant-c-settings.json, variant-c-hooks/, variant-c-notes.md, token-cost-comparison.json | 최적화된 설정 + Hook 설계 | 60분 |
| 5 | 통합 & 병합 | CONSOLIDATION_REPORT.md, harness-engineering-summary.md, `/Users/kang/.claude/CLAUDE.md`, `/Users/kang/.claude/settings.json` | 마스터 하네스 (프로덕션) | 90분 |
| 6 (선택) | Hook 최적화 (Phase 2) | collect-experiment-quality-batched.sh, tab-rename-debounced.sh, hook-testing-results.md | 프로덕션 준비 완료된 최적화 Hook + 테스트 결과 | 60분 |

**전체**: Task 6 포함 시 ~285분 (~4.75시간), Task 6 제외 시 ~225분 (~3.75시간)

---

## 각 Task 요약

### Task 1: 기준점 하네스 분석 & 토큰 비용 측정
- 5개 샘플 Claude Code 명령어에 대한 토큰 오버헤드 측정
- CLAUDE.md 명확성 감시 (겹침, 불일치, 장황함)
- settings.json 토큰 오버헤드 분석 (플러그인 로드, Hook 명령어, 모델 선택)
- JSON + Markdown으로 결과 문서화

**산출물**: 기준점 메트릭, 감시 보고서, Variant 사양

---

### Task 2: Variant A — 문법 & 구조 개선
- 문법, 병렬 구조, 명령조 음성에 중점을 두고 CLAUDE.md 재작성
- 약화 표현 제거 ("try to", "should")
- 겹치는 규칙 병합 ("결론 우선" + "diff/코드 블록 선호" → 단일 명시)
- 문장 다듬기 (-6% 줄, 의미는 동일)

**산출물**: Variant A CLAUDE.md + 주석 문서

---

### Task 3: Variant B — 용어 정밀성 & 엄격한 용어 정의
- 12개 용어 용어집 생성 (task, step, command, directive, hook, skill, agent, plugin, worktree, session, model, token_cost)
- 각 용어: 정의, 예제, NOT-예제 (혼동 방지)
- 용어집 용어를 일관되게 사용하여 CLAUDE.md 재작성
- 미래 도구용 머신 리더블 glossary.json 생성

**산출물**: Variant B CLAUDE.md + 용어집 JSON + 주석 문서

---

### Task 4: Variant C — 토큰 효율 & 명령어 수준 최적화
- Hook 스크립트 오버헤드 분석 (Stop hook, UserPromptSubmit hook)
- 최적화된 settings.json 설계 (사용하지 않는 플러그인 제거, Advisor 모델 opus→sonnet 다운그레이드)
- 최적화된 Hook 스크립트 생성 (배치 DB 쓰기, 디바운싱 이벤트)
- 토큰 비용 감소 측정 (~명령어당 2.2%)

**산출물**: Variant C settings.json + 최적화된 Hook + 토큰 비용 비교

---

### Task 5: 통합 & 마스터 하네스 병합
- Variant A (문법) + B (용어) → 마스터 CLAUDE.md로 병합
- Variant C (토큰 효율) → 마스터 settings.json으로 통합
- 통합 보고서 작성 (결정 근거, 위험 평가)
- 임원진 요약 작성 (메트릭, 도입 경로, 다음 단계)
- 마스터 하네스 배포 (프로덕션 파일 업데이트)

**산출물**: 마스터 CLAUDE.md + settings.json (프로덕션), 통합 보고서, 요약

---

### Task 6 (선택): Hook 최적화 & 테스트 (Phase 2)
- 배치 품질 수집 Hook 구현 (`collect-experiment-quality-batched.sh`)
- 디바운싱 탭 이름 변경 Hook 구현 (`tab-rename-debounced.sh`)
- 기준점 vs 최적화 비교 (실행 시간, 서브프로세스 수)
- 성능 개선 문서화

**산출물**: 최적화된 Hook 스크립트 + 테스트 결과, 프로덕션 배포 준비 완료

---

## 실행 추천 방식

**추천: Native (인라인 실행)**

**이유:**
- Task 1-4는 분석 + Variant 생성 (독립적, Task당 리뷰 오버헤드 낮음)
- Task 5는 단순 통합 (결정 매트릭스를 사용한 Variant 병합)
- Task 6은 선택적 미래 단계 (Hook 최적화에 열정이 있지 않다면 연기 가능)
- 모든 Task는 구체적 산출물 생성 (JSON, Markdown, 설정 파일)
- 프로덕션 배포 전 통합 하네스에 대한 최종 리뷰 1회면 충분

**예상 비용:**
- Native (인라인): ~8-10k 토큰 + 최종 리뷰 (~5k) = ~13-15k 전체
- Subagent-driven: ~25-30k 토큰 (Task당 신규 컨텍스트 + Task당 리뷰)

**추천 유지: Native가 품질 손실 없이 더 빠르고 저렴.**

---

## 파일 구조

```
.claude-harness-analysis/
├── baseline-metrics.json              # Task 1: 토큰 기준점
├── semantic-audit.md                  # Task 1: 명확성 감시
├── variant-a-claude.md                # Task 2: 문법 개선 CLAUDE.md
├── variant-a-notes.md                 # Task 2: 변경 사항 + 근거
├── variant-b-claude.md                # Task 3: 용어 정밀 CLAUDE.md
├── variant-b-glossary.json            # Task 3: 12개 용어 머신 리더블 용어집
├── variant-b-notes.md                 # Task 3: 변경 사항 + 근거
├── variant-c-settings.json            # Task 4: 최적화된 settings.json
├── variant-c-hooks/                   # Task 4: 최적화된 Hook 설계
│   ├── collect-experiment-quality-batched.sh
│   └── tab-rename-debounced.sh
├── variant-c-notes.md                 # Task 4: 최적화 상세 내용
├── token-cost-comparison.json         # Task 4: 변경 전/후 메트릭
├── CONSOLIDATION_REPORT.md            # Task 5: 병합 결정 + 위험 평가
├── harness-engineering-summary.md     # Task 5: 임원진 요약
├── hook-testing-results.md            # Task 6 (Phase 2): 성능 벤치마크
└── README.md                          # 모든 분석 파일 색인

프로덕션 파일 (Task 5에서 업데이트):
/Users/kang/.claude/
├── CLAUDE.md                          # 마스터 하네스 (업데이트됨)
└── settings.json                      # 마스터 하네스 (업데이트됨)

프로덕션 Hook (Phase 2 배포):
/Users/kang/.claude/hooks/
├── collect-experiment-quality-batched.sh      # Task 6
└── tab-rename-debounced.sh                    # Task 6
```

---

## 주요 메트릭

### 기준점 (Task 1)
- 현재 명령어당 토큰 비용: ~3640 토큰 (평균)
- CLAUDE.md 크기: 26줄, 385단어
- 활성화된 플러그인: 5개
- Hook: 2개 (Stop, UserPromptSubmit)
- Advisor 모델: opus (높은 비용)

### 마스터 하네스 (Task 5 목표)
- 명령어당 토큰 비용: ~3586 토큰 (-54 토큰, -1.5%)
- CLAUDE.md 크기: 24줄, 354단어 (-8%)
- 활성화된 플러그인: 3개 (-2 미사용)
- Hook: 2개 (동일, 최적화 경로 문서화)
- Advisor 모델: sonnet (37.5% 더 저렴)
- 용어 정밀성: 0 → 12개 정의된 용어
- 명확성 개선: +8% (문법 + 용어집)

### Phase 2 Hook (Task 6 목표)
- Stop hook 시간: -300ms (배치 트랜잭션)
- UserPromptSubmit hook 빈도: -80% (디바운싱)
- Hook에서의 토큰 절감: 세션당 -15 토큰

---

## 성공 기준

✅ 6개 Task 모두 완료 (Task 6 선택)
✅ 마스터 CLAUDE.md 배포 (지침 손실 없음)
✅ 마스터 settings.json 배포 (모든 플러그인 기능)
✅ 토큰 비용 감소 ≥1.5% 측정됨
✅ 용어 정밀성 개선 (0→12개 용어)
✅ Hook 최적화 Phase 2를 위해 문서화됨
✅ 통합 보고서가 모든 결정 설명
✅ 하네스에 대한 하위 호환성 유지 (브레이킹 체인지 없음)

---

## 플랜 승인 후 다음 단계

1. 실행 방식 선택: **Native (추천)** 또는 Subagent-driven
2. Task 1 시작 (기준점 분석)
3. Task 1-5 순차 실행 (Task 6 선택)
4. 통합 하네스 + 통합 보고서 리뷰
5. 마스터 CLAUDE.md + settings.json을 프로덕션에 배포
6. 향후 스프린트를 위해 Phase 2 (Hook 최적화) 스케줄 예약

---

**플랜 저장 위치**: `/Users/kang/gitdir/jhk_claude/plan.md` (영문)
**번역본 저장 위치**: `/Users/kang/gitdir/jhk_claude/plan-kr.md` (한글)
**상세 플랜**: `/Users/kang/gitdir/jhk_claude/docs/superpowers/plans/2026-10-07-claude-harness-engineering.md` (영문 상세)

---

## 추가 참고사항

이 한글 번역본은 **실행 목적이 아닌 문서 참고용**입니다.
- 실제 플랜 실행은 영문 상세 문서 (`2026-10-07-claude-harness-engineering.md`)를 기준으로 진행합니다.
- 한글 번역은 이해 및 팀 협업을 위한 참조 문서 역할을 합니다.
- 코드, JSON, 명령어는 영문 원본과 동일합니다.
