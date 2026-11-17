"""Prepare and score human evidence-support reviews without pretending to automate truth.

The reviewer decides whether cited/source evidence supports the *model's
verdict*. A matching citation ID alone is never recorded as factual support.
"""
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from .dataset import Claim

SUPPORT_LABELS = (
    "supports", "contradicts", "insufficient", "mixed", "not_applicable",
)
CSV_FIELDS = (
    "report_sha256", "review_key", "claim_id", "condition", "claim_text",
    "model_verdict", "cited_evidence_ids", "invalid_cited_ids",
    "cited_evidence", "supplied_evidence", "model_rationale",
    "reviewer", "support_label", "review_notes",
)


def _review_key(claim_id: str, condition: str) -> str:
    return hashlib.sha256((claim_id + "\0" + condition).encode("utf-8")).hexdigest()[:24]


def _safe_csv(value: Any) -> str:
    """Prevent formula execution when exported source text opens in a spreadsheet."""
    text = str(value)
    if text.startswith(("=", "+", "-", "@", "\t", "\r", "\n")):
        return "'" + text
    return text


def _report_index(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed = {}
    for row in report.get("rows", []):
        key = _review_key(str(row["claim_id"]), str(row["condition"]))
        if key in indexed:
            raise ValueError(
                f"Duplicate claim-condition in report: {row['claim_id']} / {row['condition']}"
            )
        indexed[key] = row
    if not indexed:
        raise ValueError("Report contains no model predictions")
    return indexed


def export_reviews(
    report: dict[str, Any], claims: list[Claim],
    *, report_sha256: str, output: str | Path,
) -> int:
    """Generate an *ungraded* local CSV; gold labels are not shown to reviewers."""
    indexed = _report_index(report)
    claim_map = {claim.id: claim for claim in claims}
    if len(claim_map) != len(claims):
        raise ValueError("Claims file contains duplicate claim IDs")
    results: list[dict[str, str]] = []
    for key, prediction in indexed.items():
        claim_id = str(prediction["claim_id"])
        claim = claim_map.get(claim_id)
        if claim is None:
            raise ValueError(f"Missing source evidence for claim {claim_id}")
        evidence_by_id = {item.id: item for item in claim.evidence}
        cited = list(prediction.get("evidence_ids") or [])
        if any(not isinstance(eid, str) for eid in cited):
            raise ValueError(f"Invalid citation format on claim {claim_id}")
        invalid = [eid for eid in cited if eid not in evidence_by_id]
        def readable(item) -> str:
            return f"[{item.id}] {item.text}\nSource: {item.source_url or '(unavailable)'}"

        results.append({
            "report_sha256": report_sha256,
            "review_key": key,
            "claim_id": _safe_csv(claim_id),
            "condition": _safe_csv(prediction["condition"]),
            "claim_text": _safe_csv(claim.text),
            "model_verdict": _safe_csv(prediction["predicted"]),
            "cited_evidence_ids": _safe_csv(", ".join(cited)),
            "invalid_cited_ids": _safe_csv(", ".join(invalid)),
            "cited_evidence": _safe_csv("\n\n".join(
                readable(evidence_by_id[eid]) for eid in cited
                if eid in evidence_by_id
            )),
            "supplied_evidence": _safe_csv("\n\n".join(
                readable(item) for item in claim.evidence
            )),
            "model_rationale": _safe_csv(prediction.get("rationale") or ""),
            "reviewer": "",
            "support_label": "",
            "review_notes": "",
        })
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(results)
    return len(results)


def summarize_reviews(
    report: dict[str, Any], *, report_sha256: str,
    review_path: str | Path,
) -> dict[str, Any]:
    """Only human labels count; blank reviews never become unsupported verdicts."""
    indexed = _report_index(report)
    with Path(review_path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or any(f not in reader.fieldnames for f in CSV_FIELDS):
            raise ValueError("Review CSV is missing required columns")
        reviews = list(reader)
    if len(reviews) != len(indexed):
        raise ValueError("Review CSV row count does not match the model report")
    found: set[str] = set()
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in reviews:
        key = row["review_key"]
        if key in found or key not in indexed:
            raise ValueError("Review CSV has duplicate or unrecognized review keys")
        found.add(key)
        if row["report_sha256"] != report_sha256:
            raise ValueError("Review file belongs to a different model report")
        label = (row.get("support_label") or "").strip().lower()
        if label and label not in SUPPORT_LABELS:
            raise ValueError(f"Unknown support label {label!r} on row {key}")
        grouped[str(indexed[key]["condition"])].append(label)
    details = {}
    for condition, labels in grouped.items():
        counts = {label: labels.count(label) for label in SUPPORT_LABELS}
        assessed = sum(counts[label] for label in SUPPORT_LABELS if label != "not_applicable")
        details[condition] = {
            "rows": len(labels),
            "reviewed": len(labels) - labels.count(""),
            "unreviewed": labels.count(""),
            "not_applicable": counts["not_applicable"],
            "assessed_verdicts": assessed,
            "supports": counts["supports"],
            "contradicts": counts["contradicts"],
            "insufficient": counts["insufficient"],
            "mixed": counts["mixed"],
            "supported_fraction_of_assessed": (
                round(counts["supports"] / assessed, 4) if assessed else None
            ),
        }
    return {
        "report_sha256": report_sha256,
        "synthetic_demo": bool(report.get("metadata", {}).get("synthetic_demo", True)),
        "method": "human_review_of_evidence_support_for_model_verdict",
        "support_label_definitions": list(SUPPORT_LABELS),
        "overall_rows": len(indexed),
        "conditions": details,
        "warning": (
            "Human support labels are reviewer judgments; they do not "
            "automatically verify source authenticity or establish ground truth. "
            "Do not cite demo-provider reviews as model research outcomes."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Manual evidence-support audit")
    parser.add_argument("--report", required=True, help="Unmodified experiment JSON report")
    parser.add_argument("--claims", help="Same claims file used to produce report")
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--export", help="Create ungraded evidence review CSV")
    actions.add_argument("--review", help="Read human-filled CSV and score reviewed cases")
    parser.add_argument("--summary", help="Output JSON path when --review is set")
    args = parser.parse_args(argv)
    if args.export and not args.claims:
        parser.error("--export requires --claims")
    if args.summary and not args.review:
        parser.error("--summary requires --review")

    raw = Path(args.report).read_bytes()
    report = json.loads(raw)
    digest = hashlib.sha256(raw).hexdigest()
    if args.export:
        from .dataset import load_claims
        n = export_reviews(
            report, load_claims(args.claims),
            report_sha256=digest, output=args.export,
        )
        print(f"Prepared {n} ungraded evidence reviews: {args.export}")
    else:
        summary = summarize_reviews(
            report, report_sha256=digest, review_path=args.review,
        )
        output = Path(args.summary or "outputs/evidence_audit.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Human evidence-audit summary: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
