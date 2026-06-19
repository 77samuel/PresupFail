"""
PresupFail Inference Pipeline v1.1
===================================
Changes from v1.0:
  - Temperature split: 0.7 for ambiguity stress test, 0.3 for main experiment
  - Records transformers/torch/CUDA/model_revision for reproducibility
  - Knowledge probe accuracy computed and saved separately
  - Item and probe order randomized per model (seed-controlled)
  - Predefined exclusion criteria applied at generation time

Usage:
    # Ambiguity stress test (temperature=0.7):
    python presupfail_inference.py \
        --input presupfail_items_pilot.json \
        --models llama3.2-3b qwen2.5-3b \
        --generations 3 \
        --mode stress_test \
        --output results/stress_test/

    # Main experiment (temperature=0.3):
    python presupfail_inference.py \
        --input presupfail_items_pilot.json \
        --models llama3.2-3b qwen2.5-3b \
        --generations 3 \
        --mode main \
        --output results/main/

Output:
    results/raw_responses.jsonl        — one line per response
    results/excluded_responses.jsonl   — excluded outputs with reason
    results/knowledge_probe_accuracy.json — per-model knowledge accuracy
    results/run_summary.json           — full run metadata
"""

import json
import time
import argparse
import os
import re
import random
import platform
from datetime import datetime
from pathlib import Path

import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM

# ── Model registry ─────────────────────────────────────────────────────────────
MODEL_REGISTRY = {
    "llama3.2-1b":  "meta-llama/Llama-3.2-1B-Instruct",
    "llama3.2-3b":  "meta-llama/Llama-3.2-3B-Instruct",
    "qwen2.5-1.5b": "Qwen/Qwen2.5-1.5B-Instruct",
    "qwen2.5-3b":   "Qwen/Qwen2.5-3B-Instruct",
    "gemma3-1b":    "google/gemma-3-1b-it",
    "gemma3-4b":    "google/gemma-3-4b-it",
}

# ── Temperature config ─────────────────────────────────────────────────────────
TEMPERATURE = {
    "stress_test": 0.7,   # ambiguity boundary test — higher variance desired
    "main":        0.3,   # main experiment — reproducibility prioritized
}

# ── Uncertainty marker patterns ────────────────────────────────────────────────
UNCERTAINTY_PATTERNS = [
    r"\bi'?m not sure\b", r"\bit appears\b", r"\blikely\b",
    r"\bprobably\b", r"\bpossibly\b", r"\bseems to\b",
    r"\bmay have\b", r"\bmight have\b", r"\baccording to available\b",
    r"\bi believe\b", r"\bi think\b", r"\bunclear\b",
    r"\bit'?s possible\b", r"\bcould be\b", r"\bapparently\b",
]
UNCERTAINTY_RE = re.compile("|".join(UNCERTAINTY_PATTERNS), re.IGNORECASE)

# ── Predefined exclusion criteria ─────────────────────────────────────────────
MIN_RESPONSE_TOKENS = 5      # shorter = likely truncated or empty
MAX_RESPONSE_TOKENS = 600    # longer = likely runaway generation

SAFETY_PATTERNS = [
    r"i'?m sorry,? i can'?t",
    r"i cannot (help|assist|provide|generate)",
    r"as an ai,? i (cannot|am not able)",
    r"this (request|question|prompt) (violates|goes against)",
    r"i'?m not able to (help|assist) with",
]
SAFETY_RE = re.compile("|".join(SAFETY_PATTERNS), re.IGNORECASE)


def get_exclusion_reason(text: str, response_tokens: int) -> str | None:
    """Returns exclusion reason string, or None if response is valid."""
    if not text or not text.strip():
        return "empty_output"
    if response_tokens < MIN_RESPONSE_TOKENS:
        return "truncated_too_short"
    if response_tokens > MAX_RESPONSE_TOKENS:
        return "runaway_generation"
    if SAFETY_RE.search(text):
        return "safety_filter_refusal"
    return None


def has_uncertainty_marker(text: str) -> bool:
    return bool(UNCERTAINTY_RE.search(text))


# ── Environment metadata ───────────────────────────────────────────────────────
def get_env_metadata() -> dict:
    cuda_version = "N/A"
    if torch.cuda.is_available():
        try:
            cuda_version = torch.version.cuda or "N/A"
        except Exception:
            pass
    return {
        "transformers_version": transformers.__version__,
        "torch_version":        torch.__version__,
        "cuda_version":         cuda_version,
        "python_version":       platform.python_version(),
        "platform":             platform.system(),
    }


