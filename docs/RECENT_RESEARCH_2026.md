# Research landscape and industry relevance (reviewed November 2026)

ForesightAI's main question is whether repeated misleading social posts
can alter a model's factual judgment even when annotated source evidence is
supplied. The papers below are **related work**, not results from our repo.

## Closest 2025–2026 studies

| Paper / source | What matters | Concrete ForesightAI connection |
| --- | --- | --- |
| *Diagnosing judgment flip risk of LLMs in fact verification under conflicting evidence*, ETRI Journal, Oct 2026 | Models may change their original judgments when evidence ratios or ordering change; overall accuracy alone misses these failures. | Keep claim-paired harmful/helpful flip rates; add ordering and evidence-composition ablations later. |
| *The Citation-Faithfulness Illusion*, ACL GroundLM, Oct 2026 | Valid citations can hide omitted credible disagreement. | Review semantic support and contradiction separately from citation-ID validity. |
| *Who is the Agent to Blame?*, EMNLP, Oct 2026 | Citation errors can arise at different steps of a multi-agent research pipeline. | Log provenance from evidence collection, prompts, predictions, and human review. |
| *ReCite*, EMNLP Findings, Oct 2026 | A real or relevant-looking citation may fail to support the specific claim. | Add an evidence-support rubric and inspect false attribution rather than counting URLs. |
| *CONSENSAGENT*, ACL Findings, 2025 | Agreement pressure among multiple LLM agents can reduce critical debate. | Compare repeated/copied comments against genuinely varied wording; **do not** equate our simulated humans with LLM agents. |
| *Hallucination to Truth*, Artificial Intelligence Review, Jan 2026 | Factuality claims require validated external evidence and careful evaluation. | Use AVeriTeC QA evidence and account for ambiguous or insufficient cases. |
| *Vera-Life-Eval*, GroundLM 2026 | Even a supporting citation may be stale or superseded at the question's target time. | Optional date/provenance tags; avoid using a dated claim with today's truth label uncritically. |
| *Advancing rumor detection in social media*, Array, Jul 2026 | Review compares text, propagation, GNN, and LLM approaches; warns about methodology and generalizability. | BERT/BiLSTM/TF-IDF remain the stance comparison, with NetLogo/Python propagation as supporting simulation. |

### Reference links

- Conflicting-evidence flip risk: https://doi.org/10.4218/etrij.2026-0242
- Citation-faithfulness illusion: https://aclanthology.org/2026.groundlm-1.17/
- Agentic citation error localization: https://aclanthology.org/2026.emnlp-main.1681/
- ReCite: https://aclanthology.org/2026.findings-emnlp.1477/
- CONSENSAGENT: https://aclanthology.org/2025.findings-acl.1141/
- 2026 factuality systematic review: https://doi.org/10.1007/s10462-025-11454-w
- GroundLM 2026 proceedings (Vera-Life-Eval): https://aclanthology.org/volumes/2026.groundlm-1/
- 2026 rumor detection systematic review: https://doi.org/10.1016/j.array.2026.100842

## Industry guidance

OpenAI's evaluation best-practices guide and Anthropic's agent-evaluation
guidance both emphasize task-specific evaluation, transparent failure cases,
logging, human reference checks, and multiple graders when quality is
subjective. Neither source establishes that a metric alone proves truth.

- https://developers.openai.com/api/docs/guides/evaluation-best-practices
- https://www.anthropic.com/research/demystifying-evals-for-ai-agents
- https://openai.com/index/trustworthy-third-party-evaluations-foundations/

### Engineering changes to prioritize

1. **Completed / present:** claim-paired harmful/helpful flips, opt-in
   token-length control, source-aware evidence input, seed-controlled
   AVeriTeC pilot and separate stance classifiers.
2. **Implement now:** paired bootstrap confidence intervals and exact
   McNemar comparisons. Do not mistake them for repeated stochastic-model
   trials or adjust uncorrected p values into certainty.
3. **Next:** human-reviewed evidence-support labels with reviewer notes,
   reproducible provenance, and disagreements preserved in the audit.
4. **Experiment next:** vary social post repetition, apparent consensus
   versus duplicate wording, and evidence/social order while controlling
   total text length and holding the target claim fixed.
5. **Optional:** temporal stale-source challenges, carefully labeled
   synthetic personas, BERT-versus-BiLSTM stance evaluation on genuine
   RumourEval splits, and a second frozen LLM.

### Why not train a Graph Neural Network, build full RAG or add Kaggle now?

Those are defensible *future* additions, but each changes the central
question and requires new data, significant compute, or a separate
evaluation. Our strongest CSC 733 deliverable is still a clean experiment
demonstrating **whether** and **why** a model's evidence-based verdict
changes after misinformation pressure.

## Statistical caveats for our paired metrics

`paired_inference` reports claim-level percentile bootstrap 95% intervals
over valid baseline-versus-condition pairs, with deterministic resampling.
It also reports an exact two-sided McNemar p-value for discordant binary
*correctness* (not for arbitrary multiclass label changes).

- Resample whole claim pairs, not individual responses.
- Invalid or missing model predictions are excluded from the paired
  estimates and must be separately reported with invalid-output rates.
- Intervals are omitted for fewer than two valid matched claims.
- These intervals describe **between-claim uncertainty conditional on
  fixed prompts/settings**. They do not capture run-to-run variance.
- Seven conditions yield multiple comparisons; p-values in this prototype
  are **uncorrected and exploratory**. Pre-register a small primary
  comparison before interpreting significance.
- Never quote mock-provider intervals as real model results.
