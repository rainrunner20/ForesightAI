"""Claim-paired uncertainty estimates for the factual-verdict experiment.

All comparisons use *the same claims* in evidence_only and the candidate
condition. Mock-provider numbers can exercise code, not support conclusions.
"""
from collections import defaultdict
import math
import random
from typing import Any


def _quantile(sorted_values: list[float], probability: float) -> float:
    index = (len(sorted_values) - 1) * probability
    low = math.floor(index)
    high = math.ceil(index)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (index - low)


def _interval(samples: list[float]) -> list[float]:
    samples.sort()
    return [round(_quantile(samples, 0.025), 4), round(_quantile(samples, 0.975), 4)]


def _exact_mcnemar_p(harmful: int, helpful: int) -> float:
    """Two-sided exact binomial test for discordant matched correct/incorrect pairs."""
    discordant = harmful + helpful
    if discordant == 0:
        return 1.0
    smaller = min(harmful, helpful)
    # exp(log-combination - n*log(2)) avoids enormous integer intermediates.
    tail = math.fsum(
        math.exp(
            math.lgamma(discordant + 1)
            - math.lgamma(k + 1)
            - math.lgamma(discordant - k + 1)
            - discordant * math.log(2)
        )
        for k in range(smaller + 1)
    )
    return round(min(1.0, 2 * tail), 6)


def paired_inference(
    rows: list[dict[str, Any]], *, seed: int = 733,
    resamples: int = 2000,
) -> dict[str, dict[str, Any]]:
    """Compute bootstrap uncertainty and exact McNemar p from matched claims.

    A missing or malformed output is excluded from paired inference (and must
    still be counted by the separate invalid-output metric). Each claim is a
    single sampling unit. This is not repeated-run/model-seed uncertainty.
    """
    if resamples < 100:
        raise ValueError("Need at least 100 bootstrap resamples")
    indexed: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        condition, claim_id = row["condition"], str(row["claim_id"])
        if claim_id in indexed[condition]:
            raise ValueError(
                f"Duplicate claim/condition pair: {claim_id} / {condition}. "
                "Use a separate trial identifier before pooling repeated runs."
            )
        indexed[condition][claim_id] = row

    baseline = indexed.get("evidence_only", {})
    results: dict[str, dict[str, Any]] = {}
    rng = random.Random(seed)
    for condition, cases in indexed.items():
        if condition == "evidence_only":
            continue
        matched: list[tuple[int, int]] = []
        for claim_id, row in cases.items():
            other = baseline.get(claim_id)
            if other is None:
                continue
            if row["gold"] != other["gold"]:
                raise ValueError(f"Contradictory gold labels on claim {claim_id}")
            if "INVALID" in (row["predicted"], other["predicted"]):
                continue
            matched.append((
                int(other["predicted"] == other["gold"]),
                int(row["predicted"] == row["gold"]),
            ))
        n = len(matched)
        harmful = sum(a == 1 and b == 0 for a, b in matched)
        helpful = sum(a == 0 and b == 1 for a, b in matched)
        result: dict[str, Any] = {
            "paired_claims": n,
            "harmful_flips": harmful,
            "helpful_flips": helpful,
            "paired_accuracy_difference": (
                round(sum(b - a for a, b in matched) / n, 4) if n else None
            ),
            "harmful_flip_rate_ci95": None,
            "helpful_flip_rate_ci95": None,
            "accuracy_difference_ci95": None,
            "mcnemar_exact_two_sided_p": (
                _exact_mcnemar_p(harmful, helpful) if n else None
            ),
        }
        if n >= 2:
            harmful_rates = []
            helpful_rates = []
            differences = []
            for _ in range(resamples):
                sample = [matched[rng.randrange(n)] for _ in range(n)]
                harmful_rates.append(
                    sum(a == 1 and b == 0 for a, b in sample) / n
                )
                helpful_rates.append(
                    sum(a == 0 and b == 1 for a, b in sample) / n
                )
                differences.append(sum(b - a for a, b in sample) / n)
            result["harmful_flip_rate_ci95"] = _interval(harmful_rates)
            result["helpful_flip_rate_ci95"] = _interval(helpful_rates)
            result["accuracy_difference_ci95"] = _interval(differences)
        results[condition] = result
    return results
