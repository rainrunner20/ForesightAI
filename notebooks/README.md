# ForesightAI | Research Lab V2

[Open the official notebook in Google Colab](https://colab.research.google.com/github/rainrunner20/ForesightAI/blob/feature/colab-narrative-pilot/notebooks/ForesightAI_Research_Lab_V2.ipynb)

This is the single authoritative notebook for CSC 733. It contains the original paper figures, plain-language explanations, controlled experiments, animated prompt analysis, live Qwen response trace, and measured-result charts.

## How to use it

- Read the visual walkthrough and paper connections first.
- Run Appendix A for setup. Keep `RUN_QWEN=False` for input previews.
- For the live demo, enable `RUN_QWEN=True` and keep `RUN_BATCH=False`; use Appendix B.
- For research data collection, enable the batch flag and follow Appendix C. Start with the small pilot before running the full study.
- Use Appendix D for measured results and human-reviewed hypothesis coverage.
- Export the V2 live trace JSON to inspect recorded outputs in the website's Visual Research Lab.

The fictional inputs and published paper figures are not our own measured Qwen results. No automatic hypothesis-quality or private-reasoning scores are claimed.

The older practice and stress-test notebooks were superseded by V2 and removed from this branch. All future notebook updates belong in V2.
