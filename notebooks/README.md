# ForesightAI | Colab Narrative Stress Test

This is an **isolated teaching pilot** for the project's updated question: can a dominant social explanation cause an LLM to commit prematurely when the facts are incomplete?

[Open the notebook in Google Colab](https://colab.research.google.com/github/rainrunner20/ForesightAI/blob/feature/colab-narrative-pilot/notebooks/ForesightAI_Narrative_Stress_Test.ipynb)

## Five-minute walkthrough

1. Open the link and choose **Runtime → Run all**. The default toy demonstration runs without an API key or LLM download.
2. Show the 50/50, 90%-A, and 90%-B comment mixtures. Explain that the verified MetroCart observations stay the same.
3. Use the slider to change which opinion dominates and toggle decisive verified evidence. **This interactive toy is programmed by us, not an LLM result.**
4. Read the three tasks: **generate alternatives → evaluate A/B/C → revise after evidence**.
5. Look at the demonstration chart and exported `foresightai_toy_demo.csv`. These results are deliberately labeled `TOY_SIMULATION`.

## Optional real-Qwen mini-pilot

- In Colab, a T4 GPU is preferable if available.
- Find `RUN_REAL_QWEN = False`, change to `True`, and run that cell and the one immediately below.
- This downloads public checkpoint `Qwen/Qwen2.5-0.5B-Instruct` (small demonstration model).
- It queries four input conditions and a decisive-evidence prompt, displays actual generated text, and exports `foresightai_qwen_pilot.csv`.
- Model outputs are only a **pilot**, not measured general reliability. The previous toy chart never becomes a Qwen chart.

## Core controls for research

Hold the observations, model, instruction wording and generation settings constant. Vary narrative ratio; shuffle comment order; balance A/B option order; check comment token counts; repeat over multiple cases and runs. Include a neutral no-comment condition. Avoid comments claiming independent privileged evidence in popularity-only comparisons.

## Limits

The default cells are a toy illustration. The optional real-model task is a small single-scenario demonstration, not a reproduction of Professor Zhang's work or the full ForesightAI study. It does not train a stance classifier, load real social data, evaluate many scenarios, or prove a causality claim.

## Related research

- Zhang et al., *The Law of Knowledge Overshadowing*, ACL 2025: https://aclanthology.org/2025.findings-acl.1199/
- Fang, Zhang et al., *Benchmarking Multi-turn Medical Diagnosis: Hold, Lure, and Self-Correction*, 2026: https://arxiv.org/abs/2604.04325

This notebook is intentionally separate from the current fact-checking runner and does not modify existing modules or datasets.
