# Claude Harness Engineering — Syntax, Word Choice & Token Optimization

> **Status**: Plan Complete | **Execution**: Ready for native (inline) or subagent-driven approach

**Goal:** Engineer the `.claude/CLAUDE.md` and `.claude/settings.json` harness for optimal syntax clarity, vocabulary precision, and token efficiency across all command interactions.

**Architecture:** Three independent improvement tracks (A: Syntax Polish, B: Vocabulary Precision, C: Token Efficiency) evaluated in parallel, then consolidated into master harness. Each track produces a variant config, measuring token cost per command execution and clarity metrics.

**Tech Stack:** Bash (command analysis), jq (JSON manipulation), shell scripting, git, Markdown (documentation)

---

## Global Constraints

- All changes to `.claude/CLAUDE.md` must be backward compatible (no removed guidance, only enhancement)
- Settings in `.claude/settings.json` remain functional with all current plugins (superpowers, context7, understand-anything, karpathy-skills)
- Stop hook for quality metrics collection (`collect-experiment-quality.sh`) must continue functioning
- Token measurement focuses on single command execution overhead, not session cost
- No new dependencies; leverage existing bash/jq tooling
- Keep harness configuration parseable by Claude Code CLI (no breaking YAML/JSON changes)

---

## Review Focus

1. **Ambiguous directives** — "Conclusion first" vs "State results directly" use overlapping language; test that rewording resolves the ambiguity without changing intent.
2. **Token overhead per command** — Measure baseline for `claude code` command invocation before/after each change; ensure no regression.
3. **Vocabulary consistency** — Terms like "task," "step," "command," "directive," "hook" used interchangeably; verify rewrite maintains precision.
4. **Hook integration robustness** — Stop hook and UserPromptSubmit hook must trigger correctly after settings.json updates; test both.
5. **Cross-reference correctness** — CLAUDE.md references settings.json behavior; ensure updates in both files remain synchronized.

---

## Tasks Overview

| Task | Title | Files | Deliverable | Est. Time |
|------|-------|-------|-------------|-----------|
| 1 | Baseline Analysis | baseline-metrics.json, semantic-audit.md | Token cost baseline + clarity audit | 30 min |
| 2 | Variant A — Syntax Polish | variant-a-claude.md, variant-a-notes.md | Grammar-tightened harness | 45 min |
| 3 | Variant B — Vocabulary Precision | variant-b-claude.md, variant-b-glossary.json, variant-b-notes.md | 12-term glossary + precise wording | 60 min |
| 4 | Variant C — Token Efficiency | variant-c-settings.json, variant-c-hooks/, variant-c-notes.md, token-cost-comparison.json | Optimized config + hook designs | 60 min |
| 5 | Consolidation & Merge | CONSOLIDATION_REPORT.md, harness-engineering-summary.md, `/Users/kang/.claude/CLAUDE.md`, `/Users/kang/.claude/settings.json` | Master harness (production) | 90 min |
| 6 (Optional) | Hook Optimization (Phase 2) | collect-experiment-quality-batched.sh, tab-rename-debounced.sh, hook-testing-results.md | Production-ready optimized hooks + test results | 60 min |

**Total**: ~285 min (~4.75 hours), or ~225 min (~3.75 hours) without Task 6

---

## Quick Task Summaries

### Task 1: Analyze Baseline Harness & Measure Token Cost
- Measure token overhead for 5 sample Claude Code commands
- Audit CLAUDE.md for clarity issues (overlaps, inconsistencies, verbosity)
- Analyze settings.json for token overhead (plugin load, hook commands, model selection)
- Document findings in JSON + Markdown

**Output**: Baseline metrics, audit report, variant specs

---

### Task 2: Variant A — Syntax Polish & Grammar Tightening
- Rewrite CLAUDE.md focusing on grammar, parallel structure, imperative voice
- Remove hedging ("try to", "should")
- Merge overlapping rules ("Conclusion first" + "Prefer diff/code blocks" → single statement)
- Tighten prose (-6% lines, same meaning)

**Output**: Variant A CLAUDE.md + notes doc

---

### Task 3: Variant B — Vocabulary Precision & Rigorous Terms
- Create 12-term glossary (task, step, command, directive, hook, skill, agent, plugin, worktree, session, model, token_cost)
- Each term: definition, examples, NOT-examples (to prevent confusion)
- Rewrite CLAUDE.md using glossary terminology consistently
- Produce machine-readable glossary.json for future tooling

**Output**: Variant B CLAUDE.md + glossary JSON + notes doc

---

### Task 4: Variant C — Token Efficiency & Command-Level Optimization
- Analyze hook script overhead (Stop hook, UserPromptSubmit hook)
- Design optimized settings.json (remove unused plugins, downgrade advisor model opus→sonnet)
- Create optimized hook scripts (batched DB writes, debounced events)
- Measure token cost reduction (~2.2% per command)

**Output**: Variant C settings.json + optimized hooks + token cost comparison

---

