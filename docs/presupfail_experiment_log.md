# PresupFail — Experiment Log

*Immutable audit trail. Append only — never edit or delete past entries.*

| Date | Version | Action | Reason / Notes |
|---|---|---|---|
| 2026-06-18 | Concept | Frozen | PresupFail selected as next paper after literature search ruled out CorrectionDecay, Knowledge Boundary Awareness, Anchor Collapse, Hallucination Phase Transition |
| 2026-06-18 | Research questions + Hypotheses | Frozen | RQ1–RQ3 finalized; H1–H3 kept conservative (statistical, not trigger-specific predictions) |
| 2026-06-18 | Trigger taxonomy | Frozen | 6 types: Factive, Existential, Aspectual, Change-of-state, Definite description, Cleft |
| 2026-06-18 | Response behavior taxonomy | Frozen | R/P/F/A/U defined |
| 2026-06-18 | Annotation guidelines v2.1 | Frozen | First full version with annotation unit, evidence span, precedence order |
| 2026-06-18 | Pilot dataset v0.1 | Built | 24 items, later reduced to 22 (removed S02, S04 for ambiguity) |
| 2026-06-18 | Stress-test run | Completed | 22 items × 2 models × 3 gens, temp=0.7, 263/264 valid (1 safety exclusion) |
| 2026-06-18 | Calibration κ exercise | Completed | 20 boundary cases, single-rater self-calibration, κ=0.49 — used to refine guidelines, NOT reported in paper |
| 2026-06-18 | Annotation guidelines v2.2 | Frozen | Added 3 boundary fixes: P vs R (explicit vs implicit), U vs R (factual contradiction overrides), U vs F (fabrication overrides uncertainty) |
| 2026-06-18 | Pre-registration v1.0 | Frozen | 6 gates defined before any main-run data collected |
| 2026-06-18 | Pre-registration v1.1 | Frozen | Gate 2 redefined as item-quality check (removed arbitrary 0.60 KVR threshold); Gate 6 (dataset balance) added |
| 2026-06-18 | Benchmark v0.1 → v1.0 | Frozen | 60 items, 10 per trigger; 3 items replaced (F08, D08, C03) for being partially-true/ambiguous; domain rebalanced (Science reduced from 42% to 33%) |
| 2026-06-19 | Run 1 (Main benchmark) | Completed | 60 items × 2 probes × 2 models × 3 gens, temp=0.3, mode=main, 720/720 valid, 0 exclusions |
| 2026-06-19 | Knowledge probe scoring | Completed | Deterministic regex scoring (96.4% auto-scored) + 13 manually reviewed cases. KVR: Llama=0.939, Qwen=0.972 |
| 2026-06-19 | Presupposition probe annotation | Completed | All 360 responses manually annotated using guidelines v2.2 (single rater, full read of every response) |
| 2026-06-19 | Statistical analysis | Completed | Gate 3 PASS (χ²=151.4, p<0.0001, Cramér's V=0.324). Gate 4: aggregate chi-square significant (p=0.029) but Kruskal-Wallis on per-item rates not significant (p=0.143) — reported as mixed/honest finding |
| 2026-06-19 | Mechanism table | Completed | Gate 5: Pragmatic failure CONFIRMATORY (n=124), Epistemic failure EXPLORATORY (n=7) |
| 2026-06-19 | PVF / ORR / BCS | Computed | Added as free reanalysis of existing data — no new compute. Cleft flagged as most architecture-sensitive trigger (33-point gap) |
| 2026-06-19 | Run 2 (Scaling study) | **Skipped** | Decision: PVF/ORR/BCS packaging judged sufficient; compute budget redirected to PVP mitigation instead |
| 2026-06-19 | Paper positioning | Frozen | Addendum 2 — framework positioning, 5 named contributions (PresupFail-60, PVF, ORR, BCS, PVP), title left unfrozen |
| 2026-06-19 | H5 hypothesis | Pre-registered | PVP improves difficult triggers (Aspectual, Cleft) more than easy ones (Change-of-state, Existential) — committed before Run 3 |
| 2026-06-19 | Run 3 (PVP mitigation) notebook | Built | 60 items × 2 models × 3 gens, PVP-wrapped presupposition probes only, temp=0.3 matching Run 1, 360 expected responses |
| | | | |

---

## Pending entries (to be filled as work proceeds)

| Date | Version | Action | Reason / Notes |
|---|---|---|---|
| | Run 3 (PVP mitigation) | Run | |
| | PVP response annotation | Complete | |
| | Random-sample κ (reported) | Complete | 40–60 item dual-rater sample, this κ goes in the paper |
| | McNemar's test (H5) | Complete | |
| | Manuscript draft | Start | |
| | Final title | Decide | |
