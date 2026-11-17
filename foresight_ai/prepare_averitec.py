"""Prepare reproducible AVeriTeC pilot samples; keep original data out of Git."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
from urllib.error import URLError
from urllib.request import Request, urlopen

from .dataset import _normalize_label, load_claims

SOURCE_BASE = "https://raw.githubusercontent.com/MichSchli/AVeriTeC/main/data"
BINARY_LABELS = ("Supported", "Refuted")


def download_official_split(split: str, destination: Path) -> None:
    """Opt-in download from the published AVeriTeC maintainers' repository."""
    if split not in ("train", "dev"):
        raise ValueError("Only the published train/dev splits may be downloaded")
    url = f"{SOURCE_BASE}/{split}.json"
    request = Request(url, headers={"User-Agent": "ForesightAI-course-research/0.1"})
    limit_bytes = 25 * 1024 * 1024
    try:
        with urlopen(request, timeout=45) as response:
            chunks = []
            total = 0
            while chunk := response.read(65536):
                total += len(chunk)
                if total > limit_bytes:
                    raise ValueError("Dataset exceeds the 25 MiB download limit")
                chunks.append(chunk)
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(
            f"Could not download official {split} split. "
            "You can download it manually from fever.ai/dataset/averitec.html."
        ) from exc
    raw = b"".join(chunks)
    if not isinstance(json.loads(raw), list):
        raise ValueError("Official download did not contain a JSON list")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)


def make_pilot(
    raw_records: list[dict], *, split: str, per_label: int = 25,
    seed: int = 733,
) -> tuple[list[dict], dict]:
    """Select evidence-bearing Supported/Refuted claims per class.

    We deliberately exclude NEE/conflicting verdicts from the main attack
    pilot: flipping the truth of a non-binary label is not well-defined.
    """
    if split not in ("train", "dev"):
        raise ValueError("Split must be train or dev")
    if per_label < 1:
        raise ValueError("per_label must be positive")
    groups: dict[str, list[dict]] = defaultdict(list)
    seen_claims: set[str] = set()
    excluded = Counter()
    for index, record in enumerate(raw_records):
        if not isinstance(record, dict):
            raise ValueError(f"Non-object input at position {index}")
        try:
            verdict = _normalize_label(record.get("label", ""))
        except ValueError:
            excluded["unknown_verdict"] += 1
            continue
        if verdict not in BINARY_LABELS:
            excluded["non_binary_label"] += 1
            continue
        claim = str(record.get("claim") or "").strip()
        if not claim:
            excluded["missing_claim"] += 1
            continue
        key = " ".join(claim.lower().split())
        if key in seen_claims:
            excluded["duplicate_claim"] += 1
            continue
        seen_claims.add(key)
        # Do not use unanswerable snippets as if they were evidence.
        usable = [
            a for question in record.get("questions", [])
            for a in question.get("answers", [])
            if str(a.get("answer_type") or "").lower() != "unanswerable"
            and str(a.get("answer") or "").strip()
        ]
        if not usable:
            excluded["no_usable_question_answers"] += 1
            continue
        prepared = dict(record)
        # The official files lack unique IDs; preserve original row identity.
        prepared["id"] = f"averitec-{split}-{index:05d}"
        groups[verdict].append(prepared)

    rng = random.Random(seed)
    for label in BINARY_LABELS:
        rng.shuffle(groups[label])
        if len(groups[label]) < per_label:
            raise ValueError(
                f"Not enough eligible {label} examples: "
                f"requested {per_label}, found {len(groups[label])}"
            )
    selected = [
        item for label in BINARY_LABELS for item in groups[label][:per_label]
    ]
    rng.shuffle(selected)
    return selected, {
        "dataset": "AVeriTeC",
        "source": SOURCE_BASE,
        "source_split": split,
        "purpose": "binary-verdict evidence-grounded rumor-pressure pilot",
        "seed": seed,
        "per_label": per_label,
        "selected_count": len(selected),
        "selected_labels": dict(Counter(item["label"] for item in selected)),
        "eligible_per_label": {k: len(groups[k]) for k in BINARY_LABELS},
        "excluded": dict(excluded),
        "selected_ids": [item["id"] for item in selected],
        "synthetic_social_posts": True,
        "validated_model_results": False,
        "note": (
            "Inspect sampled claims and evidence manually before scoring. "
            "Do not use dev claims for model training, examples, or prompt tuning."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select an annotated, reproducible AVeriTeC research pilot",
    )
    parser.add_argument("--split", choices=("train", "dev"), default="train")
    parser.add_argument("--input", help="Existing official AVeriTeC split JSON")
    parser.add_argument("--download", action="store_true",
                        help="Download selected split from the original authors")
    parser.add_argument("--per-label", type=int, default=25)
    parser.add_argument("--seed", type=int, default=733)
    parser.add_argument("--output", help="Generated local subset JSON path")
    parser.add_argument("--manifest", help="Audit metadata JSON path")
    args = parser.parse_args(argv)
    if args.input and args.download:
        parser.error("Use either --input or --download, not both")

    source = Path(args.input) if args.input else Path(
        f"data/averitec/{args.split}.json"
    )
    if args.download:
        if source.exists():
            print(f"Using existing dataset: {source}; not overwriting")
        else:
            download_official_split(args.split, source)
    if not source.exists():
        parser.error(
            f"Missing {source}. Supply --input or opt in to --download"
        )
    raw = source.read_bytes()
    records = json.loads(raw)
    if not isinstance(records, list):
        parser.error("Expected official JSON array of claims")
    subset, manifest = make_pilot(
        records, split=args.split, per_label=args.per_label, seed=args.seed,
    )
    output = Path(args.output or f"data/averitec/pilot_{args.split}.json")
    manifest_path = Path(args.manifest or f"outputs/averitec_{args.split}_manifest.json")
    if output.resolve() == source.resolve():
        parser.error("Refusing to overwrite the original dataset")
    manifest["source_sha256"] = hashlib.sha256(raw).hexdigest()
    manifest["sample_sha256"] = hashlib.sha256(
        json.dumps(subset, sort_keys=True).encode("utf-8")
    ).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(subset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # Reuse the real prompt loader to catch schema mismatches immediately.
    if len(load_claims(output)) != len(subset):
        raise AssertionError("Selection and experiment loader disagree")
    print(
        f"Prepared {len(subset)} claims ({args.per_label} per binary class) "
        f"from {args.split}: {output}"
    )
    print(f"Provenance manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
