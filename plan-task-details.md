# Claude 하네스 엔지니어링 — Task별 주제 & 목표 설정

> 각 Task의 구체적 주제, 프로그램 목표, 성공 기준을 정의한 세부 문서

---

## Task 1: 기준점 분석 & 토큰 비용 측정

### 📌 주제
**"Claude Code 하네스의 현재 상태는 어떤가?"**
- 명령어당 토큰 실제 비용은?
- 현재 문서에서 모호한 부분은?
- 설정에서 낭비되는 부분은?

### 🎯 목표
1. **토큰 비용 기준선 수립**
   - 5개 대표 명령어별 토큰 오버헤드 측정
   - 세션 시작 비용 vs 명령어 비용 구분
   - 플러그인 로드 오버헤드 량화

2. **문서 명확성 감시**
   - 겹치는 지침 찾기 (예: "결론 우선" vs "결과 직접 명시")
   - 용어 불일치 찾기 (task/step 혼동)
   - 장황한 섹션 찾기 (축약 가능한 부분)

3. **설정 효율성 분석**
   - 실제 사용 중인 플러그인 vs 선언된 플러그인
   - Hook 실행 시간 측정
   - 모델 선택 적절성 검토 (haiku vs 필요한 것)

### 📊 산출물
- `baseline-metrics.json` (3640 토큰 기준점)
- `semantic-audit.md` (7개 문제점 식별)
- `hook-performance.json` (Stop hook 450ms, Submit hook 80ms)

### ✅ 성공 기준
```
□ 5개 명령어 모두 토큰 측정 완료
□ CLAUDE.md에서 3개 이상 겹침 찾기
□ 각 플러그인의 실제 사용 여부 확인
□ Hook 실행 시간 ±10% 정확도로 측정
□ JSON 산출물 검증 (jq 파싱 성공)
```

### 💡 프로그램 구조
```python
# task_1_baseline_analyzer.py
class BaselineAnalyzer:
    def measure_token_cost(self, command_list):
        """5개 명령어 토큰 측정"""
        # 1. claude code --read 토큰 측정
        # 2. claude code --bash 토큰 측정
        # 3. claude code --skill 토큰 측정
        # 4. claude code --agent 토큰 측정
        # 5. claude code (cold start) 토큰 측정
        return metrics
    
    def audit_semantic(self, claude_md_path):
        """문서 명확성 감시"""
        # 1. 겹치는 규칙 찾기
        # 2. 용어 불일치 찾기
        # 3. 장황한 부분 찾기
        return issues
    
    def analyze_settings(self, settings_json_path):
        """설정 효율성 분석"""
        # 1. 플러그인 로드 순서 검사
        # 2. Hook 실행 시간 측정
        # 3. 모델 선택 검토
        return analysis
```

---

## Task 2: Variant A — 문법 & 구조 개선

### 📌 주제
**"CLAUDE.md를 더 명확하고 간결하게 쓸 수 있을까?"**
- 문법 오류 수정
- 문장 구조 개선
- 겹치는 규칙 통합

### 🎯 목표
1. **문법 및 문장 구조 개선**
   - 약화 표현 제거 ("try to" → 명령조)
   - 일관된 시점 유지 (2인칭 "you")
   - 병렬 구조 일관성 (bullet point 스타일)

2. **겹치는 규칙 병합**
   - "Conclusion first" + "Prefer diff/code blocks" → 1개 규칙로
   - "Read file only once" + "Never re-read" → 1개로 통합
   - 중복 제거로 -6% 라인 수 달성

3. **가독성 지표 개선**
   - Flesch-Kincaid Grade 점수 계산
   - 평균 문장 길이 단축
   - 전문 용어 지수 낮추기

### 📊 산출물
- `variant-a-claude.md` (24줄, 354단어)
- `variant-a-notes.md` (변경 사항 상세 설명)
- `readability-metrics.json` (가독성 점수)

### ✅ 성공 기준
```
□ 줄 수: 26 → 24 (-8% 달성)
□ 단어 수: 385 → 354 (-8% 달성)
□ 겹친 규칙: 3개 모두 병합
□ 약화 표현: 완전히 제거
□ Flesch-Kincaid 점수: 7 이하 (고등학교 수준)
□ 모든 의미 손실 X (의미 = 기준점)
```

### 💡 프로그램 구조
```python
# task_2_syntax_polish.py
class SyntaxPolisher:
    def identify_overlaps(self, text):
        """겹치는 규칙 찾기"""
        # 1. 의미론적 유사성 측정 (cosine similarity)
        # 2. 규칙 A와 B의 중복도 계산
        # 3. 임계값 > 0.85 → 겹침으로 표시
        return overlaps
    
    def rewrite_for_clarity(self, text):
        """명확성을 위해 재작성"""
        # 1. 약화 표현 검출 및 제거
        # 2. 병렬 구조 확인
        # 3. 평균 문장 길이 계산
        return polished_text
    
    def calculate_readability(self, text):
        """가독성 지표 계산"""
        # Flesch-Kincaid Grade = 0.39*words/sents + 11.8*syls/words - 15.59
        return grade_level
```

