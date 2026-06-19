# PresupFail — Reproducibility Manifest

*One-page frozen reference. Update only by appending a new dated section for new runs — never edit past entries.*

---

## Run 1 — Main Benchmark Experiment

| Item | Value |
|---|---|
| Benchmark version | v1.0 (`presupfail_items_benchmark_v10.json`) |
| Annotation guidelines | v2.2 (`presupfail_annotation_guidelines_v2.2.md`) |
| Pre-registration | v1.1 (`presupfail_preregistration.md`) |
| Mode | `main` |
| Temperature | 0.3 |
| Generations per item | 3 |
| Seeds | 42, 49, 56 (seed = 42 + gen_idx × 7) |
| Max new tokens | 300 |
| Models | meta-llama/Llama-3.2-3B-Instruct, Qwen/Qwen2.5-3B-Instruct |
| Items | 60 (10 per trigger type × 6 types) |
| Probe types | knowledge, presupposition (paired) |
| Expected records | 720 |
| Valid records | 720 |
| Excluded records | 0 |
| Run timestamp | 2026-06-18T19:06:08.627232 UTC |
| Python version | 3.12.13 |
| Transformers version | 5.0.0 |
| Torch version | 2.10.0+cu128 |
| CUDA version | 12.8 |
| Compute | Kaggle T4 GPU |
| Inference script | `presupfail_inference.py` v1.2 / `presupfail_benchmark_v10.ipynb` |

---

## Stress-Test Run (Calibration Only — Not Reported in Paper)

| Item | Value |
|---|---|
| Benchmark version | Pilot v0.1 (22 items) |
| Mode | `stress_test` |
| Temperature | 0.7 |
| Generations | 3 |
| Models | Same as Run 1 |
| Valid records | 263 / 264 (1 safety_filter_refusal exclusion) |
| Purpose | Annotation guideline calibration (κ=0.49 single-rater self-test, not reported) |

---

## Run 3 — PVP Mitigation Experiment

| Item | Value |
|---|---|
| Benchmark version | v1.0 (same items as Run 1) |
| Prompt version | PVP v1 — *"Before answering, check whether this question assumes something that may not be true. If it does, identify and correct the false assumption first, then answer."* |
| Mode | PVP-wrapped presupposition probes only (no knowledge probes — baseline established in Run 1) |
| Temperature | 0.3 (matches Run 1 for direct comparability) |
| Generations | 3 |
| Seeds | 42, 49, 56 (identical to Run 1) |
| Models | Same as Run 1 |
| Items | 60 |
| Expected records | 360 |
| Inference script | `presupfail_run3_pvp_mitigation.ipynb` |
| Status | *[fill in after run: timestamp, valid/excluded counts, environment versions]* |

---

## Annotation

| Item | Value |
|---|---|
| Knowledge probe scoring | Deterministic regex (96.4% auto) + 13 manually verified cases |
| Presupposition probe scoring | Single-rater manual annotation, full read, guidelines v2.2 |
| Reported κ sample | *[fill in: N items, rater identity/method, κ value]* |
| Reported κ method | *[fill in: e.g. 48-hour-gap self-annotation / second human rater / disclosed limitation]* |

---

## File Manifest

| File | Purpose |
|---|---|
| `presupfail_items_benchmark_v10.json` | Frozen 60-item benchmark |
| `presupfail_annotation_guidelines_v2.2.md` | Frozen annotation protocol |
| `presupfail_preregistration.md` | Frozen gates, hypotheses, positioning |
| `presupfail_experiment_log.md` | Full audit trail |
| `presupfail_inference.py` | Core inference pipeline (v1.2) |
| `presupfail_benchmark_v10.ipynb` | Run 1 notebook (main benchmark) |
| `presupfail_run3_pvp_mitigation.ipynb` | Run 3 notebook (PVP) |
| `presupfail_main_v10_fully_annotated.jsonl` | 720 fully annotated responses (Run 1) |
| `presupfail_final_results_summary.json` | All statistical results (Run 1) |
| `pvf_orr_bcs.json` | PVF, ORR, BCS metrics |
