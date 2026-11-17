"""Manual evidence auditing is explicit, reproducible, and not an LLM judge."""
import csv
import hashlib
import json
import tempfile
from pathlib import Path
import unittest

from foresight_ai.dataset import Claim, Evidence
from foresight_ai.evidence_audit import (
    CSV_FIELDS, export_reviews, summarize_reviews,
)


def sample() -> tuple[dict, list[Claim]]:
    claims = [
        Claim(
            "C1", "=SUM(1,1) this fictional rumor", "Refuted",
            (
                Evidence("E1", "Question: Did the bus reopen?\nAnswer: Yes",
                         "https://example.org/transit"),
                Evidence("E2", "Second independent source", ""),
            ),
        ),
        Claim(
            "C2", "An unrelated fictional claim", "Supported",
            (Evidence("E1", "The fictional event happened."),),
        ),
    ]
    report = {
        "metadata": {"synthetic_demo": True},
        "rows": [
            {
                "claim_id": "C1", "condition": "evidence_only",
                "predicted": "Refuted", "evidence_ids": ["E1", "E99"],
                "rationale": "I used the first source.",
            },
            {
                "claim_id": "C1", "condition": "rumor_pressure",
                "predicted": "Supported", "evidence_ids": ["E2"],
                "rationale": "Changed judgment.",
            },
            {
                "claim_id": "C2", "condition": "evidence_only",
                "predicted": "Supported", "evidence_ids": ["E1"],
                "rationale": "Reported answer.",
            },
        ],
    }
    return report, claims


class EvidenceAuditTests(unittest.TestCase):
    def test_review_export_preserves_evidence_and_blinds_gold(self):
        report, claims = sample()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "reviews.csv"
            count = export_reviews(
                report, claims, report_sha256="sha1", output=output,
            )
            self.assertEqual(count, 3)
            with output.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["report_sha256"], "sha1")
            self.assertIn("[E1]", rows[0]["cited_evidence"])
            self.assertIn("Question: Did the bus reopen?", rows[0]["supplied_evidence"])
            self.assertIn("https://example.org/transit", rows[0]["cited_evidence"])
            self.assertEqual(rows[0]["invalid_cited_ids"], "E99")
            self.assertTrue(rows[0]["claim_text"].startswith("'="))
            self.assertEqual(rows[0]["support_label"], "")
            self.assertNotIn("gold", CSV_FIELDS)

    def test_unreviewed_does_not_count_as_unsupported(self):
        report, claims = sample()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "reviews.csv"
            export_reviews(report, claims, report_sha256="abc", output=output)
            with output.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            rows[0]["support_label"] = "supports"
            rows[0]["reviewer"] = "Reviewer A"
            rows[1]["support_label"] = "contradicts"
            rows[2]["support_label"] = ""
            with output.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            summary = summarize_reviews(
                report, report_sha256="abc", review_path=output,
            )
            a = summary["conditions"]["evidence_only"]
            self.assertEqual(a["rows"], 2)
            self.assertEqual(a["reviewed"], 1)
            self.assertEqual(a["unreviewed"], 1)
            self.assertEqual(a["assessed_verdicts"], 1)
            self.assertEqual(a["supported_fraction_of_assessed"], 1.0)
            b = summary["conditions"]["rumor_pressure"]
            self.assertEqual(b["contradicts"], 1)
            self.assertEqual(b["supported_fraction_of_assessed"], 0.0)
            self.assertTrue(summary["synthetic_demo"])

    def test_rejects_cross_run_review_file_and_unknown_labels(self):
        report, claims = sample()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "review.csv"
            export_reviews(report, claims, report_sha256="old-sha", output=output)
            with self.assertRaisesRegex(ValueError, "different model report"):
                summarize_reviews(report, report_sha256="new-sha", review_path=output)
            with output.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            rows[0]["support_label"] = "the verdict is true"
            with output.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "Unknown support label"):
                summarize_reviews(report, report_sha256="old-sha", review_path=output)

    def test_missing_source_and_duplicate_report_keys_rejected(self):
        report, claims = sample()
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "Missing source evidence"):
                export_reviews(
                    report, claims[:1], report_sha256="sha",
                    output=Path(folder) / "r.csv",
                )
            bad = dict(report)
            bad["rows"] = report["rows"] + [report["rows"][0]]
            with self.assertRaisesRegex(ValueError, "Duplicate claim-condition"):
                export_reviews(
                    bad, claims, report_sha256="sha",
                    output=Path(folder) / "r.csv",
                )

    def test_mock_report_hash_can_be_calculated_without_network(self):
        report, claims = sample()
        raw = json.dumps(report, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "review.csv"
            export_reviews(report, claims, report_sha256=digest, output=output)
            self.assertEqual(
                summarize_reviews(
                    report, report_sha256=digest, review_path=output,
                )["overall_rows"], 3,
            )


if __name__ == "__main__":
    unittest.main()
