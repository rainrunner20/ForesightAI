# ForesightAI experiments: five extensions

The research question is **whether an LLM's verification verdict changes when a social discussion contradicts the supplied evidence**. We do not claim that popularity predicts truth.

## Conditions

| Name | Implementation | What changes? | Primary observation |
| --- | --- | --- | --- |
| `evidence_only` | Python runner | Claim and evidence only | Reference accuracy |
| `rumor_pressure` | Python runner | Synthetic repeated opposing messages | Accuracy and flip rate |
| `evidence_first` | Python runner | Same evidence and posts, reordered and labeled | Does ordering affect robustness? |
| `fake_authority` | Python runner | Unverified, unnamed authority claims | Accuracy and flip rate |
| `rumor_mutation` | Python runner | Different stylistic framings of the same misleading allegation | Accuracy and flip rate |
| `echo_chamber` | Python + optional NetLogo prototype | Network-generated messages from seeded agents | Exposure, accuracy and flip rate |
| `evidence_rescue` | Python runner | Previous rumor verdict explicitly shown, original evidence reprioritized | Correction rate after initial error |
| AI Decision Replay | Dashboard + JSON report | Step through condition outputs | Verdict/citation changes (not internal reasoning) |

The last row is an interface, not an eighth experimental condition. These are **controlled synthetic interventions**, never harvested quotations from actual people.

## Real-world use cases

**News and public information:** An assistant summarizing emerging events must not treat duplicated posts as independent verification.

**Customer support and brand monitoring:** Repeated rumors about a service outage or recall might mislead an AI summary if evidence provenance is ignored.

**Financial-risk monitoring:** A model should be resilient to unverified rumors about a company. We are not predicting stock returns or giving investment recommendations.

**Trust and safety evaluation:** The benchmark can compare an evidence-grounded prompting strategy with context-heavy alternatives.

## Research design — what the results can and cannot establish

1. Select a documented annotated claim subset; preserve dataset licenses and URLs.
2. Hold each claim and underlying supplied evidence constant across conditions.
3. Use the same model/version, decoding settings, inference hardware, and evaluation script.
4. Record the seed, order, prompt length, fact-checker ratio, post count, and raw model output.
5. Report per-condition accuracy, flip rate, citation coverage, invalid outputs, and recovery rate.
6. Do at least three seeds and analyze paired differences, class imbalance, and uncertainty intervals before drawing conclusions.
7. Perform **manual evidence support audits** on a pre-defined sample: a valid evidence ID alone does not mean the claim was properly supported.

### Important confounds

- System instructions already warn the model that social posts are unverified, so `evidence_first` studies an **ordering/instruction-strength intervention**, not a contrast with a fully naive model.
- `echo_chamber` may generate fewer than the requested posts when the synthetic network doesn't spread. Log realized post counts, and use matched-length controls before attributing changes to topology alone.
- `evidence_rescue` is an **independent reassessment prompt with the prior verdict supplied**, not a real multi-turn conversation or access to hidden model reasoning.
- The source URLs and labels in AVeriTeC are external and may change. Data quality and evidence date matter.
- The built-in mock model gives deliberately fixed answers. Never cite mock scores in the paper.
- NetLogo and the Python simulator are not empirically validated models of online behavior.

## What makes this an NLP project

The claim verification task is natural-language classification with transformer inference. The input is text with source evidence and generated discourse. Outputs are structured text and citation IDs. We compare prompt sensitivity and evaluate answer flips, accuracy, and evidence use. Future baselines include TF-IDF + logistic regression and encoder-only stance classification using RumourEval; those are **not trained in this starter**.

## Running one complete example

```powershell
python -m unittest discover -s tests -v
python -m foresight_ai.cli --provider mock --seed 733 --posts 16 --output outputs/demo.json
python -m http.server 5173 --directory web
```

In the UI, select **Experiments → Import results JSON** and choose the generated file. For real LLM outputs, install and run Ollama, pull a suitable model, then use `--provider ollama`. We do not download licensed datasets or large models automatically.
