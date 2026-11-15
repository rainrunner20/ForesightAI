"""Run repeatable, paired conditions against the same set of claims."""
from dataclasses import asdict
from pathlib import Path
import json
from typing import Any

from .dataset import Claim
from .metrics import summarize
from .prompts import SYSTEM, make_prompt
from .providers import ModelProvider, parse_prediction
from .scenarios import CONDITIONS, make_scenario


def run_experiment(claims: list[Claim], provider: ModelProvider, post_count: int = 16,
                   provider_name: str = "mock", model_name: str = "mock") -> dict[str, Any]:
    if not claims:
        raise ValueError("No claims were loaded")
    records: list[dict[str, Any]] = []
    for claim in claims:
        for condition in CONDITIONS:
            scenario = make_scenario(claim, condition, post_count)
            response = parse_prediction(provider.predict(SYSTEM, make_prompt(claim, scenario)))
            records.append({"claim_id": claim.id, "claim": claim.text,
                            "condition": condition, "social_posts": scenario.post_count,
                            "gold": claim.gold_verdict, "predicted": response["verdict"],
                            "evidence_ids": response["evidence_ids"],
                            "available_evidence_ids": [item.id for item in claim.evidence],
                            "rationale": response["rationale"]})
    return {"metadata": {"provider": provider_name, "model": model_name,
                         "synthetic_demo": provider_name == "mock", "claim_count": len(claims),
                         "social_posts_per_condition": post_count,
                         "conditions": list(CONDITIONS)},
            "metrics": summarize(records), "rows": records}


def save_report(report: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
