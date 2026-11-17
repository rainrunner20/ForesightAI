# Real AVeriTeC pilot and Kaggle review

## 1. Real claim-verification benchmark (primary)

The project uses the official [AVeriTeC dataset](https://fever.ai/dataset/averitec.html)
from the authors' [GitHub repository](https://github.com/MichSchli/AVeriTeC).
It has annotated question-answer evidence, claim verdicts, and source URLs.
The dataset is published under **CC BY-NC 4.0**; keep the attribution and
avoid posting source claims and evidence to our public project repo.

Our official-source downloader only supports the `train` and `dev` JSON
files. Run it from the root of the cloned repository:

```powershell
# Downloads official data only when --download is explicitly supplied.
python -m foresight_ai.prepare_averitec --split train --download `
  --per-label 25 --seed 733

# Reuse a cached download, no network call:
python -m foresight_ai.prepare_averitec --split train `
  --per-label 25 --seed 733

# Smoke-test the pilot with mock outputs (NOT real accuracy).
python -m foresight_ai.cli --provider mock `
  --input data/averitec/pilot_train.json --limit 3 --posts 4 `
  --output outputs/averitec-smoke.json
```

The selected records stay under `data/averitec/` and their provenance manifest
under `outputs/`; both directories are ignored by Git. No external data
is included in the repository. The source SHA-256 and selected record IDs
are logged for reproducibility.

### Why a binary pilot?

Our attack generator can create an **opposing** claim for a Supported or
Refuted case, but there's no single logically opposite truth value for
`Not Enough Evidence` or `Conflicting Evidence/Cherrypicking`.
The pilot therefore chooses an equal number of **Supported and Refuted**
claims that have at least one answerable question-answer pair.

This is deliberate selection for a controlled experiment, not a claim that
the full dataset has only two labels. Four-way claim verification remains
a different, more ambitious evaluation.

The pilot does **not** prove the selected source evidence is good enough
to support the verdict; manually audit the claim context, source dates,
and question-answer evidence before drawing conclusions.

### Source evidence bug fixed

Each answer is now stored *with its question*, source URL, and (where
provided) Boolean explanation. Example:

```text
Question: Was service restored?
Answer: No
Explanation: The closure is temporary.
```

The previous version extracted a bare `No`, which removed crucial
meaning. Unanswerable entries are skipped rather than being treated as
evidence. At most eight QA entries are still passed to the LLM. That
truncation must be checked against the original annotations before final
evaluation. The official nonhyphenated `Cherrypicking` label is normalized.

### Preparing the untouched development split

Prepare a separate dev sample only **after** choosing your research
procedure based on train data:

```powershell
python -m foresight_ai.prepare_averitec --split dev --download `
  --per-label 25 --seed 733
```

Do not tune prompts using the development evaluation claims. The script
keeps `train` and `dev` identities distinct via stable IDs such as
`averitec-dev-00042`.

## 2. Kaggle research: what is worth using?

### Most relevant optional idea: SciHal

[Hallucination Detection for Scientific Content (2025)](
https://www.kaggle.com/competitions/hallucination-detection-scientific-content-2025)
tests whether individual assertions in LLM-generated scientific summaries
are **entailed, contradicted, or unverifiable** with respect to reference
abstracts. It also offers finer-grained error categories.

**Useful application:** Design a *secondary evidence-entailment audit*
for the ForesightAI dashboard. This task is not a direct replacement for
AVeriTeC or RumourEval, and competition material can be gated by rules.
The competition's 2025 closing date has passed; we have not downloaded
or trained on its content.

### Useful inspiration, not central data

- [FEVER prompt-learning competition](https://www.kaggle.com/competitions/assignment-3-prompt-learning-framework/data):
  the underlying claim/evidence classification problem relates to our work,
  but that specific competition's data may require agreeing to rules. Our
  main benchmark remains directly sourced AVeriTeC.
- [TruthLens fake news detection](https://www.kaggle.com/competitions/fake-news-detection-projectx/overview):
  binary article-text labeling. This does not measure resistance to
  repeated social misstatements when reliable evidence is already supplied.
- [2024 AVeriTeC shared task](https://fever.ai/2024/task.html) and
  [2025 FEVER 8](https://fever.ai/2025/task.html): more directly aligned
  with evidence-based verification than general fake-news competitions.

No Kaggle competition entries, account access, submissions, or leaderboard
scores are claimed. Dataset/competition rules take precedence over public
copies or derivative uploads.

## 3. Research prerequisites still outstanding

- Download, inspect, and manually audit the real dataset on an execution machine.
- Verify the opposing generated synthetic posts do not leak labels or
  accidentally change the interpretation of a claim.
- Run real frozen-LLM paired experiments; mock results are not research.
- Add claim-level uncertainty intervals and an evidence-support audit.
- Train the stance classifiers on real RumourEval splits, separately.
