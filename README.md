# ForesightAI

**How reliable are language models when a social discussion repeatedly contradicts the evidence?**

ForesightAI is a CSC 733 Natural Language Processing research prototype. We test whether repeated misleading social messages change an LLM's claim-verification verdict, and whether an evidence-first prompt helps it stay grounded. We also built a browser-based research console to explain the experimental design and visualize a fictional social network.

> **Status — prototype, not a fact-checking service.** The web dashboard defaults to fictional examples and deterministic toy scores. It does **not** display measured LLM accuracy until you import a model-generated report. The Python runner can perform actual local inference using Ollama. No trained classifier, live social-media ingestion, or validated NetLogo integration is claimed as complete.

## Why this is interesting

When an organization asks an AI assistant to summarize a fast-moving discussion, social consensus and trustworthy source evidence are not the same thing. A rumor repeated by many accounts can look persuasive even without independent verification. We study that failure mode with paired, reproducible test conditions.

Our core question: **Do repeated misleading comments make an LLM more likely to change a correct verdict, and can evidence prioritization reduce that effect?**

## What works right now

| Component | Status | Notes |
| --- | --- | --- |
| Browser research dashboard | Working demo | Seven interactive views, Twist Lab, replay timeline, evidence inspector, import/export |
| AVeriTeC-style JSON/JSONL loader | Implemented | Converts real claim/evidence records without contacting outside sources |
| Controlled context generation | Implemented | Seven conditions: evidence-only, rumor, grounding, fake authority, mutation, echo chamber, rescue |
| Local Qwen/Ollama adapter | Implemented, not run here | Requires Ollama and a downloaded local model |
| Paired evaluation and report export | Implemented | Accuracy, flip rates, recovery metric, citation-ID checks, malformed outputs and stepwise replay |
| Import results into dashboard | Implemented | Experiments, Decision Replay, and Diffusion Lab consume JSON emitted by Python |
| Unit tests and CI workflow | Implemented | Standard-library Python tests and browser JS syntax validation |
| Echo-chamber simulation | Implemented in Python | Seeded, uncalibrated agent network with per-step frames and generated social posts |
| NetLogo teaching model | Source included, unverified | Optional `.nls` example that must be tested in NetLogo; not an integrated empirical model |
| RumourEval TF-IDF baseline | Code implemented, untrained here | Optional scikit-learn training/evaluation on supplied data |
| BERT stance classifier | Code implemented, untrained here | Optional Hugging Face encoder fine-tuning on supplied data |

## Quickstart: dashboard

The dashboard has **no npm packages** and **no API keys**. From the project root:

```powershell
python -m http.server 5173 --directory web
```

Open `http://localhost:5173`. You can also open `web/index.html` directly in many browsers.

Inside the UI:

1. Change rumor repetition and fact-checker presence.
2. Switch between Overview, Claim Explorer, Diffusion Lab, Evidence Audit, Experiments, Twist Lab, and Decision Replay.
3. Click an agent on the network map, select a twist, or step through a sample decision timeline.
4. Export a **synthetic** JSON configuration. This does not contain measured experiment results.
5. To load actual Python outputs, import a generated JSON report on **Experiments**; Decision Replay and Diffusion Lab will use it too.

## Quickstart: research runner

The Python core uses the standard library, so no installation is needed for the demo.

```powershell
python -m unittest discover -s tests -v
python -m foresight_ai.cli --provider mock --seed 733 --agents 120 --posts 16 --output outputs/demo.json
```

The mock backend only validates the pipeline; its deliberately fixed answers **cannot** be cited as scientific results.

### Token-length audit and neutral control (optional)

The original seven conditions remain the default. A separate `neutral_length_control`
can match the rumor prompt's **system + user text** token length within one token
using an explicitly selected Hugging Face tokenizer. This helps check whether
a result is due to repetition or just the length of the prompt.

```powershell
python -m pip install -e ".[tokenization]"
python -m foresight_ai.cli --provider mock --posts 4 --conditions evidence_only,rumor_pressure,neutral_length_control --tokenizer Qwen/Qwen3-4B --allow-tokenizer-download --output outputs/neutral-demo.json
```

The tokenizer is optional and this example is **still a mock demo**, not
measured AI performance. The count excludes Ollama's chat template and may not
exactly match a quantized local model. See [docs/TOKEN_CONTROLS.md](docs/TOKEN_CONTROLS.md).


### Research uncertainty (new)

Each Python report now includes `paired_inference`: paired accuracy
differences, harmful/helpful flips, claim-level 95% bootstrap intervals,
and exact McNemar p-values. These are exploratory and **not valid real-model
results when using the mock provider**. For methodology and current research
papers, read [docs/RECENT_RESEARCH_2026.md](docs/RECENT_RESEARCH_2026.md).

