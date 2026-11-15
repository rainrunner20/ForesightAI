"""Command-line entry point. Run `python -m foresight_ai.cli --help`."""
import argparse
import os
from pathlib import Path

from .dataset import load_claims
from .experiment import run_experiment, save_report
from .providers import MockProvider, OllamaProvider


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ForesightAI social-context reliability experiments")
    parser.add_argument("--input", default="data/demo_claims.json", help="AVeriTeC JSON or JSONL file")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of claims")
    parser.add_argument("--posts", type=int, default=16, help="Synthetic misleading posts per condition (0–100)")
    parser.add_argument("--provider", choices=("mock", "ollama"), default="mock")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    parser.add_argument("--output", default="outputs/latest.json")
    args = parser.parse_args(argv)
    if not 0 <= args.posts <= 100:
        parser.error("--posts must be between 0 and 100")
    claims = load_claims(args.input, limit=args.limit)
    provider = MockProvider() if args.provider == "mock" else OllamaProvider(
        model=args.model, url=os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat"))
    report = run_experiment(claims, provider, post_count=args.posts, provider_name=args.provider,
                            model_name=("mock" if args.provider == "mock" else args.model))
    save_report(report, args.output)
    label = "DEMO ONLY (not real model measurements)" if args.provider == "mock" else "MODEL EXPERIMENT"
    print(f"{label}: wrote {len(report['rows'])} predictions to {Path(args.output).resolve()}")
    for condition, stats in report["metrics"].items():
        print(f"  {condition}: accuracy={stats['verdict_accuracy']:.1%}, flip rate={stats['flip_rate_vs_evidence_only']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
