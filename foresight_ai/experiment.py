"""Run paired claim trials with transparent prompt and result accounting."""
from pathlib import Path
import json
from typing import Any

from .dataset import Claim
from .metrics import summarize
from .prompts import SYSTEM, make_prompt
from .providers import ModelProvider, parse_prediction
from .scenarios import CONDITIONS, make_scenario
from .token_controls import TokenCounter, make_neutral_length_control, token_count

OPTIONAL_CONDITIONS = ("neutral_length_control",)
AVAILABLE_CONDITIONS = CONDITIONS + OPTIONAL_CONDITIONS


def run_experiment(claims: list[Claim], provider: ModelProvider, post_count: int = 16,
                   provider_name: str = "mock", model_name: str = "mock", *,
                   seed: int = 733, agents: int = 120,
                   fact_checker_ratio: float = 0.15,
                   conditions: tuple[str, ...] = CONDITIONS,
                   token_counter: TokenCounter | None = None,
                   tokenizer_name: str | None = None) -> dict[str, Any]:
    if not claims:
        raise ValueError("No claims were loaded")
    if not conditions or any(c not in AVAILABLE_CONDITIONS for c in conditions):
        raise ValueError("Unknown or empty condition selection")
    if len(set(conditions)) != len(conditions):
        raise ValueError("Duplicate experiment conditions")
    if "evidence_rescue" in conditions and "rumor_pressure" not in conditions:
        raise ValueError("evidence_rescue requires rumor_pressure in the same run")
    if "neutral_length_control" in conditions:
        if "rumor_pressure" not in conditions:
            raise ValueError("neutral_length_control requires rumor_pressure")
        if token_counter is None:
            raise ValueError("neutral_length_control requires a real tokenizer")

    rows: list[dict[str, Any]] = []
    replay: list[dict[str, Any]] = []
    network_samples: dict[str, dict] = {}
    # Rescue depends on a prior rumor verdict; always run it last.
    ordered = tuple(c for c in conditions if c != "evidence_rescue")
    if "evidence_rescue" in conditions:
        ordered += ("evidence_rescue",)
    for claim in claims:
        prior_rumor_verdict: str | None = None
        steps = []
        for condition in ordered:
            target_tokens: int | None = None
            if condition == "neutral_length_control":
                rumor = make_scenario(
                    claim, "rumor_pressure", post_count, seed=seed, agents=agents,
                    fact_checker_ratio=fact_checker_ratio,
                )
                scenario, target_tokens, _ = make_neutral_length_control(
                    claim, rumor, token_counter,
                )
            else:
                scenario = make_scenario(
                    claim, condition, post_count, seed=seed, agents=agents,
                    fact_checker_ratio=fact_checker_ratio,
                )
            prompt = make_prompt(claim, scenario, prior_verdict=prior_rumor_verdict)
            prompt_tokens = (
                token_count(SYSTEM, prompt, token_counter) if token_counter else None
            )
            raw = provider.predict(SYSTEM, prompt)
            response = parse_prediction(raw)
            if condition == "rumor_pressure":
                prior_rumor_verdict = response["verdict"]
            row = {
                "claim_id": claim.id, "claim": claim.text,
                "condition": condition, "social_posts": scenario.post_count,
                "gold": claim.gold_verdict, "predicted": response["verdict"],
                "evidence_ids": response["evidence_ids"],
                "available_evidence_ids": [item.id for item in claim.evidence],
                "rationale": response["rationale"],
                "prior_predicted": (
                    prior_rumor_verdict if condition == "evidence_rescue" else None
                ),
                "step": len(steps),
                "prompt_tokens": prompt_tokens,
                "neutral_target_tokens": target_tokens,
                "token_gap_vs_rumor": (
                    prompt_tokens - target_tokens
                    if prompt_tokens is not None and target_tokens is not None else None
                ),
            }
            rows.append(row)
            steps.append({
                "condition": condition, "step": len(steps),
                "social_posts": scenario.post_count, "predicted": response["verdict"],
                "evidence_ids": response["evidence_ids"],
                "rationale": response["rationale"],
                "prompt_tokens": prompt_tokens,
            })
            if scenario.simulation and len(network_samples) < 3:
                network_samples[claim.id] = scenario.simulation
        replay.append({
            "claim_id": claim.id, "claim": claim.text,
            "gold": claim.gold_verdict, "steps": steps,
        })
    return {
        "metadata": {
            "schema_version": 2, "provider": provider_name, "model": model_name,
            "synthetic_demo": provider_name == "mock",
            "claim_count": len(claims), "seed": seed,
            "agent_count": agents, "fact_checker_ratio": fact_checker_ratio,
            "social_posts_per_condition": post_count,
            "conditions": list(ordered),
            "tokenizer": tokenizer_name,
            "token_count_scope": "system_plus_user_text_without_chat_template",
            "neutral_length_tolerance_tokens": 1 if token_counter else None,
        },
        "metrics": summarize(rows),
        "rows": rows, "replay": replay, "network_samples": network_samples,
    }


def save_report(report: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
