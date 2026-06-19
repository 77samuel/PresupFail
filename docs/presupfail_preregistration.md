# PresupFail — Pre-registered Success Criteria v1.1

*Registered before pilot execution. No criteria may be changed after data collection begins.*

*Date frozen: 2026-06-18*

---

## Gate 1 — Annotation Protocol Acceptance

**Criterion:** Cohen's κ ≥ 0.80 on the 20-item ambiguity stress test

- If met → annotation protocol accepted, proceed to main pilot
- If not met → revise boundary definitions only (not codes), re-test on a fresh 20-item set
- Maximum revision cycles: 2. If κ < 0.80 after two cycles, stop and reconsider the taxonomy

---

## Gate 2 — Item Quality Control (not a model performance threshold)

**Criterion:** Items for which ≥ 80% of models produce an Incorrect (I) or Fabricated (Fk) response on the knowledge probe are flagged for review and may be replaced before scaling.

- Rationale: this evaluates item quality, not model capability. An item that no model can answer correctly on direct probe is likely ambiguous, too obscure, or imprecisely formulated.
- Flagged items are reviewed and either revised or replaced with unambiguous alternatives before scaling to the full dataset.
- This gate does not set any threshold on overall KVR. KVR is reported as a descriptive finding, not a pass/fail criterion.

---

## Gate 3 — Primary Effect (Trigger × Behavior)

**Criterion:** Chi-square p < 0.05 AND Cramér's V ≥ 0.20 for trigger type × response behavior distribution

- V ≥ 0.20 = medium effect (minimum threshold for a meaningful empirical finding)
- If V < 0.20 but p < 0.05 → report as statistically significant but practically weak; revise contribution framing
- If p ≥ 0.05 → null result; report honestly and reframe paper as an exploratory benchmark contribution

---

## Gate 4 — Architecture Effect

**Criterion:** Kruskal-Wallis p < 0.05 for cross-architecture comparison of RR and AR

- If significant → architecture finding is a confirmed result
- If not significant → reported as a negative finding, not omitted. A negative finding is scientifically valid and will be reported as such.

---

## Gate 5 — Mechanism Claims

**Criterion:** To make pragmatic vs. epistemic failure claims, require minimum cell counts in the mechanism table:

| Pattern | Minimum count required |
|---|---|
| C + A/F (pragmatic failure) | ≥ 15 instances |
| I/Fk + A/F (epistemic failure) | ≥ 15 instances |

- If either cell count < 15 → mechanism analysis reported as exploratory only, not as a confirmed finding
- If both ≥ 15 → mechanism analysis reported as a primary result

---

## Gate 6 — Dataset Balance (before scaling)

**Criterion:** Before expanding from pilot to full dataset, verify:

1. Each trigger type contributes 15–20% of the final dataset
2. No single domain contributes > 30% of items
3. No single response behavior category exceeds 50% of pilot annotations

- If one response category exceeds 50% → rebalance item set to reduce that category's dominance before scaling
- Rebalancing means replacing items, not relabeling responses

---

## Sample Size Decision Rule

**Method:** Power analysis after pilot, not pre-commitment to a fixed N

