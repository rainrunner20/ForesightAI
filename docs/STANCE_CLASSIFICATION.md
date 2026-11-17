# RumourEval stance-classification experiments

This is a separate, supporting NLP task for the CSC 733 project:
classify whether a reply **supports, denies, questions, or comments on** a
source rumor. This does **not** directly determine the factual truth of the rumor.
The central LLM verification experiment remains in `foresight_ai.cli`.

## Dataset contract

Use an export of the official RumourEval 2019 Task A or an appropriately
documented derived split. This pipeline does not directly parse the original
competition's nested Twitter/Reddit ZIP structures.

Accepted files: CSV, JSON list, JSONL.

| Column | Meaning |
| --- | --- |
| `source_text` | The source rumor, not an unrelated headline |
| `reply_text` | The replying message being classified |
| `label` | 0=support, 1=deny, 2=query, 3=comment; or label strings |
| `id` | Optional message identifier |
| `thread_id` | Optional root conversation/thread identifier |

The fields above match the exposed format of the community
[Hugging Face RumourEval 2019 dataset](https://huggingface.co/datasets/strombergnlp/rumoureval_2019).
For original sources and usage terms, consult
[the SemEval 2019 RumourEval repository](https://github.com/kippfreud/RumourEval).

Keep the dataset's original training/development/test split identities and
license attribution. **Do not commit third-party tweet/reply contents** here.
Put local exports under `data/rumoureval/` (ignored by Git).

### Leakage protection

The loader rejects pairs of splits that share the same normalized source rumor
text or any nonempty matching `thread_id`. Label IDs are validated and all
four stance classes must appear in training. We avoid random per-reply splits,
because replies from one source thread can leak across splits.

## TF-IDF + Logistic Regression (fast baseline)

```powershell
python -m pip install -e ".[stance]"
python -m foresight_ai.stance_cli --backend tfidf `
  --train data/rumoureval/train.csv `
  --dev data/rumoureval/dev.csv `
  --test data/rumoureval/test.csv `
  --output-dir outputs/stance-tfidf --seed 733
```

Inputs concatenate source + `[REPLY]` + reply. The pipeline uses word
uni/bi-gram TF-IDF and a class-balanced Logistic Regression classifier.
It saves a local `tfidf_model.joblib` and `tfidf_report.json`. Only
load joblib/pickle model artifacts you trust.

## BERT encoder fine-tuning (optional and compute-intensive)

```powershell
python -m pip install -e ".[bert]"
python -m foresight_ai.stance_cli --backend bert `
  --train data/rumoureval/train.csv `
  --dev data/rumoureval/dev.csv `
  --test data/rumoureval/test.csv `
  --model-id google-bert/bert-base-uncased `
  --epochs 2 --batch-size 4 --max-length 192 `
  --allow-model-download `
  --output-dir outputs/stance-bert --seed 733
```

The tokenizer handles the source and reply as **a pair of text sequences**,
and a four-way classification head is fine-tuned with labeled examples.
The validation split selects the checkpoint; the test split is for final
held-out evaluation. Training uses Hugging Face Trainer, PyTorch, and
Accelerate; allow checkpoint downloads only after reviewing the source.
A GPU is recommended but not required by the code.

BERT *code* is included, but no model has been trained or benchmarked in this
repository. The optional packages, checkpoint, and real dataset must be
installed/provided on the training machine; the default CI never downloads
BERT weights.

## What is reported

Each run writes held-out and validation metrics:
- Accuracy and macro-F1 across **all four classes**.
- Support/deny/query macro-F1, called `macro_f1_sdq`, so the dominant
  `comment` class cannot obscure performance on the more informative stances.
- Per-class precision, recall, F1, and support counts.
- Confusion matrix with the fixed order support, deny, query, comment.
- Held-out predictions with message IDs (not the underlying copyrighted text).

These metrics are not advertised as an official RumourEval leaderboard score.
Do not repeatedly tune against the test split; use only validation for
hyperparameter selection. Keep versioned splits and exact model/library
versions for real research reports.

## Continuous integration

The regular job checks loader behavior without optional packages. A separate
CI job installs only the lightweight `stance` extra and trains TF-IDF using
*invented unit-test messages*. It does **not** produce publishable accuracy.
