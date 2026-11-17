"""Load paired source/reply stance examples without downloading datasets."""
import csv
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

LABELS = ("support", "deny", "query", "comment")


@dataclass(frozen=True)
class StanceExample:
    id: str
    source_text: str
    reply_text: str
    label: int
    thread_id: str = ""

    @property
    def input_text(self) -> str:
        # Both the source rumor and its reply matter for the stance.
        return self.source_text + "\n[REPLY]\n" + self.reply_text

    @property
    def source_fingerprint(self) -> str:
        normalized = " ".join(self.source_text.lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_label(value: object) -> int:
    aliases = {
        "support": 0, "supporting": 0,
        "deny": 1, "denying": 1,
        "query": 2, "question": 2, "questioning": 2,
        "comment": 3, "commenting": 3,
    }
    if type(value) is int and 0 <= value < len(LABELS):
        return value
    name = str(value).strip().lower()
    if name in aliases:
        return aliases[name]
    if name in ("0", "1", "2", "3"):
        return int(name)
    raise ValueError(f"Unsupported stance label: {value!r}")


def load_stance_split(path: str | Path) -> list[StanceExample]:
    """Read exported RumourEval-style CSV, JSONL or JSON records.

    Required columns: source_text, reply_text, label.
    Optional columns: id, thread_id. Do not merge unrelated rumor threads.
    """
    path = Path(path)
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            records = list(csv.DictReader(handle))
    elif path.suffix.lower() == ".jsonl":
        records = [
            json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    elif path.suffix.lower() == ".json":
        records = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Expected .csv, .json, or .jsonl: {path}")
    if not isinstance(records, list) or not records:
        raise ValueError(f"Expected a nonempty array or CSV of stance examples: {path}")
    result = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{path}: record {index} must be an object")
        source = str(record.get("source_text", "")).strip()
        reply = str(record.get("reply_text", "")).strip()
        if not source or not reply:
            raise ValueError(f"{path}: record {index} needs source_text and reply_text")
        label = normalize_label(record.get("label"))
        result.append(StanceExample(
            id=str(record.get("id", index)),
            source_text=source, reply_text=reply, label=label,
            thread_id=str(record.get("thread_id") or "").strip(),
        ))
    return result


def validate_split_isolation(
    train: list[StanceExample], dev: list[StanceExample],
    test: list[StanceExample],
) -> None:
    """Do not train on another reply from the same source rumor/thread."""
    def keys(rows: list[StanceExample]) -> set[str]:
        found: set[str] = set()
        for row in rows:
            found.add("source:" + row.source_fingerprint)
            if row.thread_id:
                found.add("thread:" + row.thread_id)
        return found

    for name_a, rows_a, name_b, rows_b in (
        ("train", train, "dev", dev),
        ("train", train, "test", test),
        ("dev", dev, "test", test),
    ):
        if keys(rows_a) & keys(rows_b):
            raise ValueError(
                f"Possible thread/source leakage across {name_a}/{name_b}; "
                "use thread-disjoint splits and review the dataset IDs."
            )
    if set(row.label for row in train) != set(range(4)):
        raise ValueError("Training split must contain all four stance classes")
