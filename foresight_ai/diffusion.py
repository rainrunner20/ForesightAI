"""Seeded toy agent model for *controlled* social-context generation.

This is deliberately not a calibrated model of any real population. Agents,
network links, and sharing probabilities are invented experimental stimuli.
"""
from dataclasses import asdict, dataclass
import random


@dataclass(frozen=True)
class NetworkResult:
    seed: int
    agent_count: int
    fact_checker_ratio: float
    frames: tuple[dict, ...]
    nodes: tuple[dict, ...]
    links: tuple[tuple[int, int], ...]
    posts: tuple[str, ...]

    def to_dict(self) -> dict:
        result = asdict(self)
        result["kind"] = "synthetic_agent_model"
        return result


def simulate_network(*, seed: int = 733, agent_count: int = 120,
                     steps: int = 12, fact_checker_ratio: float = 0.15,
                     sharing_rate: float = 0.42, homophily: float = 0.55,
                     rumor_text: str = "An unverified claim is being repeated.") -> NetworkResult:
    """Spread a fictional rumor through a seeded small-world-ish network.

    Homophily biases edge selection toward agents with similar skepticism.
    The model is interpretable and deterministic, not fitted to human data.
    """
    if not 10 <= agent_count <= 500:
        raise ValueError("agent_count must be 10..500")
    if not 1 <= steps <= 50:
        raise ValueError("steps must be 1..50")
    for name, value in (("fact_checker_ratio", fact_checker_ratio),
                        ("sharing_rate", sharing_rate), ("homophily", homophily)):
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be within 0..1")

    rng = random.Random(seed)
    skepticism = [rng.random() for _ in range(agent_count)]
    checkers = set(rng.sample(range(agent_count), round(agent_count * fact_checker_ratio)))
    links: set[tuple[int, int]] = set()
    neighbors: list[set[int]] = [set() for _ in range(agent_count)]
    for source in range(agent_count):
        # Preserve a connected ring; add two plausible long-range contacts.
        candidates = [(source + 1) % agent_count]
        for _ in range(2):
            if rng.random() < homophily:
                pool = sorted(range(agent_count), key=lambda i: abs(skepticism[i] - skepticism[source]))[:max(5, agent_count // 5)]
                candidates.append(rng.choice(pool))
            else:
                candidates.append(rng.randrange(agent_count))
        for target in candidates:
            if target == source:
                continue
            a, b = sorted((source, target))
            links.add((a, b))
            neighbors[source].add(target)
            neighbors[target].add(source)

    # Only the first three non-fact-checkers are initially sharing.
    seeds = [i for i in range(agent_count) if i not in checkers][:3]
    spreaders = set(seeds)
    exposed = set(seeds)
    corrected = set()
    frames = []
    for step in range(steps + 1):
        frames.append({"step": step, "exposed": len(exposed),
                       "sharing": len(spreaders), "fact_checkers": len(checkers),
                       "corrected": len(corrected),
                       "exposed_ids": sorted(exposed),
                       "sharing_ids": sorted(spreaders),
                       "corrected_ids": sorted(corrected)})
        if step == steps:
            break
        next_spreaders = set()
        for source in sorted(spreaders):
            for target in sorted(neighbors[source]):
                if target in exposed:
                    continue
                exposed.add(target)
                if target in checkers:
                    corrected.add(target)
                    continue
                checker_neighbors = len(checkers.intersection(neighbors[target]))
                resistance = min(0.9, checker_neighbors * 0.2)
                chance = sharing_rate * (1 - 0.75 * skepticism[target]) * (1 - resistance)
                if rng.random() < chance:
                    next_spreaders.add(target)
        # A share gets one turn to travel; already-exposed agents do not respawn.
        spreaders = next_spreaders

    nodes = tuple({"id": i, "skepticism": round(skepticism[i], 3),
                   "fact_checker": i in checkers, "exposed": i in exposed,
                   "corrected": i in corrected} for i in range(agent_count))
    # Uniform sampling of synthetic messages. These posts are not empirical data.
    sample_count = min(25, len(exposed - checkers))
    posters = sorted(rng.sample(sorted(exposed - checkers), sample_count)) if sample_count else []
    posts = tuple(f"Synthetic agent {i}: {rumor_text}" for i in posters)
    return NetworkResult(seed, agent_count, fact_checker_ratio, tuple(frames),
                         nodes, tuple(sorted(links)), posts)