- After pilot, compute observed effect size (Cramér's V)
- Run power analysis for chi-square test: α = 0.05, power = 0.80
- Required N = output of power analysis
- Cap: 480 items maximum (annotation cost constraint)
- Floor: 180 items minimum (benchmark credibility threshold)
- Final N decided by power analysis, bounded by floor and cap

---

## What Cannot Change After Pilot Begins

- Label definitions (R/P/F/A/U and C/I/Ab/Fk)
- Precedence order for R/P/F/A/U assignment
- Fabrication threshold definition
- Statistical tests and effect size measures
- Any of the six gates above

---

## Analysis Stages (locked)

**Stage 1 — Knowledge Recognition**
- KVR by model
- KVR by trigger type
- Flag items failing Gate 2

**Stage 2 — Presupposition Behavior**
- R/P/F/A/U distributions per trigger type and per model
- Chi-square + Cramér's V (Gate 3)
- Architecture × trigger interaction (Gate 4)

**Stage 3 — Mechanism Analysis**
- Cross-annotation table: knowledge probe label × presupposition probe label
- Four interpretation patterns:
  - C + R → Robust reasoning
  - C + A/F → Pragmatic failure
  - I/Fk + A/F → Epistemic failure
  - Ab + U → Conservative uncertainty
  - I + R → Conservative/lucky rejection
- Gate 5 determines whether mechanism claims are confirmatory or exploratory

---

## What Does Not Change From This Point

- No new hypotheses
- No new metrics
- No new taxonomies
- No new prompt designs
- No threshold adjustments after seeing pilot data

---

## Addendum — PVP Mitigation Experiment (Run 3)

*Added after main experiment results were known. This is a new, separate experiment, not a modification of the frozen main benchmark analysis above.*

**PVP (Presupposition Verification Protocol):** a lightweight inference-time protocol that instructs the model to verify presupposed information before answering, with no fine-tuning and no few-shot examples.

**H5 (pre-registered before running PVP):** PVP provides larger absolute improvements in rejection rate for linguistically difficult trigger types (Aspectual, Cleft) than for already-robust trigger types (Change-of-state, Existential).

**Analysis plan for Run 3:**
1. ORR before vs after, overall and per model
2. PVF before vs after, per trigger per model — primary comparison table/figure
3. McNemar's test (paired, since same items reused) — per trigger and overall
4. BCS before vs after
5. H5 test: rank trigger types by baseline rejection rate, compute PVP improvement (Δ) per trigger, test whether Δ correlates negatively with baseline rate (Spearman)

## Addendum 2 — Paper Positioning (Frozen)

*This positioning is locked before writing begins. It governs framing throughout the manuscript.*

**Do not position this as a benchmark paper. Position it as an evaluation framework.**

The contribution stack, in order of presentation:

1. **PresupFail-60** — the benchmark (dataset contribution)
2. **PVF (Presupposition Vulnerability Fingerprint)** — reusable characterization framework (methodology contribution)
3. **ORR + BCS** — transparent, unweighted robustness and consistency measures (methodology contribution)
4. **PVP (Presupposition Verification Protocol)** — lightweight inference-time intervention demonstrating practical utility (applied contribution)

Only item 1 is a dataset. Items 2–4 are methodology. The abstract and introduction must reflect this balance — lead with the framework, not the dataset.

**Frozen abstract-level framing (paraphrase, do not quote verbatim in final text):**
A linguistically grounded framework for evaluating presupposition-induced hallucinations in small language models, consisting of a benchmark, a vulnerability fingerprint, transparent robustness/consistency measures, and a lightweight verification protocol demonstrating the framework's practical utility.

**Named contributions — exactly five, no more:**
PresupFail-60, PVF, ORR, BCS, PVP. Do not introduce additional named terms or acronyms beyond these five anywhere in the manuscript.

**Required closing figure — "Framework Summary":**
A single diagram showing the pipeline: PresupFail-60 → (PVF, ORR/BCS) → vulnerability identification → PVP intervention. Placed near the end of the paper (Discussion or Conclusion). Purpose: let a reviewer grasp the full paper from one figure in under 10 seconds.

**Title — explicitly NOT frozen.** Decide after Run 3 results are known. The title should lead with the phenomenon (presupposition-induced hallucination / trigger-specific patterns), not the word "framework." Candidate pattern: "When Small Language Models Accept False Presuppositions: [strongest finding] and a Lightweight Verification Protocol." Final wording depends on which result (PVP effect size, PVF architecture-sensitivity finding, or trigger-type effect) turns out strongest after Run 3.

**Required Introduction sentence (locked content, not locked wording):** Must explicitly distinguish PresupFail from domain/task-organized hallucination benchmarks by stating that this benchmark organizes evaluation around linguistic trigger structure rather than factual domain — this is the one-sentence novelty anchor for reviewers.




*Pre-registration v1.1 — permanently frozen.*