# ── Item loader ────────────────────────────────────────────────────────────────
def load_items(path: str) -> list[dict]:
    with open(path) as f:
        items = json.load(f)
    required = {
        "item_id", "trigger_type", "domain",
        "embedded_false_proposition",
        "knowledge_probe", "presupposition_probe",
        "gold_answer", "source",
    }
    for item in items:
        missing = required - item.keys()
        if missing:
            raise ValueError(f"Item {item.get('item_id','?')} missing: {missing}")
    return items


# ── Model loader ───────────────────────────────────────────────────────────────
def load_model(model_key: str) -> tuple:
    model_id = MODEL_REGISTRY[model_key]
    print(f"\nLoading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.eval()

    # Get model revision/commit hash for reproducibility
    try:
        from huggingface_hub import model_info
        info = model_info(model_id)
        revision = info.sha or "unknown"
    except Exception:
        revision = "unknown"

    return tokenizer, model, model_id, revision


# ── Single generation ──────────────────────────────────────────────────────────
def generate_response(
    tokenizer,
    model,
    prompt: str,
    temperature: float,
    max_new_tokens: int,
    seed: int,
) -> dict:
    torch.manual_seed(seed)
    random.seed(seed)

    messages = [{"role": "user", "content": prompt}]
    if hasattr(tokenizer, "apply_chat_template"):
        input_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        input_text = f"User: {prompt}\nAssistant:"

    inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
    prompt_tokens = inputs["input_ids"].shape[1]

    t0 = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=temperature > 0,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
            output_scores=True,          # token-level logits
        )
    elapsed = round(time.time() - t0, 3)

    response_ids = outputs.sequences[0][prompt_tokens:]
    response_text = tokenizer.decode(response_ids, skip_special_tokens=True).strip()
    response_tokens = len(response_ids)

    # ── Compute log-probability statistics ──────────────────────────────────
    avg_log_prob   = None
    first_tok_prob = None
    total_log_prob = None

    try:
        import torch.nn.functional as F
        scores = outputs.scores          # tuple of (vocab_size,) tensors, one per generated token
        if scores and len(scores) > 0:
            log_probs = []
            for step_idx, score_tensor in enumerate(scores):
                if step_idx >= len(response_ids):
                    break
                token_id = response_ids[step_idx].item()
                lp = F.log_softmax(score_tensor[0], dim=-1)[token_id].item()
                log_probs.append(lp)

            if log_probs:
                total_log_prob   = round(sum(log_probs), 4)
                avg_log_prob     = round(sum(log_probs) / len(log_probs), 4)
                # first-token probability (linear scale)
                first_tok_prob   = round(float(torch.exp(torch.tensor(log_probs[0]))), 4)
    except Exception:
        pass   # logit capture is best-effort; never block the main pipeline

    return {
        "response_text":          response_text,
        "prompt_tokens":          prompt_tokens,
        "response_tokens":        response_tokens,
        "total_tokens":           prompt_tokens + response_tokens,
        "generation_time_sec":    elapsed,
        "has_uncertainty_marker": has_uncertainty_marker(response_text),
        "avg_log_prob":           avg_log_prob,      # mean per-token log-prob
        "first_token_prob":       first_tok_prob,    # linear prob of first generated token
        "total_log_prob":         total_log_prob,    # sum of per-token log-probs
        "seed":                   seed,
        "temperature":            temperature,
        "max_new_tokens":         max_new_tokens,
    }


