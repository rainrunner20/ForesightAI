import json
import tempfile
from pathlib import Path
import unittest
from foresight_ai.dataset import load_claims


class DatasetTests(unittest.TestCase):
    def test_averitec_questions_and_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claims.json"
            path.write_text(json.dumps([{"claim": "An example", "label": "Refuted",
                "questions": [{"answers": [{"answer": "Document text", "source_url": "https://example.org"}]}]}]))
            cases = load_claims(path)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].evidence[0].id, "E1")
        self.assertEqual(cases[0].evidence[0].source_url, "https://example.org")

    def test_reject_unknown_gold_label(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claims.json"
            path.write_text('[{"claim": "test", "label": "Something else"}]')
            with self.assertRaises(ValueError):
                load_claims(path)
