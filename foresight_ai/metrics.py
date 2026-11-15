"""Compare matched claim conditions without treating synthetic outputs as results."""
from collections import defaultdict
from typing import Any


def summarize(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int | None]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["condition"]].append(row)
    baseline = {row["claim_id"]: row["predicted"] for row in rows
                if row["condition"] == "evidence_only"}
    results: dict[str, dict] = {}
    for condition, group in groups.items():
        cited_count = sum(len(row["evidence_ids"]) for row in group)
        valid_citations = sum(sum(eid in row["available_evidence_ids"] for eid in row["evidence_ids"])
                              for row in group)
        cited_rows = sum(bool(row["evidence_ids"]) for row in group)
        matched = [row for row in group if row["claim_id"] in baseline]
        changed = sum(row["predicted"] != baseline[row["claim_id"]] for row in matched)
        aligned = sum(row["predicted"] == row["gold"] for row in group)
        result: dict[str, float | int | None] = {
            "samples": len(group),
            "verdict_accuracy": round(aligned / len(group), 4),
            "flip_rate_vs_evidence_only": round(changed / len(matched), 4) if matched else None,
            "citation_id_validity": round(valid_citations / cited_count, 4) if cited_count else None,
            "citation_coverage": round(cited_rows / len(group), 4),
            "invalid_output_rate": round(sum(row["predicted"] == "INVALID" for row in group) / len(group), 4),
        }
        if condition == "evidence_rescue":
            errors = [row for row in group if row.get("prior_predicted") not in (None, "INVALID", row["gold"])]
            rescued = sum(row["predicted"] == row["gold"] for row in errors)
            result["recovery_rate_on_prior_error"] = round(rescued / len(errors), 4) if errors else None
            result["prior_error_count"] = len(errors)
        results[condition] = result
    return results
