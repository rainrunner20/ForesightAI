"""Regressions for real AVeriTeC data fidelity and sample selection."""
import json
import tempfile
from pathlib import Path
import unittest

from foresight_ai.dataset import load_claims
from foresight_ai.prepare_averitec import make_pilot, main


def record(label: str, ident: int, *, answers: bool = True) -> dict:
    return {
        "claim": f"A fictional public-service claim number {ident}.",
        "label": label,
        "questions": [
            {"question": "Was the service restored?", "answers": (
                [
                    {
                        "answer": "No", "answer_type": "Boolean",
                        "boolean_explanation": "Only temporary maintenance.",
                        "source_url": "https://example.org/evidence",
                    },
                    {"answer": "No answer could be found.",
                     "answer_type": "Unanswerable"},
                ] if answers else [
                    {"answer": "No answer could be found.",
                     "answer_type": "Unanswerable"},
                ]
            )},
        ],
    }


class RealDataTests(unittest.TestCase):
    def test_question_boolean_context_and_source_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.json"
            path.write_text(json.dumps([record("Refuted", 1)]), encoding="utf-8")
            claims = load_claims(path)
        evidence = claims[0].evidence
        self.assertEqual(len(evidence), 1)
        self.assertIn("Question: Was the service restored?", evidence[0].text)
        self.assertIn("Answer: No", evidence[0].text)
        self.assertIn("Explanation: Only temporary maintenance.", evidence[0].text)
        self.assertEqual(evidence[0].source_url, "https://example.org/evidence")

    def test_official_cherrypicking_variant_normalized(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.json"
            path.write_text(json.dumps([
                record("Conflicting Evidence/Cherrypicking", 1)
            ]), encoding="utf-8")
            claim = load_claims(path)[0]
        self.assertEqual(claim.gold_verdict, "Conflicting Evidence/Cherry-picking")

    def test_pilot_balances_binary_labels_and_records_provenance(self):
        raw = (
            [record("Supported", n) for n in range(8)]
            + [record("Refuted", n + 8) for n in range(8)]
            + [record("Not Enough Evidence", 55)]
            + [record("Conflicting Evidence/Cherrypicking", 56)]
            + [record("Refuted", 57, answers=False)]
        )
        a, manifest_a = make_pilot(raw, split="train", per_label=3, seed=19)
        b, manifest_b = make_pilot(raw, split="train", per_label=3, seed=19)
        self.assertEqual(a, b)
        self.assertEqual(manifest_a, manifest_b)
        self.assertEqual(len(a), 6)
        self.assertEqual(set(manifest_a["selected_labels"]), {"Supported", "Refuted"})
        self.assertEqual(manifest_a["selected_labels"]["Supported"], 3)
        self.assertEqual(manifest_a["selected_labels"]["Refuted"], 3)
        self.assertEqual(manifest_a["excluded"]["non_binary_label"], 2)
        self.assertEqual(manifest_a["excluded"]["no_usable_question_answers"], 1)
        self.assertTrue(all(x["id"].startswith("averitec-train-") for x in a))

    def test_source_not_overwritten_and_generated_files_are_loadable(self):
        raw = [record("Supported", n) for n in range(3)] + [
            record("Refuted", n + 3) for n in range(3)
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "train.json"
            output = Path(directory) / "pilot.json"
            manifest = Path(directory) / "manifest.json"
            source.write_text(json.dumps(raw), encoding="utf-8")
            self.assertEqual(
                main([
                    "--input", str(source), "--split", "train",
                    "--per-label", "2", "--seed", "99",
                    "--output", str(output), "--manifest", str(manifest),
                ]), 0,
            )
            self.assertEqual(len(load_claims(output)), 4)
            self.assertEqual(json.loads(source.read_text()), raw)
            self.assertEqual(
                json.loads(manifest.read_text())["selected_count"], 4
            )

    def test_rejects_missing_class_and_unsupported_split(self):
        with self.assertRaisesRegex(ValueError, "Not enough eligible"):
            make_pilot(
                [record("Supported", 1)], split="train", per_label=1
            )
        with self.assertRaises(ValueError):
            make_pilot([], split="blind_test", per_label=1)


if __name__ == "__main__":
    unittest.main()