---

## Task 3: Variant B — 용어 정밀성 & 어휘 정의

### 📌 주제
**"하네스에서 사용하는 모든 용어를 명확하게 정의할 수 있을까?"**
- 12개 핵심 용어 정의
- 각 용어의 예시 제공
- 혼동하기 쉬운 용어 구분

### 🎯 목표
1. **12개 핵심 용어 정밀 정의**
   - task: "테스트 사이클 포함, 독립적 평가 가능 단위"
   - step: "2-5분 작업, 가시적 입출력"
   - command: "결정론적 실행, 명령어"
   - directive: "의사결정 가이드"
   - hook: "이벤트 트리거 스크립트"
   - skill: "플러그인 내 호출 가능 기능"
   - agent: "신규 컨텍스트, 특화된 전문가"
   - plugin: "마켓플레이스 확장"
   - worktree: "격리된 git 작업 복사본"
   - session: "Claude Code 한 대화"
   - model: "Claude 변형 (haiku/sonnet/opus)"
   - token_cost: "명령어 추론 가격"

2. **용어집 머신 리더블 형식**
   - JSON 형식 (프로그래매틱 검증용)
   - 각 용어에 NOT-예제 (혼동 방지)
   - 예제 코드 포함

3. **용어 일관성 검증**
   - CLAUDE.md 내 용어 사용 일관성 확인
   - 정의되지 않은 용어 찾기
   - 용어 충돌 감지

### 📊 산출물
- `variant-b-claude.md` (용어집 포함 버전)
- `variant-b-glossary.json` (머신 리더블 12개 용어)
- `term-consistency-report.md` (일관성 검증)

### ✅ 성공 기준
```
□ 12개 용어 모두 정의 (정의 < 50단어)
□ 각 용어 예제 2개 이상
□ 각 용어 NOT-예제 1개 이상
□ glossary.json 유효 (jq 파싱 성공)
□ CLAUDE.md에서 미정의 용어 0개
□ 용어 충돌 0개
```

### 💡 프로그램 구조
```python
# task_3_vocabulary_precision.py
class VocabularyPrecision:
    def create_glossary(self):
        """12개 용어 용어집 생성"""
        glossary = {
            "task": {
                "definition": "...",
                "examples": [...],
                "not_examples": [...]
            },
            # 반복 11번
        }
        return glossary
    
    def validate_term_consistency(self, claude_md, glossary):
        """CLAUDE.md 내 용어 일관성 검증"""
        # 1. glossary의 모든 용어 검색
        # 2. 정의되지 않은 용어 찾기
        # 3. 용어 충돌 감지
        return inconsistencies
    
    def generate_glossary_json(self, glossary):
        """JSON 형식 생성"""
        # 1. 구조화된 JSON 생성
        # 2. 검증 (schema 체크)
        # 3. 미리보기
        return glossary_json
```

---

## Task 4: Variant C — 토큰 효율 & 명령어 최적화

### 📌 주제
**"하네스에서 불필요한 토큰 비용을 줄일 수 있을까?"**
- 사용하지 않는 플러그인 제거
- Advisor 모델 다운그레이드
- Hook 배치 처리 및 디바운싱

### 🎯 목표
1. **설정 최적화 (settings.json)**
   - 플러그인: 5개 → 3개 (-2개 미사용 플러그인)
   - Advisor 모델: opus → sonnet (37.5% 비용 절감)
   - 플러그인 로드 순서 최적화

2. **Hook 최적화 설계**
   - Stop Hook: 개별 DB 쿼리 → 배치 트랜잭션 (-300ms)
   - Submit Hook: 키마다 실행 → 5초 디바운싱 (-80% 호출)

3. **토큰 비용 감소 측정**
   - 기준점 3640 → 목표 3586 (-54 토큰, -1.5%)
   - 각 최적화 별 기여도 계산

### 📊 산출물
- `variant-c-settings.json` (최적화 설정)
- `variant-c-hooks/` (배치/디바운싱 Hook 설계)
- `token-cost-comparison.json` (변경 전/후)
- `variant-c-notes.md` (최적화 근거)

### ✅ 성공 기준
```
□ 플러그인: 5 → 3개로 감소
□ Advisor: opus → sonnet 변경
□ Token 감소: -1.5% 이상
□ Hook 설계: 배치 + 디바운싱 구현
□ JSON 유효성: jq 파싱 성공
□ Hook 호환성: 기존 함수 시그니처 유지
```

