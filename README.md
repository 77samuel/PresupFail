# PresupFail

**A linguistically grounded benchmark and evaluation framework for presupposition-induced hallucinations in small language models.**

Repository: https://github.com/77samuel/PresupFail

## Overview

PresupFail studies how small language models (sub-7B parameters) respond when a question's
linguistic structure presupposes a false proposition. Different presupposition trigger types
(factive, existential, change-of-state, aspectual, definite description, cleft) produce
systematically different hallucination behaviors. We introduce:

- **PresupFail-60** — a 60-item benchmark, 10 items per trigger type, each with a paired
  knowledge probe and presupposition probe
- **Response taxonomy (R/P/F/A/U)** — Rejection, Partial correction, Fabrication,
  Accommodation, Uncertainty
- **PVF** — Presupposition Vulnerability Fingerprint, a per-trigger per-model rejection profile
- **ORR / BCS** — Overall Rejection Rate and Behavioral Consistency Score
- **PVP** — Presupposition Verification Protocol, a lightweight inference-time intervention

## Repository Structure
PresupFail/

├── benchmark/                  Frozen benchmark dataset (v1.0)

├── docs/                       Pre-registration, annotation guidelines, experiment log

├── code/                       Inference pipeline and Kaggle notebooks

├── results/                    Raw and annotated model outputs

│   ├── stress_test/             Calibration run (not reported in paper)

│   ├── main_v10/                 Main benchmark run (720 responses)

│   └── pvp_mitigation/           PVP intervention run (356 responses)

└── annotation_tasks/           Inter-rater reliability annotation sheets


## Models Evaluated

| Model | HuggingFace ID |
|---|---|
| Llama-3.2-3B-Instruct | meta-llama/Llama-3.2-3B-Instruct |
| Qwen2.5-3B-Instruct | Qwen/Qwen2.5-3B-Instruct |

## Reproducing the Experiments

```bash
pip install -r requirements.txt
```

1. **Main benchmark run** (temperature=0.3):
```bash
   python code/presupfail_inference.py \
     --input benchmark/presupfail_items_benchmark_v10.json \
     --models llama3.2-3b qwen2.5-3b \
     --generations 3 --mode main \
     --output results/main_v10/
```

2. **PVP mitigation run**: see `code/presupfail_run3_pvp_mitigation.ipynb`
   (designed for Kaggle T4 GPU; requires a HuggingFace token with access to
   the Llama-3.2 license).

Full experimental parameters (seeds, temperature, environment versions) are
recorded in `docs/presupfail_reproducibility_manifest.md`.

## Annotation Protocol

Responses are labeled using a frozen decision tree (`docs/presupfail_annotation_guidelines_v2.2.md`):
R → P → F → A → U   (precedence order)

Inter-rater reliability: Cohen's κ = 0.862 (n=50, two independent raters).

## Key Findings

- Trigger type significantly predicts hallucination behavior
  (χ² = 151.4, p < 0.0001, Cramér's V = 0.324)
- Aspectual and Cleft triggers show the lowest baseline rejection rates
- The PVP intervention significantly increases premise-flagging rate
  (McNemar's exact test, p = 5.08 × 10⁻¹⁹), with the largest gains on the
  weakest baseline triggers (Spearman ρ = -1.000, exact p = 0.0028)
- Failures are predominantly pragmatic (models know the fact but fail to
  apply it under presupposition framing) rather than epistemic

## Citation

If you use this benchmark or code, please cite:
Stephen, S. and Vignesh, R. (2026). [Paper title — to be finalized].

[Journal/Venue]. https://github.com/77samuel/PresupFail

## Authors

- Samuel Stephen — Karunya Institute of Technology and Sciences, Coimbatore, India
  (samuels24@karunya.edu.in, ORCID: 0009-0002-9446-000X)
- R. Vignesh — Karunya Institute of Technology and Sciences, Coimbatore, India
  (vignesh@karunya.edu, ORCID: 0009-0008-0134-8726)
