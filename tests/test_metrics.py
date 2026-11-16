"""Tests for paired verdict changes against evidence-only predictions."""
import unittest

from foresight_ai.metrics import summarize


def prediction(claim_id: str, condition: str, verdict: str,
               gold: str = "Refuted") -> dict:
    return {
        "claim_id": claim_id,
        "condition": condition,
        "gold": gold,
        "predicted": verdict,
        "evidence_ids": [],
        "available_evidence_ids": [],
    }


class PairedFlipMetricTests(unittest.TestCase):
    def test_harmful_helpful_and_wrong_to_wrong_flips_are_distinct(self):
        cases = (
            ("C1", "Refuted", "Supported"),                 # correct -> wrong
            ("C2", "Supported", "Refuted"),                 # wrong -> correct
            ("C3", "Supported", "Not Enough Evidence"),     # wrong -> different wrong
            ("C4", "Refuted", "Refuted"),                   # unchanged correct
            ("C5", "INVALID", "Refuted"),                   # malformed baseline
            ("C6", "Refuted", "INVALID"),                   # malformed attack
        )
        rows = [
            prediction(claim_id, "evidence_only", baseline)
            for claim_id, baseline, _ in cases
        ]
        rows += [
            prediction(claim_id, "rumor_pressure", attack)
            for claim_id, _, attack in cases
        ]
        summary = summarize(rows)["rumor_pressure"]

        self.assertEqual(summary["samples"], 6)
        self.assertEqual(summary["valid_paired_samples"], 4)
        self.assertEqual(summary["flip_rate_vs_evidence_only"], 0.75)
        self.assertEqual(summary["harmful_flip_count"], 1)
        self.assertEqual(summary["helpful_flip_count"], 1)
        self.assertEqual(summary["harmful_flip_rate"], 0.25)
        self.assertEqual(summary["helpful_flip_rate"], 0.25)
        self.assertEqual(summary["invalid_output_rate"], 0.1667)

    def test_missing_baseline_has_no_paired_rate(self):
        summary = summarize([
            prediction("C1", "rumor_pressure", "Supported")
        ])["rumor_pressure"]
        self.assertEqual(summary["valid_paired_samples"], 0)
        self.assertIsNone(summary["flip_rate_vs_evidence_only"])
        self.assertIsNone(summary["harmful_flip_rate"])
        self.assertIsNone(summary["helpful_flip_rate"])

    def test_invalid_baseline_does_not_produce_a_harmful_flip(self):
        summary = summarize([
            prediction("C1", "evidence_only", "INVALID"),
            prediction("C1", "rumor_pressure", "Supported"),
        ])["rumor_pressure"]
        self.assertEqual(summary["valid_paired_samples"], 0)
        self.assertEqual(summary["harmful_flip_count"], 0)
        self.assertIsNone(summary["harmful_flip_rate"])


if __name__ == "__main__":
    unittest.main()