### 💡 프로그램 구조
```python
# task_4_token_efficiency.py
class TokenEfficiency:
    def optimize_plugins(self, settings_json):
        """플러그인 최적화"""
        # 1. 실제 사용 플러그인 식별
        # 2. 미사용 플러그인 목록화
        # 3. 제거 영향 평가
        return optimized_plugins
    
    def downgrade_advisor_model(self, settings_json):
        """Advisor 모델 다운그레이드"""
        # 1. opus vs sonnet 성능 비교
        # 2. 코드 리뷰 작업에 sonnet 충분성 확인
        # 3. 비용 절감 계산 (37.5%)
        return new_advisor_model
    
    def design_batched_hook(self):
        """배치 Hook 설계"""
        # 1. 개별 DB 쿼리 → 트랜잭션으로 변경
        # 2. 실행 시간 감소 추정 (-300ms)
        # 3. 동시성 이슈 검토
        return batched_hook_code
    
    def design_debounced_hook(self):
        """디바운싱 Hook 설계"""
        # 1. 이벤트 빈도 분석
        # 2. 5초 윈도우 설정
        # 3. 락 파일 기반 구현
        return debounced_hook_code
    
    def calculate_token_savings(self, baseline, optimized):
        """토큰 절감 계산"""
        # 1. 각 최적화의 기여도 계산
        # 2. 누적 절감액 계산
        # 3. 퍼센테이지 환산
        return savings_breakdown
```

---

## Task 5: 통합 & 마스터 하네스 병합

### 📌 주제
**"3개 Variant를 어떻게 합칠 것인가?"**
- 각 Variant의 강점 선택
- 충돌 해결 (있다면)
- 최종 마스터 하네스 결정

### 🎯 목표
1. **Variant 병합 전략**
   - Variant A (문법) + B (용어) → CLAUDE.md로 통합
   - Variant C (효율) → settings.json으로 통합
   - 충돌 해결 매트릭스 작성

2. **통합 보고서 작성**
   - 각 결정 근거 설명
   - 위험 평가 (없어야 함)
   - 테스트 체크리스트

3. **프로덕션 배포**
   - Master CLAUDE.md → `/Users/kang/.claude/CLAUDE.md` 업데이트
   - Master settings.json → `/Users/kang/.claude/settings.json` 업데이트
   - 검증: 파일 파싱 성공, Hook 동작

### 📊 산출물
- `/Users/kang/.claude/CLAUDE.md` (최종 프로덕션)
- `/Users/kang/.claude/settings.json` (최종 프로덕션)
- `CONSOLIDATION_REPORT.md` (병합 결정 문서)
- `harness-engineering-summary.md` (임원진 요약)

### ✅ 성공 기준
```
□ CLAUDE.md: 문법(A) + 용어(B) 모두 통합
□ settings.json: 효율(C) 최적화 적용
□ 지침 손실: 0개 (의미는 100% 유지)
□ 파일 검증: JSON/Markdown 파싱 성공
□ Hook 테스트: tab-rename.sh + collect-quality.sh 실행 성공
□ Git 커밋: 깨끗한 상태 (변경사항 없음)
```

### 💡 프로그램 구조
```python
# task_5_consolidation.py
class Consolidation:
    def merge_variants(self, variant_a_md, variant_b_md, variant_c_json):
        """Variant 병합"""
        # 1. Variant A + B 충돌 분석
        # 2. 병합 순서 결정 (문법 먼저, 용어 나중)
        # 3. 통합 CLAUDE.md 생성
        # 4. Variant C는 settings.json으로 직접 통합
        return master_files
    
    def validate_integration(self, master_files):
        """통합 검증"""
        # 1. JSON/Markdown 파싱 성공
        # 2. 모든 지침 존재 확인
        # 3. Hook 경로 유효성 확인
        return validation_results
    
    def deploy_to_production(self, master_files):
        """프로덕션 배포"""
        # 1. 백업 생성
        # 2. 파일 복사
        # 3. 검증
        # 4. Git 커밋
        return deployment_status
```

---

## Task 6: Hook 최적화 & 테스트 (Phase 2)

### 📌 주제
**"Hook을 더 빠르고 효율적으로 실행할 수 있을까?"** (선택사항)
- 배치 DB 트랜잭션
- 이벤트 디바운싱
- 성능 벤치마크

### 🎯 목표
1. **배치 Hook 구현**
   - Stop Hook: 7개 개별 sqlite3 호출 → 1개 트랜잭션
   - 실행 시간: 450ms → 150ms (-67%)
   - DB 잠금 경합 감소

2. **디바운싱 Hook 구현**
   - Submit Hook: 키마다 실행 → 5초마다 1회
   - 호출 빈도: 100% → 20% (-80%)
   - 서브프로세스 생성 대폭 감소

3. **성능 벤치마크**
   - 기준점 vs 최적화 비교
   - 5회 반복 측정 (일관성 확인)
   - 결과 문서화

