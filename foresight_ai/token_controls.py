"""Tokenizer-aware audits and a neutral-length control for the same claim."""
from typing import Protocol

from .dataset import Claim
from .prompts import SYSTEM, make_prompt
from .scenarios import Scenario


class TokenCounter(Protocol):
    def count(self, text: str) -> int: ...


class HuggingFaceTokenCounter:
    """Use an explicitly selected tokenizer; never silently approximate with words."""

    def __init__(self, model_id: str, *, allow_download: bool = False):
        try:
            from transformers import AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                'Tokenizer support is optional. Install: pip install ".[tokenization]"'
            ) from exc
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                local_files_only=not allow_download,
                trust_remote_code=False,
            )
        except (OSError, ValueError) as exc:
            raise RuntimeError(
                f"Could not load tokenizer {model_id!r}. Cache it first or use "
                "--allow-tokenizer-download after checking model provenance."
            ) from exc
        self.model_id = model_id

    def count(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))


def token_count(system: str, prompt: str, counter: TokenCounter) -> int:
    """Count concatenated system/user text; NOT Ollama's full chat template."""
    return counter.count(system + "\n\n" + prompt)


def make_neutral_length_control(
    claim: Claim, reference: Scenario, counter: TokenCounter,
    *, tolerance: int = 1,
) -> tuple[Scenario, int, int]:
    """Match the rumor prompt length using claim-agnostic neutral filler.

    This controls approximate input token count, not semantic or positional
    equivalence. It must never be mistaken for organically collected posts.
    """
    if reference.condition != "rumor_pressure":
        raise ValueError("Neutral control must be paired with rumor_pressure")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    target = token_count(SYSTEM, make_prompt(claim, reference), counter)

    # Keep post count and the evidence/prompt layout fixed. Neutral filler
    # avoids assertions about the claim and does not contain the gold verdict.
    messages = [f"Synthetic post {i + 1}: Routine update." for i in range(reference.post_count)]
    scenario = Scenario("neutral_length_control", len(messages), tuple(messages))
    actual = token_count(SYSTEM, make_prompt(claim, scenario), counter)
    if not messages and abs(target - actual) <= tolerance:
        return scenario, target, actual
    if actual > target + tolerance:
        raise ValueError("Neutral template is already longer than rumor prompt")

    # Adding neutral text in round-robin order avoids a single giant filler
    # post. Measure after every edit rather than assuming one word = one token.
    attempts = max(100, target * 4)
    for index in range(attempts):
        if abs(target - actual) <= tolerance:
            return scenario, target, actual
        if actual > target:
            break
        if not messages:
            break
        slot = index % len(messages)
        messages[slot] += " background"
        scenario = Scenario("neutral_length_control", len(messages), tuple(messages))
        actual = token_count(SYSTEM, make_prompt(claim, scenario), counter)
    if abs(target - actual) > tolerance:
        raise ValueError(
            f"Could not create a neutral control within {tolerance} tokens: "
            f"target={target}, actual={actual}"
        )
    return scenario, target, actual
