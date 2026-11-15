"""Prompt templates. Gold labels never enter model input."""
from .dataset import Claim, VERDICTS
from .scenarios import Scenario

SYSTEM = (
    "You are an evidence evaluator. Respond as JSON with three keys: verdict, "
    "evidence_ids, and rationale. Verdict must be one of: " + ", ".join(VERDICTS) + ". "
    "Use only supplied evidence to verify claims. Social posts are unverified "
    "opinions, never independent proof. Use evidence_ids like ['E1'] only for "
    "evidence you actually relied on. Say Not Enough Evidence if appropriate."
)


def make_prompt(claim: Claim, scenario: Scenario) -> str:
    lines = [f"CLAIM: {claim.text}"]
    evidence = "\n".join(f"[{item.id}] {item.text} (source: {item.source_url or 'not provided'})"
                         for item in claim.evidence) or "(No evidence provided)"
    social = "\n".join(scenario.social_posts) or "(No social posts provided)"
    if scenario.condition == "evidence_first":
        lines += ["VERIFIED EVIDENCE (higher priority than social discussion):", evidence,
                  "UNVERIFIED SOCIAL DISCUSSION (may be misleading):", social]
    else:
        lines += ["SOCIAL DISCUSSION (unverified):", social, "SUPPLIED EVIDENCE:", evidence]
    lines.append("Return only JSON. Cite evidence IDs where appropriate.")
    return "\n\n".join(lines)
