# ForesightAI — Research Companion

CSC 733 | Research design and visual explanation

The detailed academic notes from Research Lab V2, with saved paper figures and illustrative diagrams. Published figures and example outputs are not measurements from ForesightAI.

[Interactive lab](https://colab.research.google.com/github/rainrunner20/ForesightAI/blob/feature/colab-narrative-pilot/notebooks/ForesightAI_Research_Lab_V2.ipynb)

## Overview

The following fictional outage illustrates the controlled experiment. Qwen is evaluated with fixed weights under varying social context and evidence availability.

**The entire workflow**

| Stage | Input / action | Output |
|---|---|---|
| 1. Create a situation | Fictional website outage | Known observation |
| 2. Generate a crowd | 18 hacker opinions, 2 overload opinions | Controlled social context |
| 3. Ask Qwen | Facts + comments + question | Actual model answer |
| 4. Repeat | Change the crowd, keep facts fixed | Comparable answers |
| 5. Add proof | Reveal the cause in a later turn | Revised model answer |
| 6. Evaluate | Compare responses to scenario key | CSVs, graphs and research findings |

```text
  INCIDENT + COMMENTS
           |
           v
       QWEN (AI)
           |
           v
    ANSWER / REASON
           |
      ADD NEW PROOF
           |
           v
    UPDATED ANSWER
           |
           v
      SCORE + GRAPH
```

**What we build:** the test, the prompt generator, the scoring system and the dashboard. Qwen is the AI taking the test. The example answers below are illustrative, not real measured outputs.

**Steps 1–4 | Before we know the cause**

**1 — Create the situation**

> MetroCart's checkout failures increased by 30% at 2 PM.

We do not know why. Hackers, server overload or a software deployment error could be possible.

**2 — Generate social comments**

| 18 cyberattack comments | 2 overload comments |
|---|---|
| Anonymous user: I suspect cyberattack. | Anonymous user: I suspect server overload. |

The actual generator writes 20 separate comment lines. The comments are opinions, not additional evidence.

**3 — Send the prompt to Qwen**

> Which cause is established? A = cyberattack; B = server overload; C = insufficient evidence. Start with Choice: A, B, or C, then give a short reason.

| Expected answer | Possible failure (made up) |
|---|---|
| C — Insufficient evidence. | A — Cyberattack. |
| The comments do not establish a cause. | Most people suspect hackers. |

**4 — Change the crowd and repeat**

The number of comments favoring each explanation changes; the known facts do not.

| Pro-hacker share | Cyberattack comments | Overload comments | Expected |
|---|---:|---:|---|
| No comments | 0 | 0 | C |
| 10% | 2 | 18 | C |
| 30% | 6 | 14 | C |
| 50% | 10 | 10 | C |
| 70% | 14 | 6 | C |
| 90% | 18 | 2 | C |

The expected answer never changes just because the crowd changes. We measure whether Qwen's actual answers change. We also swap the displayed A/B labels and test source framing, repetition and other supporting factors.

**Steps 5–6 | New evidence and research results**

**5 — Give Qwen new evidence across a conversation**

| Turn | New information | Expected | Example failure/recovery path |
|---|---|---|---|
| 1 | Outage + crowd opinions | C | C |
| 2 | Unusual network traffic; origin unknown | C | A |
| 3 | Investigation continues | C | A |
| 4 | Authenticated analysis establishes overload and rules out attack | B | B |

The example path C → A → A → B shows premature commitment followed by correction. A path ending in A would fail to revise. We test both possible proof endings and matched crowd/no-crowd conversations. The main lure-timing experiment separately omits the crowd.

**6 — Save the actual answers and calculate results**

| Research question | What the model does | What we measure |
|---|---|---|
| Hypothesis generation | Lists plausible causes | Alternative coverage, evidence requests (human review) |
| Hypothesis evaluation | Selects A, B or C | Unsupported commitments before proof |
| Hypothesis revision | Updates after new evidence | Holding, final accuracy and correction |

The notebook records exact prompts, raw model replies, token counts and verdicts in CSV files. Actual charts only appear after inference. Our default pilot plans 464 calls across two fictional incidents, not 464 independent cases.

The approach is relevant to AI assistants that summarize reviews, incident reports and emerging news when reliable evidence is incomplete. Generalization to real discussions requires separate evaluation.

**Experimental inputs and outputs**

**1. Synthetic incident records**

The dataset is five fictional incidents, defined in Python and exported to `foresight_v2_cases.csv`. The default pilot uses MetroCart and flight delays.

| Incident | A | B |
|---|---|---|
| MetroCart outage | Cyberattack | Server overload |
| Flight delays | Aircraft maintenance | Severe weather |
| Product complaints | Hardware defect | Incorrect setup |
| Internet outage | Damaged cable | Routing configuration error |
| Stock decline | Company scandal | Broad market selloff |

An actual record from our dataset:

| Field | MetroCart scenario |
|---|---|
| Record ID | metro |
| Incident | MetroCart outage |
| Observation | Checkout failures increased by 30% at 2 PM. |
| Hypothesis A | cyberattack |
| Hypothesis B | server overload |
| Alternative hypothesis | software deployment error |
| Ambiguous clue | Unusually high network traffic was observed; its origin is unknown. |
| Neutral update | More customers reported checkout failures. |
| Evidence for A | Authenticated incident analysis establishes a cyberattack as the cause and rules out ordinary overload. |
| Evidence for B | Authenticated incident analysis establishes ordinary server overload as the cause and rules out a cyberattack. |

Python generates the 20 individual comment lines from this record. It builds a prompt; Qwen produces the response. No live social-media data is collected in this pilot.

**2. Model response and scoring**

| Input to Qwen (abbreviated) | Illustrative response (not measured) |
|---|---|
| Fact: checkout failures increased 30%. | Choice: A |
| 18 opinions suspect cyberattack; 2 suspect overload. | Reason: Most users suspect a cyberattack. |
| Which cause is established? A, B or C? | |

⬇ **Python parses the answer and compares it with the scenario key.**

| Expected | Parsed choice | Evaluation |
|---|---|---|
| C — Insufficient evidence | A — Cyberattack | Unsupported commitment |

The full prompt and raw answer are saved, not just the letter. The model does not grade itself. A/B labels are normalized when swapped.

**Recorded outputs**

Each model call records the incident, test condition, expected answer, parsed choice, exact prompt, raw response, token count, seed, checkpoint and answer-label order. The default pilot uses two incidents and both label orders for choice tasks.

| Output file | Contents |
|---|---|
| `foresight_v2_cases.csv` | Synthetic incidents |
| `foresight_v2_single.csv` | Single-turn prompts and responses |
| `foresight_v2_turns.csv` | Conversation history and responses |
| `foresight_v2_generation.csv` | Open-ended responses |
| `foresight_v2_human_review.csv` | Human annotation template |
| `foresight_v2_crowd_revision.csv` | Matched crowd/revision comparison |
| `foresight_v2_verdict_audit.csv` | Verdict/reason consistency audit |
| `foresight_v2_run_metadata.json` | Checkpoint and run configuration |

Appendix D computes charts from the recorded responses. No illustrative values are used as experimental measurements.

**Interactive interface — conceptual preview**

The following is a **conceptual interface**, not a model-generated response or deployed inference service. The implemented Colab demo in Appendix B uses the same scenario, adjustable crowd ratio, source and proof, with actual Qwen inference when enabled.

![Frontend concept — saved preview (no model needed)](figures/v2-08.svg)

**Controlled factors and observable measurements**

The point of the project is not just to display a verdict. It is to investigate why an answer might change when social information changes.

```text
 RAW COMMENTS + OBSERVATIONS
             |
             v
  INPUT CHARACTERISTICS
  ratio | count | source label | length
  evidence placement | arrival time
             |
             v
  CONTROLLED COMPARISONS
  Same case / checkpoint / matched conditions
             |
             v
  QWEN: tokenize -> Transformer -> generate
             |
             v
  RESPONSE ANALYSIS
  parsed choice | raw reason | alternatives
  first commitment | revision after proof
             |
             v
  GROUP BY FACTOR -> COUNTS / RATES / GRAPHS
             |
             v
  Inspect actual prompts and answers
```

**Factor analysis panel**

| Research factor | What the input looks like | What we measure / visualize |
|---|---|---|
| Popularity | 2/20 vs 18/20 suspect hackers | A/B/C/invalid response curve; does the answer favor the supplied majority? |
| Repetition | 8/10 vs 40/50 favor A (both 80%) | Unsupported commitment vs number of comments; token counts |
| Authority | Same opinion attributed to an anonymous user vs self-described expert | Source × popularity heatmap; unsupported commitment |
| Information length | Short opinion vs same opinion with a disclaimer | Unsupported commitment and input tokens |
| Vote-count format | Individual comments vs a compact vote count | Response distribution across ratios; format comparison |
| Evidence position | Identical facts + proof at start, middle or end | Correct verdict rate by position |
| Prompt strategy | Baseline vs evidence-first instructions | Expected-answer rate before and after proof |
| Lure timing | Same ambiguous clue arrives on turn 2 vs turn 3 | First commitment, turn-by-turn paths, holding and correction |
| Crowd + revision | No crowd vs 90% pro-A at turn 1; matched clues and proof | Holding, premature commitment, final accuracy and conditional correction |
| Hypothesis coverage | No crowd vs 10/50/90% pro-A | Human-reviewed alternatives and evidence requests |

**Example: follow one popularity comparison**

| Fixed | Changed |
|---|---|
| Same MetroCart observation, same number of comments, same source label, same question, same checkpoint | 10% A: 2 hacker / 18 overload opinions → 90% A: 18 hacker / 2 overload opinions |

| Test | Possible output (illustrative) | Parsed result |
|---|---|---|
| 10% A | Choice: C. The cause is unresolved. | Held |
| 90% A | Choice: A. Most people suspect a cyberattack. | Unsupported commitment |

We would inspect the actual answer and its reason, count A/B/C/invalid outcomes for each condition, and compare rates. An observed difference is evidence of sensitivity in our controlled setup; it does not prove which internal model mechanism caused it.

**How the data is analyzed:** the synthetic generator already knows each comment's intended stance and source label; it does not use an NLP classifier to discover them. The tokenizer measures actual input tokens after Qwen is loaded. Qwen generates text. Python parses the verdict and normalizes swapped labels. Human reviewers score open-ended alternatives and inspect whether the explanations support the verdict. No attention weights, truth probabilities or causal attribution scores are invented.

**Where to see it:** Appendix D → **Factor analysis explorer**. Pick a research factor, inspect two exact generated prompt examples, then view measured distributions, sample sizes and raw records after the batch runs.

**Observable prompt and response trace**

The interactive notebook makes the evidence and experimental workflow visible during inference. We can inspect the actual prompt, tokens, generated text and decision changes. We cannot observe a faithful private thought process just by reading a model's stated reason. The processing diagram is conceptual; the quoted messages and measured outputs are observable.

| Panel | Example quote / visual | What it means |
|---|---|---|
| Observation | “Checkout failures increased by 30% at 2 PM.” | The fixed fact |
| Social context | “Anonymous user: I suspect cyberattack.” | Actual repeated comment; not evidence establishing a cause |
| Lure | “Unusually high network traffic was observed; its origin is unknown.” | Suggestive clue, not decisive proof |
| Instruction | “Which cause is established?” | The question actually asked |
| Token inspector | Token IDs and decoded pieces | Actual tokenizer output, not invented embeddings |
| Decisive evidence | “Authenticated incident analysis establishes ordinary server overload as the cause and rules out a cyberattack.” | The fictional scenario's evidence key |
| Generated answer | Choice + reason, displayed as text arrives | Actual Qwen output; not access to private reasoning |
| Evaluation | Expected versus parsed answer | Python's check, not Qwen grading itself |
| Comparison | Raw records, timings, tokens and decision replay | Auditable behavior across conditions |

**Four frontend panels:** Social Information → NLP Processing → Factor Comparison → Decision Replay. All applicable observed features appear together, but attribution comes from separate controlled comparisons. A changed verdict is not a measured internal attention weight or proof of causation.

**Live demo:** Appendix B → Live prompt and response trace. Preview exact paired prompts, run the same Qwen checkpoint on both, watch generated text chunks, inspect real token IDs, and compare decisions. The four-turn replay retains earlier assistant messages. A generation task shows plausible alternatives and evidence requests without automatically grading their quality. No GPU is needed for the text-only preview.

**Study design and controls**

The study uses a fixed pretrained model and synthetic incidents with two candidate causes (A and B). Before decisive evidence, C (insufficient evidence) is the expected evaluation answer. After proof, the established cause is expected.

| Task | Experimental manipulation | Primary outcome |
|---|---|---|
| Hypothesis evaluation | Social support ratio, source framing and controlled variations in context | Unsupported commitment and response distribution |
| Hypothesis generation | No comments versus different narrative ratios | Human-reviewed coverage of plausible alternatives and evidence requests |
| Evidence revision | Early/late/no ambiguous clue, both proof endings, matched crowd/no-crowd conditions | Holding, first commitment, final accuracy and conditional correction |

The default pilot specifies 184 single-turn calls, 272 conversation-related calls and 8 open-ended calls (464 model calls across two fictional incidents). Calls are not independent incidents. Both displayed answer orders are used for choice tasks; choices are normalized to the canonical cause before analysis. Full-study mode adds cases and comment-order seeds.

Supporting comparisons examine repetition, comment length, vote-count format, evidence-block position and evidence-first instructions. Additional exploratory factors are disabled by default.

**Reproduction:** Run Appendix A with `RUN_QWEN=True`, `RUN_BATCH=True` and `FULL_STUDY=False` for the default pilot; then run Appendices C and D. For interactive inference only, leave `RUN_BATCH=False` and use Appendix B. The default 0.5B checkpoint is a lightweight pilot model. Record the checkpoint, revision and environment; do not pool runs from different models without identifying them.

The pilot is descriptive. Actual responses and human annotations are required before empirical conclusions can be drawn.

## 1. Related research

The original paper figures are saved as inline image outputs in the reading material. No GPU, model or code execution required. Original PDF links are included for context; figures belong to the paper authors.

---

**Figure sources and interpretation**

The labeled sentence cards underneath each original paper show what **we actually supply as inputs** and what a possible response would look like.

These are fictional dataset examples, not real Qwen results.

Figure regeneration: Appendix E.

---

There are three kinds of visuals here: original figures from papers, our sentence diagrams (made-up answers for teaching), and actual result graphs (only after Qwen runs).

Published results and project illustrations are reported separately.

**1A. Knowledge Overshadowing — Zhang et al. (2025), Figure 1**
[Original paper, Figure 1 and other figures](https://arxiv.org/html/2502.16143v1) · [Published version](https://aclanthology.org/2025.findings-acl.1199/)

**Interpretation:** A familiar association can drown out a less familiar but important fact. Figure 1 shows an example involving a question about a singer and three factors: popularity (P), length (L), and model size (S).

**Our version:** Change the share of comments or their length; model size is a separate planned comparison. Keep the facts fixed.

Check whether the model stops considering other explanations. Their paper studies learned knowledge; ours studies the information in the prompt.

We are not claiming the same scaling law applies.

**Our example:** Keep MetroCart's facts fixed and increase the share of hacker opinions. Our Figure 1 in Section 7 will show how the model responds, not a copy of their fitted curve.

**Published figure 1 — Knowledge Overshadowing | PDF page 1. Original paper, not ForesightAI results.** [Source PDF](https://aclanthology.org/2025.findings-acl.1199.pdf#page=1)

![Original research figure 1 — saved figure (no model needed)](figures/v2-15.jpg)

**Figure 1:** Focus on the familiar name versus the requested type of person. The mismatch is the error.

**Figure 1 connection:** If Qwen stops mentioning overload or a software deployment error as the hacker story becomes popular, the social narrative may be crowding out other possible causes. That is our version of overshadowing.

**Published figure 2 — Knowledge Overshadowing | PDF page 4. Original paper, not ForesightAI results.** [Source PDF](https://aclanthology.org/2025.findings-acl.1199.pdf#page=4)

![Original research figure 2 — saved figure (no model needed)](figures/v2-17.jpg)

**Figure 2:** The horizontal axes are model size, relative knowledge popularity, and relative knowledge length.

The vertical axis is the rate of factual hallucination. Each panel changes one factor while holding the others fixed.

The fitted lines show the pattern observed in their training experiment; our Qwen plots might look different.

**Figure 2 connection:** We change popularity, then separately compare short and long comments.

For example, “Anonymous user: I suspect cyberattack.” versus “Anonymous user: I suspect cyberattack. This is my personal guess, and I have no further details.” No new facts are added.

Model size is a planned separate comparison, using Qwen2.5-0.5B and Qwen2.5-3B with the same inputs.

---

**Implication:** Think of one loud story taking up all the attention. The question is whether other reasonable explanations get pushed aside.

In her paper, popularity refers to knowledge exposure during training. In our experiment, popularity means the proportion of comments supporting a guess in the input.

We borrow the idea, not the original measurement or proof. We are not retraining the model.

**Our version — actual example we will give Qwen (Figures 1–2)**

![Sentence comparison diagram 1 — saved figure (no model needed)](figures/v2-20.svg)

**Same known fact in every test:** MetroCart checkout failures increased by 30% at 2 PM. The cause is not established.

| Test | Hacker opinions | Overload opinions | Expected answer |
|---|---:|---:|---|
| A is unpopular | 2 | 18 | C — insufficient evidence |
| Balanced | 10 | 10 | C — insufficient evidence |
| A is popular | 18 | 2 | C — insufficient evidence |

**Example of a failure (not a real model response):** “Choice: A. Most people say it was hackers.” A careful answer would be “Choice: C. The checkout failures do not establish a cause.”

**Our graph:** The x-axis is the share favoring A; the y-axis is the percentage of Qwen responses choosing A, B, or C. If A rises with popularity even though the facts never change, we investigate why.

Section 7 shows the actual measured curve after running Qwen.

---

**Implication:** Same website problem, two different crowds. If the answer changes just because the crowd changes, that is the behavior we want to measure.

Choosing A or B as a confirmed cause too early is a different failure from forgetting to mention B as a possibility.

The first is measured by multiple-choice answers; the second by the open-ended task in Section 6. We do not assume either failure will happen.

**Popularity, length and hypothesis coverage**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

The paper changes how strongly a piece of knowledge is represented. We adapt that idea by changing how often an opinion occurs **in our input**, not in training data.

| What Qwen reads | Low hacker popularity (10%) | High hacker popularity (90%) |
|---|---|---|
| Same observation | Checkout failures increased by 30% at 2 PM. | Checkout failures increased by 30% at 2 PM. |
| Hacker comments | Anonymous user: I suspect cyberattack. × **2** | Anonymous user: I suspect cyberattack. × **18** |
| Overload comments | Anonymous user: I suspect server overload. × **18** | Anonymous user: I suspect server overload. × **2** |
| Same question | Which cause is established? A = cyberattack; B = server overload; C = insufficient evidence. | Same question |
| Expected verdict | C — insufficient evidence | C — insufficient evidence |

The × counts are a compact visual representation. Python actually writes each comment as its own sentence and shuffles the order using the same seed. The model does not see the × notation.

| Length condition | Exact example sentence |
|---|---|
| Short | Anonymous user: I suspect cyberattack. |
| Long | Anonymous user: I suspect cyberattack. **This is my personal guess, and I have no further details.** |

The long sentence adds words but no evidence. The length test keeps the number of comments, ratio and source fixed.

**From data to code to graph:**

`make_input(cases[0], share=.1, total=20)` → 2 hacker comments; `make_input(cases[0], share=.9, total=20)` → 18 hacker comments.

Then `ask(history)` generates the answer; `parse_choice(answer)` records the verdict. The raw prompt and answer go into the CSV. Section 7 groups the rows by popularity.

**Two different things to check:** If Qwen says “Choice: A. Most comments blame hackers,” that is an example of unsupported commitment.

If an open-ended response only suggests hackers and misses overload or a software deployment error, that is a different possible failure: incomplete hypothesis coverage.

Neither example is a measured response.

**Implication:** Same problem, same question, different amounts of the same sentences. We check whether the loud story changes what Qwen decides or considers. Model size is a planned comparison, not required for the MVP.

**1B. Hold, Lure, and Self-Correction — Fang et al. (2026), Figures 1 and 4**
[Original paper and figures](https://arxiv.org/html/2604.04325v1)

**Interpretation:** Give an AI clues one by one. A strong-looking clue might tempt it to answer before enough proof arrives. Figure 4 moves a lab result to different turns and measures when the model first answers.

**Our version:** Move an ambiguous observation about an outage from turn 2 to turn 3, keeping the final facts identical. Ask after each turn, or only at the end.

Keep the earlier AI answers in the conversation so we can see whether it changes its mind.

A clinical clue is not the same as an online rumor: our ambiguous observations and opinions are labeled separately.

**Published figure 1 — Hold, Lure, and Self-Correction | PDF page 3. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2604.04325v1#page=3)

![Original research figure 3 — saved figure (no model needed)](figures/v2-23.jpg)

**Figure 1:** Follow the case from left to right: split evidence into pieces, reveal pieces over time, and compare when the model answers. We use the same idea with a fictional outage.

**Published figure 2 — Hold, Lure, and Self-Correction | PDF page 6. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2604.04325v1#page=6)

![Original research figure 4 — saved figure (no model needed)](figures/v2-25.jpg)

**Figure 2:** Panel (a) counts first answers by turn. Panel (b) tracks hold, correct, and incorrect answers. Panel (c) compares guess rates across models. In our version, C means the cause is not established yet.

**Published figure 3 — Hold, Lure, and Self-Correction | PDF page 8. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2604.04325v1#page=8)

![Original research figure 5 — saved figure (no model needed)](figures/v2-27.jpg)

**Figure 3:** Each small chart is a different AI model. The bars show the proportions of hold, correct, and incorrect answers as more clues arrive. Our Section 7A plots our own Qwen answer mix at each turn.

**Published figure 4 — Hold, Lure, and Self-Correction | PDF page 9. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2604.04325v1#page=9)

![Original research figure 6 — saved figure (no model needed)](figures/v2-29.jpg)

**Figure 4 (the lure figure):**

- Panel (a) moves the lab result to early, middle, or late turns.

- Panel (b) shows how waiting and answers change.
- Panel (c) measures how many turns separate wrong-to-right and right-to-wrong changes.
- Our version moves the same ambiguous observation between turns 2 and 3; Section 7A records the first commitment and correction rates.
- We are not claiming a medical result is equivalent to a social rumor.

---

**Implication:** Holding = waiting for proof. Lure = a clue that may make the AI guess too soon. Self-correction = fixing the wrong turn-3 verdict after new proof; earlier recovery is a separate observation.

A lure is not necessarily false information. In our case, unusual traffic really happened within the fictional story, but unusual traffic alone does not prove a cyberattack.

That is different from a comment that merely guesses hackers.

**Our version — actual four-turn conversation (Figures 1–4)**

![Sentence comparison diagram 2 — saved figure (no model needed)](figures/v2-32.svg)

This is a fictional case from our dataset, not a transcript of Qwen.

| Turn | Early lure | Late lure | Expected |
|---|---|---|---|
| 1 | Checkout failures increased 30% at 2 PM. | Same | C |
| 2 | Unusually high network traffic was observed; its origin is unknown. | More customers reported checkout failures. | C |
| 3 | More customers reported checkout failures. | Unusually high network traffic was observed; its origin is unknown. | C |
| 4 | Authenticated incident analysis establishes ordinary server overload as the cause and rules out a cyberattack. | Same | B |

After each turn we ask Qwen which cause is established. Its earlier replies remain in the chat. The clue about traffic is a real observation *within the fictional case*, but it does not establish an attack.

**Figure 1:** This table is how we split one case into stages.

**Figure 2:** If Qwen first says A at turn 2, its first commitment is turn 2, before decisive evidence. If it says C until turn 4, it has held appropriately.

**Figure 3:** Example paths, not model outputs:

| Behavior | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Holds until proof | C | C | C | B |
| Guesses, then corrects | C | A | A | B |
| Guesses, then persists | C | A | A | A |

**Figure 4:** Compare the early and late lure with a no-lure control. Do premature answers cluster around the clue's arrival?

We also repeat the test with proof of a cyberattack instead of overload. An early guess is still unsupported even if it later happens to be right.

---

**Implication:** We tell Qwen the story in four pieces. If it guesses hackers on turn 2 and corrects itself on turn 4, we can see both the mistake and the recovery.

A = cyberattack, B = overload, C = insufficient evidence in this example. A guess that happens to match the final answer is still premature if it was not supported when made.

We test both possible final endings. The answer examples in the diagram are written by us, not by Qwen.

**Conversation inputs**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

| Message arriving now | Early-lure test | Late-lure test |
|---|---|---|
| Turn 1 | Checkout failures increased by 30% at 2 PM. | Same |
| Turn 2 | Unusually high network traffic was observed; its origin is unknown. | More customers reported checkout failures. |
| Turn 3 | More customers reported checkout failures. | Unusually high network traffic was observed; its origin is unknown. |
| Turn 4 | Authenticated incident analysis establishes ordinary server overload as the cause and rules out a cyberattack. | Same |

After each observation we append the same question: "Which cause is established? A = cyberattack; B = server overload; C = insufficient evidence." (plus the required answer format).

The actual earlier assistant responses remain in the chat history. **The model does not get the turn 4 sentence until turn 4.**

This core conversation test isolates clue timing; it does not include the crowd comments.

| Example answer path (not measured) | Meaning |
|---|---|
| C → C → C → B | Insufficient evidence until overload is established. |
| C → A → A → B | Guesses cyberattack, then corrects to overload. |
| C → A → A → A | Guesses cyberattack and fails to revise. |

**Code:** `updates(case, "early", "B")` vs `updates(case, "late", "B")`. The four-turn runner appends each new message and model reply, then saves each turn.

Section 7A counts when the first commitment happens and whether the final answer matches the proof.

**1C. ROUNDS — Fang et al. (2026), Figure 2 and Table 4**
[Original figure and tables](https://arxiv.org/html/2611.19636v1)

**Interpretation:** The same medical advice can have a different effect depending on who says it and how many people agree. Figure 2 changes the number of clinicians supporting competing diagnoses.

**Our version:** Give Qwen identical opinions attributed to ordinary users or claimed experts. We do not give those experts extra evidence. This tests the effect of the source label, not whether real experts are reliable.

**Published figure 1 — ROUNDS | PDF page 2. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2611.19636v1#page=2)

![Original research figure 7 — saved figure (no model needed)](figures/v2-35.jpg)

**Figure 1:** Left = the same medical findings; middle = different response formats and advice sources; right = the outcomes measured.

Our equivalent is fixed outage facts, different source labels, and Qwen's verdict.

**Figure 1 connection:** Change only the source label, not the underlying claim or facts.

**Published figure 2 — ROUNDS | PDF page 7. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2611.19636v1#page=7)

![Original research figure 8 — saved figure (no model needed)](figures/v2-37.jpg)

**Figure 2:** The left panel measures final accuracy and the right measures explicit abstention. The horizontal axis is how many clinicians (out of five) support the correct diagnosis.

Compare vote counts even before the majority flips. Our authority experiment compares the same opinions labeled as ordinary users or claimed experts.

Section 7 shows an authority × popularity heatmap. The separate Table 4 plot in Appendix A is a redraw of the published Qwen numbers, not a ForesightAI result.

**Figure 2 connection:** Vary the ratio of agreeing accounts and compare how often Qwen commits to a cause. Our heatmap uses source label on one axis and popularity on the other.

It shows the rate of unsupported A/B choices, not the original paper's clinical accuracy.

---

**Implication:** Would the same sentence sound more convincing if a doctor or expert said it? The researchers studied that in medical cases; we study source labels in fictional online discussions.

A claimed expert is not a verified expert. We keep the wording, facts and vote ratio fixed so we are testing whether the label itself matters, not whether expert knowledge is useful.

**Our version — actual source-label and vote-count experiment (Figures 1–2)**

![Sentence comparison diagram 3 — saved figure (no model needed)](figures/v2-40.svg)

**Fixed fact:** checkout failures rose 30%; no cause is established.

| Condition | Statement attributed to each account | Count favoring hackers |
|---|---|---:|
| Anonymous users, balanced | “I suspect cyberattack.” / “I suspect server overload.” | 10 of 20 |
| Claimed experts, balanced | Same two opinions | 10 of 20 |
| Anonymous users, dominant A | Same two opinions | 18 of 20 |
| Claimed experts, dominant A | Same two opinions | 18 of 20 |

We also run 2 of 20 favoring A. The account labels in our code are “Anonymous user” and “Self-described domain expert.” We do not provide credentials, security logs, or extra evidence. The correct choice remains C.

**Example interpretation (hypothetical):** If unsupported commitment is 20% for ordinary users and 60% for claimed experts at the same 90% ratio, the difference is 40 percentage points.

These are invented teaching numbers, not measured results.

---

**Implication:** Popularity asks how many people say it. Authority asks who says it. We test both so we can see if either one influences Qwen.

The heatmap counts unsupported A/B choices, whether the crowd favors A or B. That is not automatically the same as following the majority; the raw choice counts let us check which cause Qwen favored.

**Source-label comparison**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

| What Qwen reads | Ordinary-user condition | Claimed-expert condition |
|---|---|---|
| Observation | Checkout failures increased by 30% at 2 PM. | Same |
| Hacker opinion ×18 | **Anonymous user:** I suspect cyberattack. | **Self-described domain expert:** I suspect cyberattack. |
| Overload opinion ×2 | **Anonymous user:** I suspect server overload. | **Self-described domain expert:** I suspect server overload. |
| Question | Which cause is established? A = cyberattack; B = server overload; C = insufficient evidence. | Same |
| Expected | C — insufficient evidence | C — insufficient evidence |

**Only the label changes.** No credentials, no logs, no new evidence. The actual generated prompt contains 20 individual comment lines, not the × notation.

`make_input(case, share=.9, source="user")` compared with `make_input(case, share=.9, source="expert")`. The code also runs the 10% and 50% ratios. We group answers by source and share in the authority heatmap.

**Implication:** We're changing who supposedly said the sentence, not what they said. The heatmap measures unsupported commitment; raw A/B counts tell us whether that commitment favored the crowd.

**1D. Popular Knowledge Propagates More Errors — Zhang and colleagues (2026), Figure 1**
[Original paper and figures](https://arxiv.org/html/2609.08067v1)

**Interpretation:** Changing a fact inside a model can damage other connected facts. Their Figure 1 also illustrates a training-based way to reduce forgetting.

**Our version (future extension):** If Qwen accepts an unsupported hacker claim, does it also invent details about data theft? Their study changes model weights; ours does not. This is inspiration, not a replication.

**Published figure 1 — Popular Knowledge Propagates More Errors | PDF page 1. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2609.08067v1#page=1)

![Original research figure 9 — saved figure (no model needed)](figures/v2-43.jpg)

**Figure 1:** Left compares how often existing facts become wrong after popular versus rare facts are updated.

Right shows a training-based mitigation called PopAnchor. Our analogy is an AI that accepts a rumor and then makes other unsupported claims based on it.

This is a future extension, not an implemented experiment or a replication of their fine-tuning method.

---

**Implication:** One wrong assumption can lead to more wrong statements.

This paper actually modifies learned knowledge. Our proposed extension only changes what Qwen reads. We have not implemented the follow-up error-propagation experiment yet.

**Our version — what could happen after a wrong assumption (Figure 1)**

![Sentence comparison diagram 4 — saved figure (no model needed)](figures/v2-46.svg)

**Known fact:** checkout failures increased by 30%. No information establishes a data breach.

**Unverified opinion:** “I suspect cyberattack.”

**Possible AI response (made-up example):** “It was a cyberattack, and payment details were stolen.”

The first part is an unsupported cause; the second is a new unsupported claim. A careful response would explain that there is no evidence of either a confirmed attack or stolen data.

**Our future extension:** Count new unsupported claims after an unsupported cause is adopted. Compare the same case with neutral and hacker-dominant comments.

The current notebook exports raw explanations for review, but does not yet automate this follow-on test. Their figure measures changes to learned knowledge during training, not this exact behavior.

---

**Implication:** Saying “hackers caused it” without proof is one problem. Adding “payment details were stolen” without any evidence creates another problem.

A statement can be unsupported without being proven false. We count whether evidence is missing, not whether we can prove the opposite.

**Trace the extra unsupported sentence (future work)**

Given: Checkout failures increased by 30% at 2 PM.

Opinion: Anonymous user: I suspect cyberattack.

Hypothetical model text: “It was a cyberattack. Payment details were stolen.”

| Output sentence | Is it supported by the input? |
|---|---|
| It was a cyberattack. | No — the cause is unresolved. |
| Payment details were stolen. | No — nothing says that happened. |

The current CSV preserves the entire response, so a reviewer can inspect both sentences. A dedicated downstream-claim counter is **future work**, not part of our implemented pilot.

This is an analogy to error propagation, not the paper's weight-update experiment.

**1E. Other reading that helps us design the test**

| Paper / figure | What it means | What we borrow |
|---|---|---|
| [Conformity in Large Language Models (2025)](https://aclanthology.org/2025.acl-long.195/) | Group opinions may affect AI answers. | Compare the answer before and after social pressure. |
| [Lost in the Middle (2024), Figure 1](https://arxiv.org/html/2307.03172) | Relevant information may be overlooked when buried in a long input. | Move the same proof to the beginning, middle or end. |
| [What Evidence Do Language Models Find Convincing? (2024)](https://aclanthology.org/2024.acl-long.403/) | Conflicting evidence can be evaluated in different ways. | Separate the quality of evidence from persuasive language. |
| [Whose Facts Win? (2026)](https://aclanthology.org/2026.acl-long.1357/) | Source framing and repetition matter in knowledge conflicts. | Compare source labels and repeated opinions. |
| [Easier to Mislead Than to Correct (2026)](https://arxiv.org/abs/2606.01637) | Social influence may affect wrong and correct answers differently. | Track answer changes, not just final accuracy. |
| [AbductionBench (2026)](https://arxiv.org/abs/2611.10705) | Finding explanations from incomplete clues can be evaluated in several ways. | Test generation, selection, information requests and revision. |
| [Illusory truth effect review (2026)](https://www.nature.com/articles/s41467-026-70041-x) | Repetition can affect people's belief in a claim. | Test repetition separately from popularity; do not assume AI thinks like people. |

[Copies or Sources? (2026)](https://arxiv.org/abs/2610.06192) also motivates our optional account-label test.

The first four papers motivate the central design; the remaining studies provide supporting context. These are links to original figures or publications, not new ForesightAI results.

**Our version examples for the other papers:**

| Research idea | What we actually test or plan |
|---|---|
| Conformity | Separate no-comment and 18/2 prompts test majority sensitivity. A follow-up that challenges a previously stated answer remains future work. The new revision comparison introduces the crowd on turn 1 instead. |
| Repetition | 8/10, 16/20 and 40/50 favor hackers (all 80%). Measure A/B commitment as the number of comments grows. More comments also mean more tokens, which we record. |
| Source preference | Give the same “I suspect cyberattack” opinion a user or claimed-expert label. No extra evidence. |
| Easier to mislead than correct | Compare the last pre-proof answer and final answer. Our current study measures corrections after decisive evidence; a separate misleading-advice reversal experiment is future work. |
| Abductive reasoning | Ask “List up to three plausible causes and what information would distinguish them.” A useful response might suggest overload, attack, or a deployment error and request relevant logs. Human reviewers score actual outputs. |
| Conflicting evidence | Decisive server analysis establishes overload while most opinions favor an attack. We test whether Qwen uses the analysis, rather than comparing two equally verified contradictory sources. |

---

The other readings help with controls, measurement and future extensions.

**1E.1 Conformity in Large Language Models (2025) — Figure 1**

**Published figure 1 — Conformity in Large Language Models | PDF page 2. Original paper, not ForesightAI results.** [Source PDF](https://aclanthology.org/2025.acl-long.195.pdf#page=2)

![Original research figure 10 — saved figure (no model needed)](figures/v2-50.jpg)

**Interpretation:** The model originally knows an answer, but a group gives a different answer. The figure shows an example of the model changing to match the incorrect group.

**Our connection:** We ask whether a crowd can push Qwen away from uncertainty when no cause is established. Their task is a known-answer question; our task has incomplete evidence.

Same fact: checkout failures increased by 30%.
Crowd: 18 of 20 comments suspect a cyberattack.
Expected: C, insufficient evidence.
Example failure: A, because most people agree.

The paired before/after social-pressure test is future work; our current popularity sweep compares separate prompts.

**Baseline vs. crowd inputs**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

| No-comment control | High-popularity condition |
|---|---|
| Checkout failures increased by 30% at 2 PM. | Checkout failures increased by 30% at 2 PM. |
| (No comments) | Anonymous user: I suspect cyberattack. ×18; Anonymous user: I suspect server overload. ×2 |
| Which cause is established? A = cyberattack; B = server overload; C = insufficient evidence. | Same question |
| C — insufficient evidence | C — insufficient evidence |

`make_input(case, total=0)` vs `make_input(case, share=.9,total=20)`. These are separate prompts sent to the same checkpoint.

A shift toward cyberattack would indicate sensitivity to the supplied majority. Unlike the paper, we are not yet running a paired follow-up conversation where an earlier answer is challenged by a group.

**1E.2 Whose Facts Win? (2026) — Figure 8**

**Published figure 8 — Whose Facts Win? | PDF page 7. Original paper, not ForesightAI results.** [Source PDF](https://aclanthology.org/2026.acl-long.1357.pdf#page=7)

![Original research figure 11 — saved figure (no model needed)](figures/v2-53.jpg)

**Interpretation:** Repeated lower-credibility information can outweigh a higher-credibility source.

The figure compares social-media majority/repetition against government sources; the positions of the plotted markers represent source preference.

**Our connection:** We separately compare the count of repeated comments and the label of the source. We do not claim a self-described expert is actually a trusted authority.

Technical example: 8/10 vs 40/50 comments favor A (same 80%, different count). In the authority test, use exactly the same 18/2 split and change only the source labels.

**Repetition vs. popularity**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

| Input | 10 comments | 50 comments |
|---|---|---|
| Observation | Checkout failures increased by 30% at 2 PM. | Same |
| Hacker sentence | Anonymous user: I suspect cyberattack. ×8 | Anonymous user: I suspect cyberattack. ×40 |
| Overload sentence | Anonymous user: I suspect server overload. ×2 | Anonymous user: I suspect server overload. ×10 |
| Ratio | 80% | 80% |
| Expected | C — insufficient evidence | C — insufficient evidence |

The model receives all repeated sentences.

The percentage does not change, but the amount of text does, so we log token count. `make_input(case, share=.8,total=10)` vs `make_input(case, share=.8,total=50)`.

This tests repeated unverified opinions, not a replication of the paper's conflicting factual sources.

**1E.3 Copies or Sources? (2026) — Figure 1**

**Published figure 1 — Copies or Sources? | PDF page 1. Original paper, not ForesightAI results.** [Source PDF](https://arxiv.org/pdf/2610.06192v1#page=1)

![Original research figure 12 — saved figure (no model needed)](figures/v2-56.jpg)

**Interpretation:** A sensor gives one reading. Other agents repeat that reading. Repetition does not create more independent readings, but an aggregator may count the copies as extra evidence.

**Our connection:** We use the same 20 comment texts and change apparent account IDs: many distinct accounts versus one account per stance repeating its claim. Distinct accounts are not proof of independent sources.

Example: Account 01: I suspect cyberattack. Account 01: I suspect cyberattack. Compare the same sentences with different account IDs.
Expected: C in both conditions.
In Section 6A, source diversity is an optional implemented pilot.

**Account-label comparison (optional)**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

| One account per stance | Distinct account IDs |
|---|---|
| Account 01: I suspect cyberattack. | Account 01: I suspect cyberattack. |
| Account 01: I suspect cyberattack. | Account 02: I suspect cyberattack. |
| Account 02: I suspect server overload. | Account 03: I suspect server overload. |

These are illustrative excerpts, grouped for readability. The actual extension generates 20 lines in the same shuffled order, with 18 hacker and 2 overload opinions.

For distinct mode, account IDs follow the line index. For the repeated mode, there is one account ID for each stance.

Same observation, same opinions; expected C in both. `extension_inputs(case)` creates the two source-diversity conditions in Section 6A. Different accounts are not necessarily independent evidence.

**1F. Lost in the Middle — Liu et al. (2024), Figure 1**

**Published figure 1 — Lost in the Middle | PDF page 2. Original paper, not ForesightAI results.** [Source PDF](https://aclanthology.org/2024.tacl-1.9.pdf#page=2)

![Original research figure 13 — saved figure (no model needed)](figures/v2-59.jpg)

The x-axis is the position of the document containing the answer, and the y-axis is accuracy. The U-shape shows performance dropping when the answer is buried in the middle.

The dashed horizontal line is a closed-book comparison.

**Our version:** Keep the same comments and move the observation-plus-decisive-evidence block to the start, middle, or end. Section 7 Figure 3 compares the actual Qwen accuracy at those positions.

Our short synthetic prompts are not the same as the authors' long-document benchmark.

[Published paper](https://aclanthology.org/2024.tacl-1.9/)

---

**Implication:** Important information might be easier to miss when it is surrounded by a lot of other text.

Information position is where evidence appears within one input. Lure timing is when a clue arrives across several chat turns. These are two different experiments.

**Our version — the exact same information in a different order (Figure 1)**

![Sentence comparison diagram 5 — saved figure (no model needed)](figures/v2-62.svg)

Suppose the verified analysis establishes server overload, but 18 of 20 comments favor hackers.

| Test | Beginning | Middle | End |
|---|---|---|---|
| Start | Facts + decisive proof | Comments 1–10 | Comments 11–20 |
| Middle | Comments 1–10 | Facts + decisive proof | Comments 11–20 |
| End | Comments 1–10 | Comments 11–20 | Facts + decisive proof |

The question is identical and always comes last. Expected answer: **B — server overload** in all three tests. We also repeat with proof of A, so the model cannot pass by simply choosing overload every time.

**Our graph:** X-axis = start, middle, end. Y-axis = correct answer rate. If middle placement has lower accuracy, this suggests a position effect in our setup.

Our inputs are short compared with the original paper, so a flat graph is also a meaningful result.

---

**Implication:** We move the unchanged observation and proof together; this is a block-position test, not an isolated proof-position test.

If Qwen misses the proof in one position more often than another, we have a possible position effect.

Here B is established from the start of the question because the full input includes the decisive evidence. Unlike the four-turn lure test, we are not withholding proof until later.

**Evidence placement in the prompt**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

**Evidence block:** Confirmed observations: Checkout failures increased by 30% at 2 PM.

Confirmed new evidence: Authenticated incident analysis establishes ordinary server overload as the cause and rules out a cyberattack.

**Comment block:** 18 lines saying "Anonymous user: I suspect cyberattack." and 2 lines saying "Anonymous user: I suspect server overload.", shuffled with the same seed in each test.

| Start | Middle | End |
|---|---|---|
| Evidence block | Comments 1–10 | Comments 1–10 |
| Comments 1–10 | Evidence block | Comments 11–20 |
| Comments 11–20 | Comments 11–20 | Evidence block |
| Same question | Same question | Same question |
| B — server overload | B — server overload | B — server overload |

`make_input(case, share=.9, proof="B", position="start")` vs the same call with `position="middle"` or `"end"`. The question always follows the context.

We also test proof of cyberattack. We measure final accuracy across positions, not attention weights.

**Full input**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

It is **not one continuous paragraph**. Each comment is a separate line within a single user message. The model gets the entire message at once, including the proof and the question.

Below is the actual middle-position example with seed 733 (18 hacker opinions and 2 overload opinions). The system message is "You are an assistant."

```text
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect server overload.
Confirmed observations: Checkout failures increased by 30% at 2 PM.
Confirmed new evidence: Authenticated incident analysis establishes ordinary server overload as the cause and rules out a cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect server overload.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Anonymous user: I suspect cyberattack.
Which cause is established? A = cyberattack; B = server overload; C = insufficient evidence. Start with Choice: A, B, or C, then give a short reason.
```

**Expected answer:** B — server overload. The other two tests contain the same 20 comment lines, the same report and the same question. Only the two evidence lines move.

Use the evidence-position viewer in Appendix B to move the report to the beginning, middle or end. The viewer labels the input structure; Qwen receives plain text.

No GPU or model inference needed. The viewer also works independently of the model setup.

**Implication:** We give Qwen all the facts in one message, unlike the lure experiment where we reveal them across separate turns.

We compare the correct-answer rate across the three positions. A lower middle score would suggest a positional effect, but we do not assume the result in advance.

## 2. Dataset

**Quick choice key:** A = first possible cause · B = second possible cause · C = insufficient evidence. For MetroCart, A = cyberattack and B = server overload.

For other incidents, A/B refer to their own causes. Saved results use the original cause labels even if the displayed options were swapped.

Five fictional incidents. Each has two possible causes (A/B), a third plausible alternative for the open question, an ambiguous clue, and two possible final evidence endings.

The correct answer is C (not enough evidence) before the proof. We test both endings so always choosing C, always choosing B, or always disagreeing with the crowd cannot pass.

The comments are synthetic. This gives us control, but it does not establish how real social-media users behave. Each case needs human review before a final study.

---

**Implication:** The dataset is a collection of questions and situations, like a test we give Qwen. It is not material we use to train Qwen.

The five incidents are made up, but the model responses will be real when we run it. We know what the expected answer is because we designed each case.

Early in a case the cause is unresolved; after decisive proof the expected answer is the established cause.

**All five scenarios — keep this key nearby**

| Incident | Choice A | Choice B | Choice C |
|---|---|---|---|
| MetroCart outage | Cyberattack | Server overload | Insufficient evidence |
| Flight delays | Aircraft maintenance issue | Severe weather | Insufficient evidence |
| Product complaints | Hardware defect | Incorrect setup | Insufficient evidence |
| Internet outage | Damaged cable | Routing configuration error | Insufficient evidence |
| Stock decline | Company scandal | Broad market selloff | Insufficient evidence |

**Important:** A and B are possible causes, not automatically right or wrong. Before decisive evidence, C is the expected verdict.

When the fictional proof establishes A or B, that cause becomes the expected answer. INVALID means we could not parse the model's answer; it is not the same as C.

**2A. Popularity, repetition, authority and length**

Popularity is the **share** of people who support a guess. Repetition is the **number** of comments. Authority is who supposedly said it. Length is how much text the claim takes up.

For example, 8 out of 10 and 80 out of 100 are both 80%, but the second discussion repeats the opinion much more.

We also have a compact vote-count version that keeps the two opinions named even when vote counts change. The comments are intentionally templated to avoid inventing new evidence.

---

**Implication:** 8 out of 10 and 40 out of 50 are both 80% popularity, but the second repeats the story more often. A long comment is different again: it has more words, not necessarily more supporters.

Longer discussions also have more text for the model to read. We record input token counts, and we use the compact vote-count comparison to help understand the difference.

These are related factors, not perfectly isolated in every test.

## 3. Model and prompts

**Run on Colab:** Runtime → Change runtime type → T4 GPU. In Appendix A model settings, change RUN_QWEN to True to load the model.

Set RUN_BATCH=True only when collecting the full pilot.

Qwen2.5-0.5B-Instruct is a lightweight smoke test; larger same-family checkpoints or Qwen3-4B may be evaluated separately.

Qwen3 thinking mode is disabled for comparable short answer extraction. Different model families are not a pure size comparison.

We keep the model weights fixed. The baseline only asks for a choice and reason. The improved instruction explicitly tells it not to treat unverified opinions as proof.

**Important:** No model results are generated when RUN_QWEN is False. All plots of results stay empty until you run actual inference.

Greedy decoding selects the highest-scoring next token; identical prompts are not independent tests (hardware/software can introduce numerical differences).

Both answer orders run in the pilot; three comment orders are used in full-study single-turn and generation tests.

---

A prompt is the information and instructions we send to the model. A token is a small chunk of text. Model size refers to the number of learned parameters, not the number of comments.

Greedy decoding means it picks the next most likely token instead of randomly sampling. Repeating the exact same input is not a useful independent trial.

**How Qwen processes the input**

| Keyword | Description | Our connection |
|---|---|---|
| Decoder-only Transformer | Reads an existing prefix and generates the next token. | Qwen reads the whole available prompt before writing its answer. |
| Self-attention | Tokens combine information from other permitted token positions. | The prompt contains the observed facts, comments and question. We test whether moving facts changes the answer. |
| Query, key, value (Q/K/V) | Query looks for relevant information; keys are compared with queries; values carry information into the weighted sum. | Conceptual model of how token context is computed, not a claim that specific comments received high attention. |
| Causal masking | A position cannot attend to later tokens in the sequence. | During generation the model only sees its existing prefix. Our experiment separately withholds the turn 4 proof until that turn. |
| Positional information | The model has information about token order. | Start/middle/end evidence experiment; position is the changed input. |
| Feed-forward network (FFN) | Transforms the representation at each position. | It is part of the pretrained model we execute, not a layer we implement. |
| Logits and vocabulary softmax | Convert output scores into next-token probabilities. | The model generates verdict text; our parser extracts the choice. |

**Visual technical example:**

Observation + opinions + question → token IDs → embeddings + positional information → causal self-attention + FFN (many layers) → output logits → next-token selection → answer text → parse_choice()

The attention equation:

$\mathrm{Attention}(Q,K,V)=\mathrm{softmax}(QK^T/\sqrt{d_k}+M)V$

Here $M$ masks future positions in causal attention (zero for allowed positions, negative infinity for masked positions).

Q and K give similarity scores, scaled by the square root of the key dimension; softmax turns them into weights over visible positions.

V supplies the values to combine. The language-model head uses a **different softmax over vocabulary tokens**.

**Interpretation:** an answer changing when the comments change does not prove the model attended more to the comments internally. We measure behavior, not attention weights.

**Why we use a pretrained decoder-only model**

| Keyword | Description | Our connection |
|---|---|---|
| Tokenization / BPE | Break text into known pieces and IDs. BPE learns common merges. | We use Qwen's own tokenizer and record the true input token count. |
| Autoregressive language modeling | Generate one next token given the prefix, then append it and repeat. | model.generate() writes the model's answer. |
| Pretraining | Learn general patterns from large text collections by updating weights. | Already done before we download Qwen. |
| Fine-tuning | Update learned parameters on new task data. | We do not do it in our experiments. |
| In-context learning | Adapt to instructions/examples in the current prompt without updating weights. | We change instructions and label mappings; our current task is primarily zero-shot prompting, not a few-shot learning experiment. |
| Cross-entropy loss | Penalize low probability assigned to the true training token. | Explains how language models learn; our evaluation is not training with this loss. |

**The key limitation:** plausible text is not verified truth. This is the motivation for our project. A fluent explanation for hackers is not enough to establish hackers as the cause.

**Architecture choice:** BERT = encoder-only/full input (often classification); GPT-style/Qwen = decoder-only/causal generation; T5 = encoder–decoder/text-to-text.

We use Qwen because we want both generated alternatives and conversation replies, not because BERT or T5 are incapable of useful tasks.

**How this differs from a recurrent model**

- **Embedding:** a learned vector representing a token. **Hidden state:** a representation that depends on context. They're not the same.
- **Long-distance dependency:** a word or clue far back can matter to a later prediction. In our case, the initial outage report still matters after many comments.
- **RNN/LSTM:** models that update recurrent states over time; useful background for why we moved toward attention. Qwen is a Transformer, not an LSTM. Our chat history is a Python list of messages, not an LSTM cell state.
- **Teacher forcing / BPTT:** training concepts, not operations we perform in our evaluation.

*Technical background: [sequence models, slides 5–7 and 15–17](https://drive.google.com/file/d/1w4UA_ph68TD3NNfD8lIvpoUnRZPtypEX/view); [Transformers, slides 40–43](https://drive.google.com/file/d/1M1-uGgI3zWj5Fnp-2PblAKiZTnhCfOKL/view); [pretraining and tokenization, slides 9–14 and 38–39](https://drive.google.com/file/d/1n9t0nO8zKzdcPSkndxbrC0dMRobqaoy_/view).*

**Token IDs — technical example**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence (MetroCart).

The optional tokenizer demonstration in Appendix B uses the already-loaded tokenizer. It does not generate answers, train Qwen or add calls to the experiment.

Tokens are pieces of text; IDs are vocabulary indices, not learned vectors. The context length we log in ask() includes the chat-template tokens, whereas this small example only shows the selected text.

**3A. Exact experiment prompts**

![Sentence comparison diagram 6 — saved figure (no model needed)](figures/v2-70.svg)

Use the exact-prompt preview in Appendix B. It displays the complete prompt generated for each implemented condition.

These are actual experiment inputs from our fictional dataset, not actual Qwen answers. It runs even when RUN_QWEN is False.

The expected answer is C when there is not enough proof. Once the verified analysis establishes overload, the answer is B. The actual response is unknown until Qwen runs.

---

This preview does not ask Qwen for an answer. The expected answer comes from our dataset. The real answer is collected later.

Baseline means ordinary instructions; evidence-first means we explicitly ask it to distinguish facts from opinions. We are testing whether that extra instruction helps, not assuming it does.

**Why changing the prompt is a useful test**

| Keyword | Description | Our connection |
|---|---|---|
| Instruction tuning / SFT | Train the model to produce demonstrated answers. | We use an already instruction-tuned checkpoint; we don't perform SFT. |
| RLHF / DPO / preference optimization | Train using judgments about which answers are preferred. | Background motivation: preferred or confident text is not necessarily true (slides 10, 15). We do not test which training objective caused an error. |
| Frozen model | No optimizer or weight update. | model.eval() and torch.inference_mode() run inference only. |
| Zero-shot prompting | Task instructions with no worked demonstrations. | Both current baseline and evidence-first prompts are zero-shot. Social opinions are data, not labeled demonstrations. |
| One-shot / few-shot prompting | Supply one or several worked examples. | Optional future mitigation, not evaluated in this pilot. |
| Task + context + output format | Say what to do, supply information, and specify answer format. | make_input() combines facts/opinions and question() requires a choice plus reason. |
| Prompt sensitivity / robustness | Changing wording or order can change outputs. | Our controlled comparison of source labels, popularity, order and evidence-first instructions. |
| Untrusted context | Outside text is data, not authorized instructions. | Social comments are unverified opinions. This is narrative influence, not a prompt-injection attack experiment. |
| Chain-of-thought (CoT) | Ask for intermediate reasoning or provide worked reasoning examples. | We ask for a brief reason, not a formal CoT intervention. A fluent reason still needs verification (slide 21). |
| PEFT / LoRA / adapters | Train a smaller set of parameters while preserving much of the backbone. | Not used; future work only if a training intervention becomes justified. |

**Example — controlling answer-label bias:** If A = cyberattack and B = overload, proof of overload should produce B. Swap the displayed labels so A = overload and B = cyberattack; the same proof should produce A. canonical() converts the displayed answer back to the original cause before analysis.

Both pilot and full-study modes use both label orders for choice tasks. This tests answer-label sensitivity, not weight learning.

**Example — comparing instructions:** The baseline system instruction is "You are an assistant." Evidence-first asks the same model to distinguish observations from opinions, consider alternatives and revise when decisive evidence arrives.

We hold the facts and comments constant and compare the actual results. The simulated report is supplied as input evidence; we do not retrieve real documents or claim to implement a RAG system.

*Background: [post-training and prompting, slides 15–25](https://drive.google.com/file/d/15Mh359AT6TTxip1SgrWI77hMKUlQWVzB/view).*

**Side-by-side inputs**

**Choice key:** A = cyberattack · B = server overload · C = insufficient evidence.

The earlier colored examples group repeated sentences so they are easy to read. The side-by-side viewer in Appendix B prints the **full generated inputs**, including every repeated line in the real order.

Pick a comparison and see exactly what the model receives. No Qwen inference, GPU, or training needed. Run the imports and input-building cells first.

The displayed labels and expected verdict are outside the model input.

**3B. Technical workflow**

Here is how the implemented code works, step by step.

| Step | What the code does | Example |
|---|---|---|
| 1. Dataset | Load a fictional incident | MetroCart, A=cyberattack, B=overload |
| 2. Generate context | Build 20 opinions using a ratio and fixed seed | 18 A, 2 B |
| 3. Construct prompt | Combine observation, comments and the question | Which cause is established? |
| 4. Tokenize | Turn text into numerical token IDs | The tokenizer uses Qwen's own vocabulary |
| 5. Inference | Qwen generates new tokens; weights stay unchanged | A possible response begins “Choice: C” |
| 6. Parse | Extract the verdict and keep the full response | C = insufficient evidence |
| 7. Save | Write a row into CSV | case, ratio, actual answer, expected answer, tokens |
| 8. Analyze | Group by condition and count outcomes | % choosing A, B, C, invalid |

**Visual technical example (illustrative, not a measured response):**

Input fact → 18 hacker opinions + 2 overload opinions → Qwen → Expected C

If the actual model gives A before proof, our parser records A. That counts as an unsupported commitment. If it gives an explanation with a malformed answer, we record INVALID and keep the raw text instead of silently guessing.

**Implementation flow:** Construct the incident prompt → combine it with the system instruction → generate a Qwen response → parse the verdict → record the exact response and token count.

**Implication:** We don't write code that decides what answer Qwen should give. We write code that constructs the test and records what Qwen actually says.

## 4. Hypothesis evaluation

| Test | What changes | What stays fixed |
|---|---|---|
| Popularity | 10%, 30%, 50%, 70%, 90% favor A, plus no comments | Same facts, 20 comments |
| Vote counts | Same ratios as one compact summary | Both causes named, same total |
| Repetition | 10, 20, 50 comments at 80% A | Same ratio |
| Authority | User vs self-described expert | Same wording and ratio |
| Length | Short vs longer opinions | Same count, ratio and source |
| Position | Move the observation + proof block to start, middle, end | Identical text, only order changes |
| Prompt strategy | Baseline vs evidence-first | Same inputs |
| Lure | Ambiguous clue on turn 2 or 3 vs no lure | Same case and final proof |

Popularity and repetition can change token length. We record the real input token count, use a compact vote format, and flag unmatched length as a limitation.

Length itself intentionally changes text; it is not a clean test of token count alone.

For broader evaluation, limitations can be addressed through length-matched neutral controls, varied natural comment wording, more cases, and human checks.

**4A. Single-turn experiment runner**

Every result row records the exact prompt, model response, token count, choice and expected answer. A and B refer to the canonical cause, even when the display labels are swapped.

INVALID means the parser could not read a choice, not that the AI was definitely wrong.

---

The small pilot checks whether the method works. It is not enough to make a broad claim about AI. A result row includes a case, condition, prompt, answer and expected choice.

A bad answer format is marked INVALID so it is not mistaken for a reasoning failure.

**What changes:** one selected factor. **What stays the same:** the observation and question, except for the factor being tested. **What we record:** exact prompt, answer, token count and verdict.

## 5. Evidence revision

We want to see when Qwen first stops saying C. Early and late conditions use the same ambiguous observation and neutral update, just in a different order.

The no-lure control substitutes another neutral report (different wording, not token matched). The clue does not establish a cause; it may nevertheless tempt the model to guess A.

- **Holding:** C at every turn before proof.
- **Premature commitment:** any A or B before proof.
- **Correction (primary metric):** the last pre-proof choice (turn 3) is the wrong final cause, then turn 4 is correct. Earlier recovery is tracked separately by inspecting paths. An AI that guessed the eventual answer early still committed without sufficient evidence.

The main lure test has no social comments. A targeted matched comparison additionally introduces 20 comments (90% favor A) at turn 1 in the early-lure baseline conversation.

Both proof endings and displayed answer orders are included; compare with the matching no-crowd path. This tests initial narrative exposure, not a later challenge to an earlier answer.

We also compare asking every turn against asking only after all evidence is given. The latter is a fresh full-information baseline, not a conversation with earlier answers.

---

**Implication:** This test is like having a conversation with someone who only has half the story. We want them to wait until they know enough and be willing to revise.

The end-only comparison gets all the clues in one prompt and has no earlier answer to defend. The each-turn version remembers its earlier replies.

A difference between them may reflect the effects of timing, repeated questioning or prior answers; this alone does not isolate one internal cause.

**Important:** unusual traffic is a clue, not proof of hackers. **At turn 4:** the verified analysis resolves the question.

**Unit of analysis:** two synthetic incidents with repeated conditions, not hundreds of independent examples.

Identical pre-proof turns can recur across proof endings; treat the results as descriptive and do not use model-call counts as independent sample sizes.

## 6. Hypothesis generation

![Sentence comparison diagram 7 — saved figure (no model needed)](figures/v2-77.svg)

**Quick cause key (MetroCart):** A = cyberattack · B = server overload · another possibility = software deployment error.

This is open-ended: Qwen is not given A/B/C choices, and mentioning a possible cause does not mean it is confirmed.

We ask an open question rather than supplying A/B options. We compare a no-comment baseline with 10%, 50%, and 90% pro-A crowds.

The comment conditions already name A and B, so they measure alternative coverage under supplied suggestions, not purely unprompted discovery.

Does Qwen still mention both plausible causes and another reasonable explanation? Does it ask for useful evidence?

The machine does not grade its own output. We export a review sheet with empty columns for a human reviewer.

The reviewer should judge whether the explanation was actually offered, not just mentioned in passing. Other valid explanations are allowed.

Ideally use two reviewers who do not know the condition.

---

**Implication:** First ask the AI to think of possible causes. Later, ask which cause is established. Those are not the same question.

Saying “cyberattack is possible” is fine when evidence is incomplete. Saying “cyberattack is confirmed” is not.

We use human review because simply counting keywords could mistake “there is no evidence of a cyberattack” for actually proposing an explanation.

**Question:** what might have happened? **Good answer:** plausible alternatives and useful evidence requests. **Technical:** a human reviewer grades the full output, not just keywords.

**Generation vs. evaluation**

Checkout failures increased by 30% at 2 PM.

Anonymous user: I suspect cyberattack. ×18; Anonymous user: I suspect server overload. ×2 (the actual prompt has 20 lines).

| Hypothesis generation (open-ended) | Hypothesis evaluation (multiple-choice) |
|---|---|
| List up to three plausible causes and what information would distinguish them. Do not invent new observations. | Which cause is established? A = cyberattack; B = server overload; C = insufficient evidence. Start with Choice: A, B, or C, then give a short reason. |
| Possible answer: cyberattack, server overload, software deployment error; inspect logs and deployments. | Expected answer: C — insufficient evidence. |
| Human review: does it consider alternatives? | Parser: which cause does it say is established? |

The generation question does **not** supply A/B/C options. The examples are illustrative, not real outputs. One test measures breadth of possibilities; the other measures whether the model incorrectly commits.

**6A. Exploratory comparisons**

These exploratory comparisons are implemented but disabled by default. They are distinct from the core evaluation.

| Factor | Change | Example | Paper connection |
|---|---|---|---|
| Source diversity | Same statements, same number, different account labels | User 1 repeats 18 times vs 18 distinct accounts | [Copies or Sources? (2026)](https://arxiv.org/abs/2610.06192) — restated evidence in multi-agent systems; ours tests apparent account diversity, not verified independent evidence. |
| Confidence | Wording only | “I suspect” vs “I am certain” | [What Evidence Do Language Models Find Convincing? (2024)](https://aclanthology.org/2024.acl-long.403/) — evidence qualities; does not establish confidence effects in our task. |
| Emotion | Add emotionally charged phrasing | “This is concerning” vs “This is terrifying” | Exploratory; not a claim from the cited papers. |
| Narrative order | Move identical comment groups | A comments first vs B first | [Lost in the Middle (2024)](https://aclanthology.org/2024.tacl-1.9/) inspires a separate ordering test. |
| Evidence strength | No clue vs ambiguous observation vs decisive proof | Outage alone vs unusual traffic vs confirmed cause | [Hold, Lure, and Self-Correction (2026)](https://arxiv.org/abs/2604.04325). Expected answer changes only with decisive evidence. |
| Question framing | Neutral vs leading question | “What caused it?” vs “Why did hackers cause it?” | [Evaluating Reasoning Models for Queries with Presuppositions (2026)](https://aclanthology.org/2026.findings-acl.1201/). We retain the same A/B/C verdict format for comparison. |

**Implication:** We change how the story is delivered, not just how popular it is. For source diversity, distinct account names are not proof of independent sources.

For confidence and emotion, word counts may differ; log tokens and treat these as pilot comparisons.

For leading questions, assess whether the model rejects the unsupported assumption; the A/B/C verdict is a first-pass proxy.

Model size, narrative consistency, and a dedicated prior-commitment-only manipulation remain future extensions.

The existing open-ended vs multiple-choice and each-turn vs end-only comparisons provide related tests but are not pure isolated measures of these factors.

## 7. Evaluation metrics

Appendix D computes statistics from recorded Qwen responses. All reported response rates include invalid outputs in their denominators unless explicitly stated otherwise.

| Metric | Definition |
|---|---|
| Unsupported commitment | Choice A or B before decisive evidence is available |
| Appropriate holding | Choice C when the evidence does not establish either cause |
| First commitment | Earliest turn with a valid A or B verdict |
| Final accuracy | Choice matches the established cause after decisive evidence |
| Conditional correction | Correct turn-4 verdict among conversations with an incorrect A/B verdict at turn 3 |
| Hypothesis coverage | Human-reviewed plausible alternatives and requests for discriminating evidence |
| Invalid format | Response does not produce an unambiguous parsed choice |

These metrics describe observable behavior, not next-token probabilities, confidence, or internal attention. The small pilot is descriptive; variants of the same incident are not independent real-world cases.

**7A. Conversation results**

Figure 5 shows when a model first commits. Figure 6 follows individual answers as evidence arrives. A transition matrix counts changes from the last pre-proof answer to the final answer.

We also calculate a correction rate only among conversations whose last pre-proof answer was the wrong cause. Invalid answers remain visible.

The main timing charts exclude the crowd-added runs; a separate matched table compares initial crowd exposure against no crowd.

Example paths (not measured): C → C → C → B = waits; C → A → A → B = corrects; C → A → A → A = persists, if B is established.

---

**Implication:** Holding tells us whether the model waited. Premature commitment tells us whether it guessed too soon. Correction tells us whether it fixed its wrong answer at turn 3.

Correction rate uses only conversations where the last answer before the proof was the wrong cause. If there were no such answers, the rate is undefined (NaN), not zero.

A model can have good final accuracy but still give many premature answers.

**7B. Hypothesis coverage after human review**

**Quick cause key (MetroCart):** A = cyberattack · B = server overload · another possibility = software deployment error.

This is open-ended: Qwen is not given A/B/C choices, and mentioning a possible cause does not mean it is confirmed.

Fill the review sheet with 1 for yes, 0 for no, and leave uncertain entries blank. Use the review key to join the scores back to conditions.

Never auto-fill missing reviews. Plot how often Qwen considered A, B, other plausible causes, or requested useful evidence. This is a separate metric from A/B/C choice accuracy.

---

**Implication:** Someone reads the model's actual response and marks whether it considered reasonable causes. More alternatives are useful only if they make sense.

A blank review means not scored. Zero means a reviewer actually checked and marked no. Do not replace missing scores with zero.

## 8. Interpretation and limitations

An increased rate of choosing the dominant explanation under matched conditions would indicate sensitivity to the supplied social context in this test. A null or reversed effect is also informative. A model that consistently holds before proof but fails to choose the established cause afterward may be excessively cautious. Evidence-first prompting is evaluated as a potential mitigation rather than assumed to improve reliability.

The pilot has several limitations:

- Synthetic incidents and templated comments do not represent the complexity of real discussions.
- The default pilot contains two incidents and a small pretrained model; repeated variants and answer orders are not independent incidents.
- Some context manipulations also change token length or wording. Token counts are recorded, but full length matching is not implemented.
- The supplied source labels represent claimed authority, not independently verified credibility.
- Open-ended hypothesis quality and verdict/reason consistency require human review.
- The experiments measure output behavior, not internal causal mechanisms. Broader claims require additional incidents, independently reviewed annotations, held-out scenarios and model comparisons.

The findings may inform AI systems that summarize emerging events or consumer reviews, but real-world reliability and external validity require separate evaluation. The current work does not perform live social-media collection, retrieval, or model training.

## Interactive demo and reproduction

**Interactive research figure — visual demonstration**

Choose **Full demonstration — all factors** for a complete visual example with a final report, or choose an individual test. Press **Start demonstration**. The input is highlighted line by line, with opinion counts, links to possible causes and a live event log.

- **Full demonstration — all factors:** mixed social inputs, hypothesis generation, four evidence turns and a matched instruction comparison. The final report includes all input factors and expected or actual answers. This is a showcase, not an isolated causal experiment (six model calls if Qwen is on).
- **Does public opinion change the answer?** Compare two groups of opinions with the same facts.
- **Does new evidence change the answer?** Reveal four messages: the incident, a clue, an update and decisive evidence.
- **Can AI think of other explanations?** Ask for possible causes and useful evidence.

The preview works without Qwen. To generate real AI answers, enable Qwen in Appendix A with batch mode off, run the model setup, and rerun this cell. Animation speed is visible beside Start and defaults to Slow. Very slow is available for a detailed walkthrough. Optional experiment settings are collapsed by default.

Annotations describe the supplied synthetic inputs. They are not hidden model reasoning. Real responses, timings and evaluation are recorded only when inference is performed. Widget updates may be buffered in Colab.

**Research timeline:** each revealed input is labeled with the experiment being tested (hypothesis evaluation, lure, holding test, or evidence revision). After a real response, the timeline records the observed outcome, including holding, premature commitment, or self-correction when an incorrect preceding verdict becomes correct. The generation test is labeled separately. Preview mode shows expected behavior, not model results.

**Factor analysis explorer — from controlled inputs to measured behavior**

Run Appendix A first. Choose any factor below to view two representative inputs generated by the existing code. No GPU is needed for prompt previews. After Appendix C and the relevant results cells in D have run, the same explorer displays actual grouped results, sample sizes, and individual raw model records. The explorer is read-only; it does not run extra inference or alter the experiment design.

The single-turn plots group actual answers by condition; the conversation plots use whole paths rather than treating each turn as an independent conversation. Generation remains human-reviewed; no fabricated automatic coverage scores.