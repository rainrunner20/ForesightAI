"""Convert AVeriTeC annotated claims into stable, source-aware experiment cases."""
from dataclasses import dataclass
import json
from pathlib import Path

VERDICTS = (
    "Supported", "Refuted", "Not Enough Evidence",
    "Conflicting Evidence/Cherry-picking",
)


@dataclass(frozen=True)
class Evidence:
    id: str
    text: str
    source_url: str = ""


@dataclass(frozen=True)
class Claim:
    id: str
    text: str
    gold_verdict: str
    evidence: tuple[Evidence, ...]


def _normalize_label(label: str) -> str:
    mapping = {name.lower(): name for name in VERDICTS}
    # The official AVeriTeC file also uses "Cherrypicking" without a hyphen.
    mapping["conflicting evidence/cherrypicking"] = "Conflicting Evidence/Cherry-picking"
    key = str(label).strip().lower().replace("_", " ")
    if key not in mapping:
        raise ValueError(f"Unsupported verdict label: {label!r}")
    return mapping[key]


def load_claims(path: str | Path, limit: int | None = None) -> list[Claim]:
    """Read AVeriTeC JSON or JSONL without fetching external links.

    Each QA answer is kept *with its question*. A standalone answer like
    "No" isn't interpretable evidence without the question being answered.
    """
    path = Path(path)
    data = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        records = [json.loads(line) for line in data.splitlines() if line.strip()]
    else:
        records = json.loads(data)
    if not isinstance(records, list):
        raise ValueError("Expected a JSON array or JSONL records")
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")

    results: list[Claim] = []
    for index, record in enumerate(records[:limit] if limit else records):
        if not isinstance(record, dict):
            raise ValueError(f"Record {index} is not an object")
        claim_text = str(record.get("claim", "")).strip()
        if not claim_text:
            raise ValueError(f"Record {index} has no claim text")
        evidence: list[Evidence] = []
        for question in record.get("questions", []):
            question_text = str(question.get("question") or "").strip()
            for answer in question.get("answers", []):
                # AVeriTeC explicitly marks failed searches as unanswerable.
                # They are not affirmative or negative evidence.
                if str(answer.get("answer_type") or "").lower() == "unanswerable":
                    continue
                answer_text = str(answer.get("answer") or "").strip()
                if not answer_text:
                    continue
                explanation = str(answer.get("boolean_explanation") or "").strip()
                parts = []
                if question_text:
                    parts.append(f"Question: {question_text}")
                parts.append(f"Answer: {answer_text}" if question_text else answer_text)
                if explanation:
                    parts.append(f"Explanation: {explanation}")
                evidence.append(Evidence(
                    id=f"E{len(evidence) + 1}",
                    text="\n".join(parts),
                    source_url=str(answer.get("source_url") or ""),
                ))
        # The made-up demo fixture supports plain evidence text as well.
        for item in record.get("evidence", []):
            if isinstance(item, str) and item.strip():
                evidence.append(Evidence(
                    id=f"E{len(evidence) + 1}", text=item.strip(),
                ))
        results.append(Claim(
            id=str(record.get("id", index)), text=claim_text,
            gold_verdict=_normalize_label(record.get("label", "")),
            evidence=tuple(evidence[:8]),
        ))
    return results
