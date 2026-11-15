import unittest
from foresight_ai.dataset import Claim, Evidence
from foresight_ai.experiment import run_experiment
from foresight_ai.providers import MockProvider, parse_prediction
from foresight_ai.prompts import make_prompt
from foresight_ai.scenarios import make_scenario


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.case = Claim("1", "A fictional service closes permanently", "Refuted", (Evidence("E1", "Only a weekend closure"),))

    def test_prompt_does_not_leak_gold_verdict(self):
        scenario = make_scenario(self.case, "evidence_first", 2)
        self.assertNotIn("gold", make_prompt(self.case, scenario).lower())
        self.assertIn("[E1]", make_prompt(self.case, scenario))

    def test_paired_conditions(self):
        report = run_experiment([self.case], MockProvider(), 4)
        self.assertEqual(len(report["rows"]), 3)
        self.assertEqual(report["metadata"]["synthetic_demo"], True)
        self.assertEqual(report["metrics"]["evidence_only"]["samples"], 1)
        self.assertEqual(report["rows"][0]["social_posts"], 0)

    def test_invalid_model_verdict(self):
        self.assertEqual(parse_prediction({"verdict": "Definitely"})["verdict"], "INVALID")

    def test_repetition_range(self):
        with self.assertRaises(ValueError):
            make_scenario(self.case, "rumor_pressure", 101)


class MetricsTests(unittest.TestCase):
    def test_missing_citations_are_not_perfect_validity(self):
        from foresight_ai.metrics import summarize
        row = {"claim_id": "1", "condition": "evidence_only", "predicted": "Refuted",
               "gold": "Refuted", "evidence_ids": [], "available_evidence_ids": ["E1"]}
        result = summarize([row])["evidence_only"]
        self.assertIsNone(result["citation_id_validity"])
        self.assertEqual(result["citation_coverage"], 0)

    def test_invalid_citation_is_counted(self):
        from foresight_ai.metrics import summarize
        row = {"claim_id": "1", "condition": "evidence_only", "predicted": "Refuted",
               "gold": "Refuted", "evidence_ids": ["E1", "E9"], "available_evidence_ids": ["E1"]}
        self.assertEqual(summarize([row])["evidence_only"]["citation_id_validity"], 0.5)
