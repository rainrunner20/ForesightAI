# Human evidence-support audit

Our model currently reports whether a citation ID points to supplied evidence.
That is necessary but **not sufficient** to prove the citation supports the
model's answer. Recent ACL/EMNLP research calls out this exact problem.

This feature adds a **manual, source-aware evaluation step** rather than
using another LLM to grade the first LLM without calibration.

## Step 1: Export the evidence-review sheet

After completing a real Ollama experiment using locally downloaded AVeriTeC
claims:

```powershell
python -m foresight_ai.evidence_audit `
  --report outputs/averitec-qwen.json `
  --claims data/averitec/pilot_train.json `
  --export outputs/evidence_review.csv
```

The CSV contains **one row per claim/condition** and includes:

- Claim text, model verdict, model reasoning, and the IDs it cited.
- Original question-answer evidence and source URLs from the supplied claims.
- Whether any model citation IDs do not exist in the supplied evidence.
- Blank `reviewer`, `support_label`, and `review_notes` fields.
- A report SHA-256 and per-row key so later scoring cannot accidentally
  join an annotation to a different model run.

**The correct gold verdict is intentionally absent.** This helps reviewers
focus on whether evidence actually justifies *the model's stated verdict*,
rather than reverse-engineering an explanation from the benchmark label.

Opening CSV in spreadsheet software is supported; cells beginning with
potential formula operators are prefixed with a literal apostrophe.

## Step 2: Fill the review columns manually

For each entry, inspect the cited evidence and any other supplied sources,
taking account of dates, ambiguity, and conflicts. The allowed labels are:

| `support_label` | Meaning |
| --- | --- |
| `supports` | The cited evidence, considered in its supplied context, justifies the model's verdict |
| `contradicts` | Evidence contradicts the model's verdict |
| `insufficient` | Available evidence cannot justify the model's verdict |
| `mixed` | Credible supplied sources conflict or the model leaves important disagreement unexplained |
| `not_applicable` | No meaningful model verdict to assess, such as malformed output |
| blank | Not reviewed yet |

Do not fill labels automatically from benchmark gold labels. These are two
different measurements: **verdict correctness** versus **citation support**.

For an initial study, two teammates can review separate copies of the same
export without seeing each other's labels, then adjudicate disagreements
and report reviewer agreement. Interrater agreement calculation is **not yet
implemented**; do not claim it has been measured.

## Step 3: Summarize reviewer labels

```powershell
python -m foresight_ai.evidence_audit `
  --report outputs/averitec-qwen.json `
  --review outputs/evidence_review.csv `
  --summary outputs/evidence_audit.json
```

The report groups labels by experimental condition, counts reviewed and
unreviewed cases separately, and calculates
`supported_fraction_of_assessed` only for reviewed, assessable verdicts.
Missing annotations never silently count as evidence failures.

### Limitations

- This is **human judgment**, not an objective entailment model or verified
  source-authenticity service. The reviewer should separately verify links
  or archived evidence when relevant.
- Source dates and changes to real-world claims require careful checking.
- An answer may have a correct gold label but cite irrelevant evidence,
  or cite support for one side while omitting credible disagreements.
- A single annotator's labels are not interrater reliability. For final
  reporting, blind independent review and adjudication are desirable.
- All review material is written to `outputs/`, ignored by Git. Do not
  commit third-party research text, reviewer identities, or private sources.
- Mock-provider audit exports remain fictional examples, not experiment
  outcomes.

## Research references

- *The Citation-Faithfulness Illusion* (GroundLM 2026):
  https://aclanthology.org/2026.groundlm-1.17/
- *ReCite* (EMNLP 2026):
  https://aclanthology.org/2026.findings-emnlp.1477/
- *Who is the Agent to Blame?* (EMNLP 2026):
  https://aclanthology.org/2026.emnlp-main.1681/
- Industry guidance on human-calibrated groundedness:
  https://www.anthropic.com/research/demystifying-evals-for-ai-agents
