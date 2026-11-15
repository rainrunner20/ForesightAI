# Architecture and system boundaries

```text
    AVeriTeC annotated claims                RumourEval threads (future)
               |                                        |
       claim/evidence loader                   stance classifier (future)
               |                                        |
       synthetic social context <------- NetLogo ABM (optional / future)
               |
       paired prompt builder
               |
       Ollama local API → Qwen
               |
     structured verdict + evidence IDs
               |
     paired metrics + per-claim JSON
               |
       browser import of results
               |
   ForesightAI research console
```

## Core code

- `dataset.py`: typed claim records; extracts AVeriTeC QA evidence without fetching third-party URLs.
- `scenarios.py`: controlled misleading post generation. Templates are deliberately easy to inspect.
- `prompts.py`: bounded system instructions and three treatment prompts. Gold labels never enter model input.
- `providers.py`: dependency-free local Ollama HTTP adapter, JSON validation, and explicit mock provider.
- `experiment.py`: paired run across conditions, raw results, and metadata.
- `metrics.py`: aggregation; no ungrounded uncertainty estimates.
- `cli.py`: reproducible entry point with configurable sample limit, model, posts, output.
- `web/`: static user interface with accessible tab navigation, SVG graphs, click-to-inspect agent map, and local report file import.

## Trust boundary

The LLM sees untrusted social messages as data. System instructions ask it to rely on supplied evidence; this is tested as a baseline, not assumed foolproof. The code does not execute commands embedded in claims. AVeriTeC URLs are stored as metadata only; the runner does not automatically fetch arbitrary web pages. The Ollama adapter restricts the endpoint to localhost. Avoid logging credentials or personal information.

## Demo vs measurements

The frontend's original graph and score cards are an illustrative deterministic toy model. Its network is not NetLogo and is not fitted to observed data. When you import a report produced by the Python runner, **only the Experiments page** switches its table to report values and discloses whether the provider was mock or real. This separation prevents the rest of the UI from silently claiming empirical results.

## Reproducibility upgrades

Before final paper submission: freeze dependencies and model version, record model hashes and decoding settings, add multiple seeds and trial IDs, run a held-out test set, report per-label macro-F1 and confidence intervals, and audit whether cited passages genuinely entail verdicts. These steps are not completed in v0.1.
