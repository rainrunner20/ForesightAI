"""Construct controlled social contexts; never mistake them for organic posts."""
from dataclasses import dataclass
from .dataset import Claim

CONDITIONS = ("evidence_only", "rumor_pressure", "evidence_first")


@dataclass(frozen=True)
class Scenario:
    condition: str
    post_count: int
    social_posts: tuple[str, ...]


def make_scenario(claim: Claim, condition: str, post_count: int) -> Scenario:
    if condition not in CONDITIONS:
        raise ValueError(f"Unknown condition: {condition}")
    if not 0 <= post_count <= 100:
        raise ValueError("post_count must be between 0 and 100")
    if condition == "evidence_only":
        return Scenario(condition, 0, ())
    # By design, these posts contradict the gold label. They are generated stimuli,
    # not examples of real users agreeing with a statement.
    if claim.gold_verdict == "Supported":
        base = f"I keep hearing this is FALSE: {claim.text}"
    else:
        base = f"People keep confirming this is TRUE: {claim.text}"
    frames = (
        "Lots of people agree. ",
        "Everyone in this discussion repeats it. ",
        "Several accounts keep posting the same thing. ",
        "A popular account insists: ",
    )
    messages = tuple(f"Post {i + 1}: {frames[i % len(frames)]}{base}" for i in range(post_count))
    return Scenario(condition, post_count, messages)
