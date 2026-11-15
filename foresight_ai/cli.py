"""Command-line entry point. Run `python -m foresight_ai.cli --help`."""
import argparse
import os
from pathlib import Path

from .dataset import load_claims
from .experiment import run_experiment, save_report
from .providers import MockProvider, OllamaProvider
from .scenarios import CONDITIONS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ForesightAI social-context reliability experiments")
    parser.add_argument("--input", default="data/demo_claims.json", help="AVeriTeC JSON or JSONL file")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of claims")
    parser.add_argument("--posts", type=int, default=16, help="Synthetic posts (0–100)")
    parser.add_argument("--provider", choices=("mock", "ollama"), default="mock")
    parser.add_argument("--model", default=os.getenv("OLLAMA_MODEL", "qwen3:4b"))
    parser.add_argument("--seed", type=int, default=733)
    parser.add_argument("--agents", type=int, default=120)
    parser.add_argument("--fact-checkers", type=float, default=0.15,
                        help="Fraction of synthetic agent population that fact-checks (0..1)")
    parser.add_argument("--conditions", default=",".join(CONDITIONS),
                        help="Comma-separated subset of scenario names")
    parser.add_argument("--output", default="outputs/latest.json")
    args = parser.parse_args(argv)
    if not 0 <= args.posts <= 100:
        parser.error("--posts must be between 0 and 100")
    if not 0 <= args.fact_checkers <= 1:
        parser.error("--fact-checkers must be 0..1")
    conditions = tuple(s.strip() for s in args.conditions.split(",") if s.strip())
    if not conditions or any(c not in CONDITIONS for c in conditions):
        parser.error(f"--conditions must use names from {', '.join(CONDITIONS)}")
    claims = load_claims(args.input, limit=args.limit)
    provider = MockProvider() if args.provider == "mock" else OllamaProvider(
        model=args.model, url=os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat"))
    try:
        report = run_experiment(claims, provider, post_count=args.posts, provider_name=args.provider,
                                model_name=("mock" if args.provider == "mock" else args.model),
                                seed=args.seed, agents=args.agents,
                                fact_checker_ratio=args.fact_checkers, conditions=conditions)
    except ValueError as exc:
        parser.error(str(exc))
    save_report(report, args.output)
    label = "DEMO ONLY (not real model measurements)" if args.provider == "mock" else "MODEL EXPERIMENT"
    print(f"{label}: wrote {len(report['rows'])} predictions to {Path(args.output).resolve()}")
    for condition, stats in report["metrics"].items():
        flip = stats["flip_rate_vs_evidence_only"]
        flip_text = f"{flip:.1%}" if flip is not None else "n/a"
        print(f"  {condition}: accuracy={stats['verdict_accuracy']:.1%}, flip rate={flip_text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
