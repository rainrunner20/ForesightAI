# Research plan — reliability under misleading social context

## Problem statement

Large language models are increasingly used to summarize unverified social discussions and emerging news. A strong factual answer should rely on evidence, not on how often a claim is repeated. We will measure whether a model shifts its verdict when deliberately misleading social comments are appended to a fact-checking prompt.

### Hypotheses

- **H1 — repetition:** with identical claim evidence, increasing misleading-comment repetition will increase the rate of incorrect or changed verdicts for at least some cases.
- **H2 — grounding:** explicitly prioritizing evidence over social posts will lower mistaken verdict changes relative to a context-only instruction.
- **H3 — correction:** after misleading context, injecting a short, cited correction will restore correct answers more often than repeating an unsupported assertion. This is a *future extension*.

H1 is a hypothesis, not a promised result; the effect may be zero or contrary to expectations.

## Datasets

**Primary: AVeriTeC.** It provides 4,568 fact-checked claims with labels, question-answer evidence, and supporting explanations from multiple fact-check organizations. We propose an initial 100–200 claim sample, stratified by label and topic as feasible. Preserve a held-out evaluation split and record source dates and case IDs. Its license is CC BY-NC 4.0; download from the official source, preserve attribution, and do not commit third-party contents.

**Optional: RumourEval 2019.** Stance-labeled threads (support/deny/query/comment) can be used to train or evaluate a stance classifier. These are real discussions, not guaranteed to provide the evidence needed for every AVeriTeC claim. Do **not** join unrelated threads with unrelated claims as if they were real histories.

**Controlled stimuli.** Generate misleading posts from each claim and opposing gold label. Make the prompts explicitly synthetic. Vary wording, repetition count, and source framing; log the generator version and review examples for unintended label leakage. Initial implementation repeats templates. A stronger study needs independent/manual review of adversarial stimuli.

## Variables and controls

| Variable | Example settings | Why it matters |
| --- | --- | --- |
| Social repetition | 0, 4, 16, 32 posts | Main independent variable |
| Evidence priority | Normal vs explicit evidence-first prompt | Safeguard ablation |
| Source framing | Anonymous rumor vs claimed authority | Tests evidence laundering |
| Fact-check correction | Absent vs short cited correction | Optional recovery experiment |
| Context length | Token-matched neutral filler | Controls for prompt-size confounding |
| Ordering | Evidence first vs social first, swapped | Checks positional effects |
| Model | One frozen Qwen checkpoint first | Prevents model changes from becoming confounders |

Core matrix: claim × condition × repetition level; compare paired samples. Freeze model and sampling settings. Record prompt version, model tag, decoding parameters, dataset split, and whether source evidence was present. If using sampling >0, repeat with distinct seeds and report variability.

**Important:** The current runner supports seven conditions and adjustable repeated posts. It does not yet implement token-matched filler, randomized order, repeated model trials, or confidence intervals. Those are tracked as follow-on work, not presented as completed.

## Main metrics

1. **Verdict accuracy** compared to AVeriTeC labels. Also use macro-F1 and per-label precision/recall for class imbalance in later evaluations.
2. **Flip rate** relative to a paired evidence-only prediction, reported alongside *harmful flip rate* (correct → incorrect) and *helpful flip rate* (incorrect → correct). The implemented rates use the same denominator: claims with a valid prediction in both the evidence-only baseline and compared condition. Invalid or missing responses are excluded from paired flip rates but included in the separate invalid-output metric. A flip between two incorrect verdicts contributes to overall flip rate, but not harmful or helpful flip rate.
3. **Cited-evidence ID validity**, plus **citation coverage**. A valid ID is not enough: conduct a separate evidence-entailment or human audit for actual support.
4. **Abstention quality** when gold evidence is insufficient.
5. **Calibration**: only if a defensible confidence estimator is added; text that sounds confident is not a probability.
6. **Intervals and significance**: claim-level bootstrap intervals; for paired binary correctness, consider McNemar's test with suitable assumptions.

The output should include the complete per-claim responses, not just aggregate scores, so errors can be inspected.

## Baseline comparisons

- Majority-class and simple rule-based verdict priors (clearly labeled weak baselines).
- TF-IDF + logistic regression for *stance classification* in RumourEval, **not** a direct evidence-verification baseline for AVeriTeC.
- BiLSTM and BERT-like encoder models for stance, if time and computing resources allow.
- One local instruction-following Qwen model for central evidence/repetition experiments, with and without explicit evidence-first prompting.

## Strong optional extensions

- **Consensus illusion / coordinated bots:** NetLogo agents with heterogeneous trust, skepticism, influence, and fact-check behavior. Output post distributions that become the LLM's social context. Measure whether network topology changes the LLM's behavior rather than simply how widely the rumor spreads.
- **Evidence-rescue replay:** evaluate the same model before and after a cited correction, measure the fraction of incorrect verdicts recovered.
- **Citation laundering stress test:** posts *claiming* to cite expert reports (without actual supporting evidence) vs independently retrieved verifiable evidence.
- **Uncertainty and abstention:** examine whether the model can refuse to decide when evidence is genuinely missing; avoid overclaiming confidence calibration.
- **Rumor mutation:** semantically equivalent paraphrases vs emotionally loaded posts, controlling for token length.

## Threats to validity

Social repeats are manufactured, not organic social data. AVeriTeC labels can depend on the exact date and wording of the claim. Repeating a claim creates longer prompts; length and position effects must be controlled. The correct label may leak into stimulus templates if not carefully reviewed. An LLM may generate malformed JSON, and treating it as a missing response can skew results. No single model, small sample, or synthetic network justifies general claims about people or all LLMs.

## Suggested presentation story

Start with a simple claim and its evidence; show the model's evidence-only verdict. Introduce a wall of coordinated posts; test whether the verdict changes. Replay with grounding and inspect actual citations. Compare paired cases across the dataset, show failure cases and counterexamples, and close with the limitations and implications for AI-powered media monitoring.