# ── Per-item runner ────────────────────────────────────────────────────────────
def run_item(
    item: dict,
    probe_type: str,
    tokenizer,
    model,
    model_key: str,
    model_id: str,
    model_revision: str,
    n_generations: int,
    temperature: float,
    max_new_tokens: int,
    env_meta: dict,
    run_timestamp: str,
) -> tuple[list[dict], list[dict]]:
    """Returns (valid_records, excluded_records)."""

    prompt = (
        item["knowledge_probe"]
        if probe_type == "knowledge"
        else item["presupposition_probe"]
    )

    valid, excluded = [], []

    for gen_idx in range(n_generations):
        seed = 42 + gen_idx * 7

        try:
            gen = generate_response(
                tokenizer, model, prompt,
                temperature, max_new_tokens, seed,
            )
        except Exception as e:
            excluded.append({
                "item_id":        item["item_id"],
                "probe_type":     probe_type,
                "model_key":      model_key,
                "generation_index": gen_idx,
                "exclusion_reason": f"inference_error: {e}",
                "run_timestamp":  run_timestamp,
            })
            continue

        excl_reason = get_exclusion_reason(
            gen["response_text"], gen["response_tokens"]
        )

        base = {
            # item metadata
            "item_id":                    item["item_id"],
            "trigger_type":               item["trigger_type"],
            "domain":                     item["domain"],
            "embedded_false_proposition": item["embedded_false_proposition"],
            "gold_answer":                item["gold_answer"],
            "source":                     item["source"],
            # probe
            "probe_type":                 probe_type,
            "prompt":                     prompt,
            # model
            "model_key":                  model_key,
            "model_id":                   model_id,
            "model_revision":             model_revision,
            "generation_index":           gen_idx,
            # environment
            **env_meta,
            # generation output
            **gen,
            # annotation placeholders
            "label":         "",
            "evidence_span": "",
            "rater_id":      "",
            "notes":         "",
            "run_timestamp": run_timestamp,
        }

        if excl_reason:
            base["exclusion_reason"] = excl_reason
            excluded.append(base)
        else:
            valid.append(base)

    return valid, excluded


# ── Knowledge probe accuracy ───────────────────────────────────────────────────
def compute_knowledge_accuracy(records: list[dict]) -> dict:
    """
    Computes Knowledge Verification Rate (KVR) per model and per trigger type.

    Knowledge probe label set (separate from R/P/F/A/U presupposition taxonomy):
      C  — Correct:    model correctly identifies the embedded proposition as false
      I  — Incorrect:  model affirms or accepts the false proposition as true
      Ab — Abstain:    model declines without affirming or denying
      Fk — Fabricated: model gives a specific false answer not in the prompt

    KVR = C / (C + I + Ab + Fk)

    Only records with a non-empty label are included in KVR calculation.
    Records with empty labels are counted separately as unannotated.
    """
    from collections import defaultdict

    VALID_LABELS = {"C", "I", "Ab", "Fk"}

    # Per-model counts
    by_model = defaultdict(lambda: {"C": 0, "I": 0, "Ab": 0, "Fk": 0,
                                     "unannotated": 0, "total": 0})
    # Per-trigger counts
    by_trigger = defaultdict(lambda: {"C": 0, "I": 0, "Ab": 0, "Fk": 0,
                                       "unannotated": 0, "total": 0})

    for r in records:
        if r["probe_type"] != "knowledge":
            continue
        mk = r["model_key"]
        tt = r["trigger_type"]
        label = r.get("label", "").strip()

        by_model[mk]["total"] += 1
        by_trigger[tt]["total"] += 1

        if label in VALID_LABELS:
            by_model[mk][label] += 1
            by_trigger[tt][label] += 1
        else:
            by_model[mk]["unannotated"] += 1
            by_trigger[tt]["unannotated"] += 1

    def compute_kvr(counts: dict) -> float | None:
        denominator = counts["C"] + counts["I"] + counts["Ab"] + counts["Fk"]
        if denominator == 0:
            return None
        return round(counts["C"] / denominator, 4)

    result = {
        "by_model": {},
        "by_trigger": {},
        "formula": "KVR = C / (C + I + Ab + Fk)",
    }

    for mk, counts in by_model.items():
        result["by_model"][mk] = {**counts, "KVR": compute_kvr(counts)}

    for tt, counts in by_trigger.items():
        result["by_trigger"][tt] = {**counts, "KVR": compute_kvr(counts)}

    return result


