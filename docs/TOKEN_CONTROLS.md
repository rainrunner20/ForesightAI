# Token-length controls

## Why this exists

If the prompt containing 32 rumors is longer than the one containing 4 rumors,
a model may behave differently because of length or token position, not because
it trusted the repeated statement. We need to measure this confound.

The standard seven conditions are unchanged. An **optional**
`neutral_length_control` adds synthetic posts with no factual assertions about
the claim, padding their combined system/user text until it is within one
token of the paired `rumor_pressure` condition.

## Run with a model-family tokenizer

```powershell
python -m pip install -e ".[tokenization]"
python -m foresight_ai.cli --provider mock --posts 4 `
  --conditions evidence_only,rumor_pressure,neutral_length_control `
  --tokenizer Qwen/Qwen3-4B --allow-tokenizer-download `
  --output outputs/token-control-demo.json
```

Use `--provider ollama --model qwen3:4b` only after starting a compatible,
locally installed Ollama model. Without `--allow-tokenizer-download`, only
already-cached tokenizer files are read. Check model/tokenizer provenance before
enabling downloads. Always choose a tokenizer that matches the inference
checkpoint as closely as possible.

This optional package is **not** needed for the basic demo or GitHub CI.
The `--tokenizer` flag alone performs token-count auditing on all seven
conditions; `neutral_length_control` additionally requires it.

## What appears in the JSON report

- `metadata.tokenizer`: the explicitly requested tokenizer ID, if any.
- `metadata.token_count_scope`: `system_plus_user_text_without_chat_template`.
- `rows[].prompt_tokens`: token count in concatenated system and user text.
- `rows[].neutral_target_tokens`: rumor-context target for the neutral control.
- `rows[].token_gap_vs_rumor`: measured difference; within ±1 or the run fails.

## Interpretation and limitations

- **Not full Ollama prompt tokens.** Token counts exclude the provider's chat
  template, hidden or injected tokens, and any automatic prompt rewriting.
  When reporting research results, describe the measurement accurately.
- A Hugging Face tokenizer may differ from the actual tokenizer bundled with
  a quantized Ollama model. Confirm the mapping before treating it as exact.
- Neutral-padding posts are artificial; they match length, not discourse
  naturalness, position-level token identities, or sentiment.
- A neutral condition is a *control*, not another misinformation attack.
- The mock provider runs the pipeline but **never measures LLM reliability**.
- Token counts do not replace counterbalancing instruction order or repeating
  trials across seeds. Those are separate planned interventions.

The CLI explicitly fails rather than silently falling back to word counts
when no tokenizer is available.