### Human evidence-support review (new)

A valid citation ID is not proof that the cited evidence actually justifies
the model's factual verdict. Export a source-aware review sheet from an
experiment report and the original claim file:

```powershell
python -m foresight_ai.evidence_audit --report outputs/averitec-qwen.json --claims data/averitec/pilot_train.json --export outputs/evidence_review.csv
```

The exported CSV intentionally omits gold labels and leaves human
`support_label` entries blank. After a reviewer fills the evidence-support
labels, summarize them with:

```powershell
python -m foresight_ai.evidence_audit --report outputs/averitec-qwen.json --review outputs/evidence_review.csv --summary outputs/evidence_audit.json
```

This is **not** an automated source-entailment metric. It is a traceable
manual audit; no real evidence reviews have been performed here.
See [docs/EVIDENCE_AUDIT.md](docs/EVIDENCE_AUDIT.md).

### Local Qwen experiment (optional)

Install [Ollama](https://ollama.com/), then fetch a Qwen model in a terminal:

```powershell
ollama pull qwen3:4b
```

Run the experiment from the project root (Ollama must be running):

```powershell
python -m foresight_ai.cli --provider ollama --model qwen3:4b --input data/demo_claims.json --limit 3 --posts 16 --output outputs/qwen-demo.json
```

These examples use **fictional claims**, even though a real local model generated the verdicts. For research on annotated claims, replace `--input` with your local copy of the AVeriTeC training or development JSON file. The runner accepts the official AVeriTeC `questions[].answers[]` structure.

To see your local results in the browser, open **Experiments → Import results JSON** and select `outputs/qwen-demo.json`. The dashboard's other toy illustrations stay clearly labeled synthetic.

### Stance classification: TF-IDF and BERT (optional)

A separate pipeline accepts RumourEval-style source/reply CSV, JSON or JSONL
splits and trains either a TF-IDF + Logistic Regression baseline or a
fine-tuned BERT encoder. The original dataset is not bundled, and **no real
stance model has yet been trained or evaluated here**.

Run `python -m foresight_ai.stance_cli --help` and see
[docs/STANCE_CLASSIFICATION.md](docs/STANCE_CLASSIFICATION.md) for split
validation, optional installs, local training commands, and score definitions.

### Official AVeriTeC real-data pilot

A reproducible sampling command can download the **official** AVeriTeC
training split (explicit opt-in), produce a 50-case binary-verdict pilot
with 25 Supported + 25 Refuted cases, and save dataset SHA-256 plus
selected case IDs locally. This is **data preparation**, not a completed
LLM run:

```powershell
python -m foresight_ai.prepare_averitec --split train --download --per-label 25 --seed 733
```

The loader now keeps each answer with its original fact-checking **question**,
source URL, and optional Boolean explanation. This prevents ambiguous
standalone answers such as "No" from losing their meaning. Unanswerable
answers are excluded, and the official `Cherrypicking` label variant is
recognized. Synthetic misleading posts still need manual review before
scientific conclusions.

See [docs/REAL_DATA_AND_KAGGLE.md](docs/REAL_DATA_AND_KAGGLE.md)
for benchmark provenance, sample-selection limitations, and our Kaggle
competition assessment.

### Real dataset sources

- **[AVeriTeC](https://fever.ai/dataset/averitec.html):** 4,568 real-world fact-checked claims, with verdict labels and annotated question-answer evidence. Start with a small, stratified subset. Dataset released under CC BY-NC 4.0; check usage terms and provide attribution.
- **[RumourEval 2019](https://github.com/kippfreud/RumourEval):** Twitter/Reddit discussion threads with support/deny/query/comment stance labels and rumor verification annotations. Ideal for a later stance module. Follow the dataset and platform-specific terms.

**We do not bundle the external research datasets in this repository.** The files in `data/` are entirely fabricated examples.

## Research design

Each annotated claim runs through seven conditions by default. The first three form the core paired comparison:

| Condition | Controlled input | Purpose |
| --- | --- | --- |
| A — Evidence only | Claim + cited evidence | Baseline model verdict |
| B — Rumor pressure | Claim + same evidence + repeated misleading comments | Detect evidence-to-social influence |
| C — Evidence first | Same claim/evidence/comments, with evidence explicitly prioritized | Test a grounded prompting safeguard |

Our runner holds each claim and supplied evidence constant but varies social context, framing, and instruction placement. It also provides `fake_authority`, `rumor_mutation`, `echo_chamber`, and `evidence_rescue` conditions. The rescue step explicitly includes the prior verdict in a new independent prompt; it is not a multi-turn chat trace. **A proper report also needs controls for context length, prompt ordering, label balance, random seed, and repeated model trials.** Some controls have now been implemented (an opt-in tokenizer-aware neutral
length comparison), while randomized ordering, repeated model trials,
confidence intervals, and source-support audits remain planned. See
[docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md) and
[docs/TOKEN_CONTROLS.md](docs/TOKEN_CONTROLS.md).

Current computed metrics:

- **Verdict accuracy** against dataset labels.
- **Answer flip rate**, **harmful flip rate**, and **helpful flip rate** relative to valid evidence-only decisions.
- **Citation ID validity** (whether an output references supplied evidence IDs); this is *not* proof that a citation supports the conclusion.
- **Malformed answer rate**, so parse failures are visible rather than silently discarded.
- **Evidence-rescue rate** conditional on the previous rumor-pressure verdict being wrong.
- **Simulation reach** from a seeded synthetic agent model; this is not an empirical human-behavior measure.

Claim-paired percentile bootstrap 95% intervals and exact McNemar exploratory comparisons are implemented; real research intervals have **not** been computed because no real-model results were run here. We still need human source-support verification, repeated-model trials, and defensible uncertainty calibration. **See [docs/TWISTS.md](docs/TWISTS.md)** for experimental extensions, hypotheses, and confounds, and [simulations/README.md](simulations/README.md) for the optional NetLogo source.

## Publish the interactive dashboard

The repo contains a manual GitHub Pages workflow for the static `web/` console. See [docs/DEPLOY.md](docs/DEPLOY.md). The repository owner must select **GitHub Actions** under Settings → Pages and manually dispatch the workflow once; no live site is claimed until deployment succeeds.

## Project map

```text
foresight-ai/
├── .github/workflows/ci.yml       # Tests on pull requests
├── .github/workflows/deploy-pages.yml # Optional manual Pages deployment
├── data/demo_claims.json          # Fictional test fixture only
├── docs/                          # Research plan and five extensions
├── foresight_ai/                  # Python experiment engine
│   ├── cli.py                     # Command-line entry point
│   ├── dataset.py                 # Claim and evidence loading
│   ├── experiment.py              # Paired experiment runner
│   ├── metrics.py                 # Aggregation and evaluation
│   ├── prompts.py                 # Evidence and social prompt design
│   ├── providers.py               # Mock and local Ollama adapters
│   ├── stance_data.py               # Validated stance data splits
│   ├── stance_models.py             # TF-IDF and classifier metrics
│   ├── stance_bert.py               # Optional BERT fine-tuning
│   ├── stance_cli.py                # Stance training entry point
│   ├── token_controls.py            # Optional prompt token auditing
│   ├── scenarios.py               # Controlled misleading-post generation
│   └── diffusion.py               # Seeded synthetic social network
├── simulations/                   # Optional NetLogo teaching model (.nls)
├── tests/                         # Standard-library regression tests
├── web/                           # Browser-native interactive dashboard
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── CONTRIBUTING.md
├── SECURITY.md
└── pyproject.toml
```

## Team Git workflow

We keep `main` stable and work through feature branches. Every PR should explain **what changed, why, how it was tested, and any limitations**. Use small meaningful commits that reflect real work; we do not fabricate commit histories or claim tests were run when they were not. See [CONTRIBUTING.md](CONTRIBUTING.md).

A clean local workflow in VS Code PowerShell:

```powershell
git switch main
git pull --ff-only
git switch -c feature/stance-baseline
# Develop and actually test a small change.
git add foresight_ai tests
git commit -m "feat(nlp): add baseline stance classifier"
git push -u origin feature/stance-baseline
```

Open a PR on GitHub and request teammate review. Prefer squash merge if the branch has noisy fixup commits; do **not** delete feature branches after merging if the team wants them retained.

## Course alignment

The central experiment uses classification, text representation, evidence retrieval/attribution, language modeling, transformer-based LLM inference, prompt design, and precision/recall/F1 evaluation. The repository now includes untrained TF-IDF + logistic regression and BERT
fine-tuning pipelines for stance classification. A BiLSTM remains a possible
future comparison. These stance models do not replace the evidence-based
claim-verification experiment. A tested Python agent model feeds controlled synthetic social contexts into the NLP experiment. A separate NetLogo source example illustrates comparable mechanisms, but has not yet been executed or integrated. The ABM does not replace the NLP research question.

## Limitations and integrity

The dashboard demo is deterministic. Its numerical "reliability" curves are **not** outcomes from Qwen, GPT, or any other LLM. The mock backend uses a fixed verdict for plumbing checks, so its apparent accuracy is meaningless. Real-world claims can be ambiguous or change over time; evidence provenance and dates must be assessed before making judgments. We do not claim this tool predicts future events or determines objective truth from social-media popularity.

*Developed as an educational research project for CSC 733. See `docs/RESEARCH_PLAN.md` for planned hypotheses and evaluation controls.*
