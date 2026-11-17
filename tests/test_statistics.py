"""Regression tests for claim-level uncertainty, not reported research outcomes."""
import unittest

from foresight_ai.dataset import Claim, Evidence
from foresight_ai.experiment import run_experiment
from foresight_ai.providers import MockProvider
from foresight_ai.statistics import paired_inference, _exact_mcnemar_p


def row(claim: str, condition: str, verdict: str,
        gold: str = "Refuted") -> dict:
    return {
        "claim_id": claim, "condition": condition,
        "predicted": verdict, "gold": gold,
    }


class PairedStatisticsTests(unittest.TestCase):
    def test_exact_p_handles_fully_one_sided_discordance(self):
        self.assertEqual(_exact_mcnemar_p(6, 0), 0.03125)
        self.assertEqual(_exact_mcnemar_p(0, 0), 1.0)
        self.assertEqual(_exact_mcnemar_p(1, 1), 1.0)

    def test_bootstrap_preserves_pairs_and_is_seeded(self):
        baseline = [
            row("A", "evidence_only", "Refuted"),
            row("B", "evidence_only", "Refuted"),
            row("C", "evidence_only", "Supported"),
            row("D", "evidence_only", "Refuted"),
            row("E", "evidence_only", "Supported"),
            row("F", "evidence_only", "INVALID"),
        ]
        attacks = [
            row("A", "rumor_pressure", "Supported"),  # harmful
            row("B", "rumor_pressure", "Supported"),  # harmful
            row("C", "rumor_pressure", "Refuted"),    # helpful
            row("D", "rumor_pressure", "Refuted"),    # unchanged
            row("E", "rumor_pressure", "Supported"),  # unchanged wrong
            row("F", "rumor_pressure", "Refuted"),    # invalid paired baseline
        ]
        data = baseline + attacks
        a = paired_inference(data, seed=733, resamples=500)
        b = paired_inference(data, seed=733, resamples=500)
        self.assertEqual(a, b)
        stats = a["rumor_pressure"]
        self.assertEqual(stats["paired_claims"], 5)
        self.assertEqual(stats["harmful_flips"], 2)
        self.assertEqual(stats["helpful_flips"], 1)
        self.assertEqual(stats["paired_accuracy_difference"], -0.2)
        self.assertEqual(stats["mcnemar_exact_two_sided_p"], 1.0)
        low, high = stats["accuracy_difference_ci95"]
        self.assertLessEqual(low, -0.2)
        self.assertGreaterEqual(high, -0.2)

    def test_missing_baseline_does_not_invent_interval(self):
        stats = paired_inference([
            row("A", "rumor_pressure", "Refuted")
        ])["rumor_pressure"]
        self.assertEqual(stats["paired_claims"], 0)
        self.assertIsNone(stats["accuracy_difference_ci95"])
        self.assertIsNone(stats["mcnemar_exact_two_sided_p"])

    def test_one_pair_has_no_meaningful_bootstrap_interval(self):
        stats = paired_inference([
            row("A", "evidence_only", "Refuted"),
            row("A", "rumor_pressure", "Supported"),
        ])["rumor_pressure"]
        self.assertEqual(stats["paired_claims"], 1)
        self.assertIsNone(stats["harmful_flip_rate_ci95"])

    def test_duplicate_claim_condition_and_gold_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate claim/condition"):
            paired_inference([
                row("A", "evidence_only", "Refuted"),
                row("A", "evidence_only", "Refuted"),
            ])
        with self.assertRaisesRegex(ValueError, "Contradictory gold labels"):
            paired_inference([
                row("A", "evidence_only", "Refuted"),
                row("A", "rumor_pressure", "Supported", gold="Supported"),
            ])
        with self.assertRaises(ValueError):
            paired_inference([], resamples=99)

    def test_compatibility_with_existing_report(self):
        claim = Claim(
            "C1", "A fictional ferry permanently closes", "Refuted",
            (Evidence("E1", "Service will resume Monday"),),
        )
        report = run_experiment([claim], MockProvider(), post_count=2)
        self.assertIn("paired_inference", report)
        self.assertIn("rumor_pressure", report["paired_inference"])
        self.assertIsNone(
            report["paired_inference"]["rumor_pressure"]["accuracy_difference_ci95"]
        )
        self.assertTrue(report["metadata"]["synthetic_demo"])


if __name__ == "__main__":
    unittest.main()