# ── Randomized item/probe order ────────────────────────────────────────────────
def build_run_order(items: list[dict], model_idx: int) -> list[tuple[dict, str]]:
    """
    Returns shuffled list of (item, probe_type) pairs.
    Probe order is counterbalanced: even model_idx starts with knowledge,
    odd model_idx starts with presupposition.
    Item order is shuffled with a fixed seed per model index.
    """
    rng = random.Random(100 + model_idx)
    shuffled_items = items.copy()
    rng.shuffle(shuffled_items)

    pairs = []
    for item in shuffled_items:
        if model_idx % 2 == 0:
            pairs.append((item, "knowledge"))
            pairs.append((item, "presupposition"))
        else:
            pairs.append((item, "presupposition"))
            pairs.append((item, "knowledge"))
    return pairs


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",       required=True)
    parser.add_argument("--models",      nargs="+", default=["llama3.2-3b", "qwen2.5-3b"],
                        choices=list(MODEL_REGISTRY.keys()))
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--mode",        choices=["stress_test", "main"], default="main")
    parser.add_argument("--max_tokens",  type=int, default=300)
    parser.add_argument("--output",      default="results/")
    args = parser.parse_args()

    temperature = TEMPERATURE[args.mode]
    output_dir  = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    items       = load_items(args.input)
    env_meta    = get_env_metadata()
    run_ts      = datetime.utcnow().isoformat()

    print(f"Mode: {args.mode} | Temperature: {temperature}")
    print(f"Items: {len(items)} | Models: {args.models} | Generations: {args.generations}")
    print(f"Expected records: {len(items)*2*len(args.models)*args.generations}")

    all_valid, all_excluded = [], []

    for model_idx, model_key in enumerate(args.models):
        tokenizer, model, model_id, model_revision = load_model(model_key)
        run_order = build_run_order(items, model_idx)

        for item, probe_type in run_order:
            print(f"  [{model_key}] {item['item_id']} | {probe_type}")
            valid, excluded = run_item(
                item, probe_type,
                tokenizer, model,
                model_key, model_id, model_revision,
                args.generations, temperature, args.max_tokens,
                env_meta, run_ts,
            )
            all_valid.extend(valid)
            all_excluded.extend(excluded)

        del model, tokenizer
        torch.cuda.empty_cache()

    # ── Save outputs ─────────────────────────────────────────────────────────
    raw_path = output_dir / "raw_responses.jsonl"
    with open(raw_path, "w") as f:
        for r in all_valid:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    excl_path = output_dir / "excluded_responses.jsonl"
    with open(excl_path, "w") as f:
        for r in all_excluded:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    kp_path = output_dir / "knowledge_probe_accuracy.json"
    with open(kp_path, "w") as f:
        json.dump(compute_knowledge_accuracy(all_valid), f, indent=2)

    summary = {
        "run_timestamp":     run_ts,
        "mode":              args.mode,
        "temperature":       temperature,
        "input_file":        args.input,
        "models":            args.models,
        "n_items":           len(items),
        "n_generations":     args.generations,
        "max_new_tokens":    args.max_tokens,
        "expected_records":  len(items)*2*len(args.models)*args.generations,
        "valid_records":     len(all_valid),
        "excluded_records":  len(all_excluded),
        "exclusion_criteria": {
            "min_response_tokens": MIN_RESPONSE_TOKENS,
            "max_response_tokens": MAX_RESPONSE_TOKENS,
            "safety_filter":       True,
            "empty_output":        True,
            "inference_error":     True,
        },
        **env_meta,
    }
    with open(output_dir / "run_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDone. Valid: {len(all_valid)} | Excluded: {len(all_excluded)}")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()


# ── Knowledge probe evaluation (separate from R/P/F/A/U taxonomy) ──────────────
"""
Knowledge Probe Labels (separate taxonomy — do NOT use R/P/F/A/U):

  C  — Correct:     Model correctly states the embedded proposition is false
                    (or gives the factually accurate answer to the knowledge probe)
  I  — Incorrect:   Model accepts or affirms the false proposition as true
  Ab — Abstain:     Model declines to answer without affirming or denying
  Fk — Fabricated:  Model gives a specific false answer that was not in the prompt

Knowledge Verification Rate (KVR):
  KVR = C / (C + I + Ab + Fk)  per model, per trigger type

This is computed post-annotation. The placeholder structure is written to
knowledge_probe_accuracy.json at run time; raters fill in label counts after
annotation using the separate knowledge probe label set above.

Annotation unit for knowledge probes:
  Same as presupposition probes — first complete response only.
  Evidence span required for C and Fk labels.
  I and Ab may note absence of evidence.

Comparison logic:
  For each item, compare:
    Knowledge probe label (C/I/Ab/Fk)  vs
    Presupposition probe label (R/P/F/A/U)

  Key patterns:
    C + A or C + F  → Pragmatic failure (knows but accommodates)
    I + A or I + F  → Epistemic failure (doesn't know, accommodates)
    C + R           → Robust reasoning
    I + R           → Conservative/lucky rejection
"""

KNOWLEDGE_PROBE_LABELS = {
    "C":  "Correct — model correctly identifies the embedded proposition as false",
    "I":  "Incorrect — model affirms or accepts the false proposition",
    "Ab": "Abstain — model declines without affirming or denying",
    "Fk": "Fabricated — model gives a specific false answer not in the prompt",
}

KVR_FORMULA = "KVR = C / (C + I + Ab + Fk)"