### 📊 산출물
- `/Users/kang/.claude/hooks/collect-experiment-quality-batched.sh` (배치 구현)
- `/Users/kang/.claude/hooks/tab-rename-debounced.sh` (디바운싱 구현)
- `hook-testing-results.md` (성능 벤치마크)

### ✅ 성공 기준
```
□ 배치 Hook 구현 완료 (1개 트랜잭션)
□ 디바운싱 Hook 구현 완료 (락 파일 기반)
□ 기준점 vs 최적화: 실행 시간 50% 이상 단축
□ 5회 반복 측정 (표준편차 < 10%)
□ Hook 호환성: 기존 작업 계속 수행
□ 테스트: 정상 동작 확인
```

### 💡 프로그램 구조
```bash
#!/bin/bash
# task_6_hook_optimization.sh

# Benchmark 함수
benchmark_hook() {
    local hook=$1
    local iterations=5
    local times=()
    
    for i in $(seq 1 $iterations); do
        time_ms=$( { time $hook > /dev/null 2>&1; } 2>&1 | grep real | awk '{print $2}')
        times+=($time_ms)
    done
    
    # 평균, 최소, 최대 계산
    echo "Hook: $hook"
    echo "Times: ${times[@]}"
    echo "Average: $(calculate_average ${times[@]})"
    echo "Std Dev: $(calculate_stddev ${times[@]})"
}

# 비교: 기준점 vs 최적화
benchmark_hook "/Users/kang/.claude/hooks/collect-experiment-quality.sh"
benchmark_hook "/Users/kang/.claude/hooks/collect-experiment-quality-batched.sh"
```

---

## 📊 전체 Task 목표 맵

```
┌─────────────────────────────────────────────────────┐
│           Claude Harness Engineering               │
│              6 Task × 3 Metrics                     │
└─────────────────────────────────────────────────────┘

Task 1: 기준점 분석
├─ 토큰: 3640 (기준)
├─ 명확성: 72/100
└─ 용어 정의: 0개

Task 2: Variant A (문법)
├─ 토큰: 3635 (-5, -0.1%)
├─ 명확성: 78/100 (+6)
└─ 용어 정의: 0개

Task 3: Variant B (용어)
├─ 토큰: 3642 (+2, +0.1%)
├─ 명확성: 85/100 (+13)
└─ 용어 정의: 12개 ✓

Task 4: Variant C (효율)
├─ 토큰: 3586 (-54, -1.5%)
├─ 명확성: 77/100 (+5)
└─ 용어 정의: 0개

Task 5: 통합
├─ 토큰: 3586 (-54, -1.5%)
├─ 명확성: 86/100 (+14)
└─ 용어 정의: 12개 ✓

Task 6: Hook 최적화 (선택)
├─ 토큰: 3571 (-69, -1.9%)
├─ Hook 시간: -300ms (Stop), -80% (Submit)
└─ 성능: +67% 향상
```

---

## 🎯 최종 성공 조건

### Task 1: ✅ 기준점 수립
- [ ] 토큰 비용 정량화 (±10% 오차 범위)
- [ ] 문제점 7개 식별
- [ ] JSON 산출물 검증

### Task 2: ✅ 문법 개선
- [ ] 줄 수: 26 → 24
- [ ] 겹친 규칙: 3개 통합
- [ ] 가독성: Flesch-Kincaid < 7

### Task 3: ✅ 용어 정의
- [ ] 12개 용어 정의
- [ ] 예제/NOT-예제 완전
- [ ] 일관성 검증: 0개 충돌

### Task 4: ✅ 토큰 절감
- [ ] 토큰 감소: -1.5% 이상
- [ ] 플러그인: 5 → 3
- [ ] Hook 설계: 배치/디바운싱

### Task 5: ✅ 프로덕션 배포
- [ ] Master 파일 유효성 검증
- [ ] Hook 실행 테스트
- [ ] Git 커밋 완료

### Task 6: ✅ Hook 최적화 (선택)
- [ ] 배치: 450ms → 150ms
- [ ] 디바운싱: -80% 호출
- [ ] 5회 벤치마크 완료

---

## 📝 요약 테이블

| Task | 주제 | 목표 | 메트릭 | 위험도 |
|------|------|------|--------|--------|
| 1 | 기준점 | 측정/분석 | Token 3640 | Low |
| 2 | 문법 | 개선 | 줄 26→24 | Low |
| 3 | 용어 | 정의 | 12 terms | Low |
| 4 | 효율 | 절감 | Token -1.5% | Low |
| 5 | 통합 | 배포 | Deploy | Low |
| 6 | Hook | 최적화 | 시간 -67% | Medium |

---

**이제 각 Task가 구체적으로 무엇을 달성해야 하는지 명확합니다!** 🎯
