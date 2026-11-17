"""Evaluation traceability: malformed answers count as failures, not dropped runs."""
import hashlib
import json
import unittest
from unittest.mock import patch

from foresight_ai.dataset import Claim, Evidence
from foresight_ai.experiment import run_experiment
from foresight_ai.prompts import SYSTEM, make_prompt
from foresight_ai.providers import MockProvider, OllamaProvider
from foresight_ai.scenarios import make_scenario


class FakeOllamaResponse:
    def __init__(self, content: str):
        self.payload = json.dumps({"message": {"content": content}}).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self) -> bytes:
        return self.payload


class TraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.claim = Claim(
            "T1", "A fictional ferry permanently closes", "Refuted",
            (Evidence("E1", "It reopens on Monday."),),
        )

    def test_non_json_model_answer_becomes_invalid(self):
        provider = OllamaProvider()
        with patch("foresight_ai.providers.urlopen",
                   return_value=FakeOllamaResponse("Sorry, I cannot do JSON")):
            response = provider.predict(SYSTEM, "Test prompt")
        self.assertEqual(response["verdict"], "INVALID")
        self.assertIn("not valid JSON", response["rationale"])
        self.assertEqual(response["_raw_text"], "Sorry, I cannot do JSON")
        self.assertEqual(provider.temperature, 0.1)

    def test_json_array_model_answer_is_invalid(self):
        provider = OllamaProvider()
        with patch("foresight_ai.providers.urlopen",
                   return_value=FakeOllamaResponse('["Refuted"]')):
            response = provider.predict(SYSTEM, "Test prompt")
        self.assertEqual(response["verdict"], "INVALID")
        self.assertIn("not an object", response["rationale"])

    def test_valid_json_object_is_unchanged(self):
        provider = OllamaProvider()
        expected = {
            "verdict": "Refuted", "evidence_ids": ["E1"],
            "rationale": "Document supports rejection.",
        }
        with patch("foresight_ai.providers.urlopen",
                   return_value=FakeOllamaResponse(json.dumps(expected))):
            response = provider.predict(SYSTEM, "Test prompt")
        self.assertEqual(response, expected)

    def test_prompt_hash_matches_exact_input_text(self):
        report = run_experiment(
            [self.claim], MockProvider(), post_count=2,
            conditions=("evidence_only", "rumor_pressure"),
        )
        evidence_prompt = make_prompt(
            self.claim, make_scenario(self.claim, "evidence_only", 2),
        )
        expected = hashlib.sha256(
            (SYSTEM + "\n\n" + evidence_prompt).encode("utf-8")
        ).hexdigest()
        rows = report["rows"]
        self.assertEqual(rows[0]["prompt_sha256"], expected)
        self.assertNotEqual(rows[0]["prompt_sha256"], rows[1]["prompt_sha256"])
        self.assertIsNone(rows[0]["invalid_response_excerpt"])

    def test_invalid_model_responses_are_included_in_metrics(self):
        class InvalidProvider:
            def predict(self, system: str, prompt: str) -> dict:
                return {
                    "verdict": "INVALID", "evidence_ids": [],
                    "rationale": "Model answered with text, not JSON.",
                    "_raw_text": "plain text instead of JSON",
                }

        report = run_experiment(
            [self.claim], InvalidProvider(), post_count=2,
            conditions=("evidence_only", "rumor_pressure"),
            provider_name="ollama", model_name="test-fake-local-provider",
        )
        self.assertEqual(len(report["rows"]), 2)
        self.assertEqual(report["metrics"]["rumor_pressure"]["invalid_output_rate"], 1.0)
        self.assertEqual(
            report["rows"][0]["invalid_response_excerpt"],
            "plain text instead of JSON",
        )
        self.assertEqual(
            report["paired_inference"]["rumor_pressure"]["paired_claims"], 0
        )


if __name__ == "__main__":
    unittest.main()
