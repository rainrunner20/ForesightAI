"""Run repeated, paired claim trials with interpretable attack variants."""
from pathlib import Path
import json
from typing import Any

from .dataset import Claim
from .metrics import summarize
from .prompts import SYSTEM, make_prompt
from .providers import ModelProvider, parse_prediction
from .scenarios import CONDITIONS, make_scenario


def run_experiment(claims: list[Claim], provider: ModelProvider, post_count: int = 16,
                   provider_name: str = "mock", model_name: str = "mock", *,
                   seed: int = 733, agents: int = 120,
                   fact_checker_ratio: float = 0.15,
                   conditions: tuple[str, ...] = CONDITIONS) -> dict[str, Any]:
    if not claims:
        raise ValueError("No claims were loaded")
    if not conditions or any(c not in CONDITIONS for c in conditions):
        raise ValueError("Unknown or empty condition selection")
    if len(set(conditions)) != len(conditions):
        raise ValueError("Duplicate experiment conditions")
    if "evidence_rescue" in conditions and "rumor_pressure" not in conditions:
        raise ValueError("evidence_rescue requires rumor_pressure in the same run")

    rows: list[dict[str, Any]] = []
    replay: list[dict[str, Any]] = []
    network_samples: dict[str, dict] = {}
    # Claims are evaluated in a stable order, with a replay of their predictions.
    for claim in claims:
        prior_rumor_verdict: str | None = None
        steps = []
        # Always run rescue after rumor pressure, even if a caller provided a custom order.
        ordered = tuple(c for c in conditions if c != "evidence_rescue")
        if "evidence_rescue" in conditions:
            ordered += ("evidence_rescue",)
        for condition in ordered:
            scenario = make_scenario(claim, condition, post_count, seed=seed, agents=agents,
                                     fact_checker_ratio=fact_checker_ratio)
            prompt = make_prompt(claim, scenario, prior_verdict=prior_rumor_verdict)
            raw = provider.predict(SYSTEM, prompt)
            response = parse_prediction(raw)
            if condition == "rumor_pressure":
                prior_rumor_verdict = response["verdict"]
            row = {"claim_id": claim.id, "claim": claim.text,
                   "condition": condition, "social_posts": scenario.post_count,
                   "gold": claim.gold_verdict, "predicted": response["verdict"],
                   "evidence_ids": response["evidence_ids"],
                   "available_evidence_ids": [item.id for item in claim.evidence],
                   "rationale": response["rationale"],
                   "prior_predicted": prior_rumor_verdict if condition == "evidence_rescue" else None,
                   "step": len(steps)}
            rows.append(row)
            steps.append({"condition": condition, "step": len(steps),
                          "social_posts": scenario.post_count, "predicted": response["verdict"],
                          "evidence_ids": response["evidence_ids"],
                          "rationale": response["rationale"]})
            if scenario.simulation and len(network_samples) < 3:
                network_samples[claim.id] = scenario.simulation
        replay.append({"claim_id": claim.id, "claim": claim.text,
                       "gold": claim.gold_verdict, "steps": steps})
    return {"metadata": {"schema_version": 2, "provider": provider_name,
                         "model": model_name, "synthetic_demo": provider_name == "mock",
                         "claim_count": len(claims), "seed": seed,
                         "agent_count": agents, "fact_checker_ratio": fact_checker_ratio,
                         "social_posts_per_condition": post_count,
                         "conditions": list(ordered)},
            "metrics": summarize(rows), "rows": rows,
            "replay": replay, "network_samples": network_samples}


def save_report(report: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