### Task 5: Consolidation & Master Harness Merge
- Merge Variant A (syntax) + B (vocabulary) into master CLAUDE.md
- Integrate Variant C (token efficiency) into master settings.json
- Write consolidation report (decision rationale, risk assessment)
- Write executive summary (metrics, adoption path, next steps)
- Deploy master harness (update production files)

**Output**: Master CLAUDE.md + settings.json (production), consolidation report, summary

---

### Task 6 (Optional): Hook Optimization & Testing (Phase 2)
- Implement batched quality collection hook (`collect-experiment-quality-batched.sh`)
- Implement debounced tab-rename hook (`tab-rename-debounced.sh`)
- Benchmark baseline vs. optimized (execution time, subprocess count)
- Document performance improvements

**Output**: Optimized hook scripts + test results, ready for production deployment

---

## Execution Recommendation

**Recommended approach: Native (Inline Execution)**

**Why:**
- Tasks 1-4 are analysis + variant creation (independent, low review overhead per task)
- Task 5 is straightforward consolidation (merge variants using decision matrix)
- Task 6 is optional future phase (defer unless eager to optimize hooks)
- All tasks produce concrete output (JSON, Markdown, config files)
- One final review of consolidated harness is sufficient before production deploy

**Estimated costs:**
- Native (inline): ~8-10k tokens + one final review (~5k) = ~13-15k total
- Subagent-driven: ~25-30k tokens (fresh context per task + per-task review)

**Recommendation stands: Native is faster and cheaper without sacrificing quality.**

---

## File Structure

```
.claude-harness-analysis/
├── baseline-metrics.json              # Task 1: Token baseline
├── semantic-audit.md                  # Task 1: Clarity audit
├── variant-a-claude.md                # Task 2: Syntax-polished CLAUDE.md
├── variant-a-notes.md                 # Task 2: Changes + rationale
├── variant-b-claude.md                # Task 3: Vocabulary-precise CLAUDE.md
├── variant-b-glossary.json            # Task 3: 12-term machine-readable glossary
├── variant-b-notes.md                 # Task 3: Changes + rationale
├── variant-c-settings.json            # Task 4: Optimized settings.json
├── variant-c-hooks/                   # Task 4: Optimized hook designs
│   ├── collect-experiment-quality-batched.sh
│   └── tab-rename-debounced.sh
├── variant-c-notes.md                 # Task 4: Optimization details
├── token-cost-comparison.json         # Task 4: Before/after metrics
├── CONSOLIDATION_REPORT.md            # Task 5: Merge decisions + risk assessment
├── harness-engineering-summary.md     # Task 5: Executive summary
├── hook-testing-results.md            # Task 6 (Phase 2): Performance benchmarks
└── README.md                          # Index of all analysis files

Production Files (Updated by Task 5):
/Users/kang/.claude/
├── CLAUDE.md                          # Master harness (updated)
└── settings.json                      # Master harness (updated)

Production Hooks (Deployed Phase 2):
/Users/kang/.claude/hooks/
├── collect-experiment-quality-batched.sh      # Task 6
└── tab-rename-debounced.sh                    # Task 6
```

---

## Key Metrics

### Baseline (Task 1)
- Current token cost per command: ~3640 tokens (avg)
- CLAUDE.md size: 26 lines, 385 words
- Plugins enabled: 5
- Hooks: 2 (Stop, UserPromptSubmit)
- Advisor model: opus (high cost)

### Master Harness (Task 5 target)
- Token cost per command: ~3586 tokens (-54 tokens, -1.5%)
- CLAUDE.md size: 24 lines, 354 words (-8%)
- Plugins enabled: 3 (-2 unused)
- Hooks: 2 (same, documented optimization path)
- Advisor model: sonnet (37.5% cheaper)
- Vocabulary precision: 0 → 12 defined terms
- Clarity gain: +8% (syntax + glossary)

### Phase 2 Hooks (Task 6 target)
- Stop hook time: -300ms (batched transactions)
- UserPromptSubmit hook frequency: -80% (debouncing)
- Token savings from hooks: -15 tokens per session

---

## Success Criteria

✅ All six tasks completed (Task 6 optional)
✅ Master CLAUDE.md deployed with no guidance loss
✅ Master settings.json deployed, all plugins functional
✅ Token cost reduction ≥1.5% measured
✅ Vocabulary precision improved (0→12 terms)
✅ Hook optimization documented for Phase 2
✅ Consolidation report explains all decisions
✅ No breaking changes to harness (backward compatible)

---

## Next Steps After Plan Approval

1. Choose execution method: **Native (recommended)** or Subagent-driven
2. Begin Task 1 (baseline analysis)
3. Execute Tasks 1-5 sequentially (Task 6 optional)
4. Review consolidated harness + consolidation report
5. Deploy master CLAUDE.md + settings.json to production
6. Schedule Phase 2 (hook optimization) for future sprint

---

**Plan saved to**: `/Users/kang/gitdir/jhk_claude/plan.md`
**Detailed plan**: `/Users/kang/gitdir/jhk_claude/docs/superpowers/plans/2026-10-07-claude-harness-engineering.md`
