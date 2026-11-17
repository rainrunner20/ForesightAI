"""Train or evaluate optional stance classifiers on prepared dataset splits."""
import argparse
import json
from pathlib import Path

from .stance_data import load_stance_split, validate_split_isolation
from .stance_models import run_tfidf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="RumourEval stance: source/reply support, deny, query, comment",
    )
    parser.add_argument("--backend", choices=("tfidf", "bert"), default="tfidf")
    parser.add_argument("--train", required=True, help="Training split CSV/JSON/JSONL")
    parser.add_argument("--dev", required=True, help="Validation split CSV/JSON/JSONL")
    parser.add_argument("--test", required=True, help="Untouched held-out split")
    parser.add_argument("--output-dir", default="outputs/stance")
    parser.add_argument("--seed", type=int, default=733)
    parser.add_argument("--model-id", default="google-bert/bert-base-uncased")
    parser.add_argument("--epochs", type=float, default=2)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--allow-model-download", action="store_true",
                        help="Allow downloading the explicitly named BERT checkpoint")
    args = parser.parse_args(argv)

    try:
        train = load_stance_split(args.train)
        dev = load_stance_split(args.dev)
        test = load_stance_split(args.test)
        validate_split_isolation(train, dev, test)
        if args.backend == "tfidf":
            report = run_tfidf(
                train, dev, test, output_dir=args.output_dir, seed=args.seed,
            )
        else:
            from .stance_bert import run_bert
            report = run_bert(
                train, dev, test, output_dir=args.output_dir, seed=args.seed,
                model_id=args.model_id, epochs=args.epochs,
                batch_size=args.batch_size, max_length=args.max_length,
                allow_download=args.allow_model_download,
            )
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))

    path = Path(args.output_dir) / f"{args.backend}_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Model: {args.backend}; report: {path.resolve()}")
    print(
        f"Held-out accuracy={report['test_metrics']['accuracy']:.3f}, "
        f"macro-F1={report['test_metrics']['macro_f1']:.3f}, "
        f"support/deny/query F1={report['test_metrics']['macro_f1_sdq']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
