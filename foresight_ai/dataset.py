"""Convert AVeriTeC-style annotated claims into stable experiment cases."""
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

VERDICTS = ("Supported", "Refuted", "Not Enough Evidence", "Conflicting Evidence/Cherry-picking")


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
    key = str(label).strip().lower().replace("_", " ")
    if key not in mapping:
        raise ValueError(f"Unsupported verdict label: {label!r}")
    return mapping[key]


def load_claims(path: str | Path, limit: int | None = None) -> list[Claim]:
    """Read AVeriTeC JSON, or JSONL, without contacting third-party URLs."""
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
            for answer in question.get("answers", []):
                answer_text = str(answer.get("answer", "")).strip()
                if answer_text:
                    evidence.append(Evidence(id=f"E{len(evidence) + 1}", text=answer_text,
                                             source_url=str(answer.get("source_url", ""))))
        # The demo fixture also supports simple evidence strings for readable examples.
        for item in record.get("evidence", []):
            if isinstance(item, str) and item.strip():
                evidence.append(Evidence(id=f"E{len(evidence) + 1}", text=item.strip()))
        results.append(Claim(id=str(record.get("id", index)), text=claim_text,
                             gold_verdict=_normalize_label(record.get("label", "")),
                             evidence=tuple(evidence[:8])))
    return results
