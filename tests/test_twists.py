"""Regression tests for extension experiments and synthetic simulation."""
import unittest
from foresight_ai.dataset import Claim, Evidence
from foresight_ai.diffusion import simulate_network
from foresight_ai.experiment import run_experiment
from foresight_ai.metrics import summarize
from foresight_ai.prompts import make_prompt
from foresight_ai.scenarios import CONDITIONS, make_scenario


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.claim = Claim("C1", "The fictional ferry permanently closes", "Refuted",
                           (Evidence("E1", "The ferry reopens Monday."),))

    def test_all_seven_conditions_are_available(self):
        self.assertEqual(len(CONDITIONS), 7)

    def test_fake_authority_is_labeled_unverified(self):
        scenario = make_scenario(self.claim, "fake_authority", 4)
        self.assertEqual(scenario.post_count, 4)
        self.assertIn("no source or credentials", scenario.social_posts[0])
        self.assertIn("unverified", make_prompt(self.claim, scenario).lower())

    def test_mutation_changes_framing_not_underlying_claim(self):
        scenario = make_scenario(self.claim, "rumor_mutation", 8)
        self.assertEqual(len(set(scenario.social_posts)), 8)
        self.assertTrue(all(self.claim.text in p for p in scenario.social_posts))

    def test_evidence_rescue_mentions_previous_verdict_not_gold(self):
        scenario = make_scenario(self.claim, "evidence_rescue", 2)
        prompt = make_prompt(self.claim, scenario, prior_verdict="Supported")
        self.assertIn("previous model verdict was 'Supported'", prompt)
        self.assertNotIn("Refuted", prompt)

    def test_seeded_network_is_repeatable(self):
        a = simulate_network(seed=11, agent_count=40, fact_checker_ratio=.2)
        b = simulate_network(seed=11, agent_count=40, fact_checker_ratio=.2)
        self.assertEqual(a, b)
        self.assertEqual(a.frames[0]["exposed"], 3)
        self.assertEqual(a.frames[-1]["step"], 12)
        self.assertEqual(len(a.nodes), 40)
        self.assertTrue(all(u < v for u, v in a.links))

    def test_out_of_range_simulation_parameters_are_rejected(self):
        for settings in ({"agent_count": 1}, {"steps": 0},
                         {"fact_checker_ratio": 1.4}, {"homophily": -1}):
            with self.assertRaises(ValueError):
                simulate_network(**settings)


class CorrectionTests(unittest.TestCase):
    class ScriptedProvider:
        def __init__(self):
            self.i = 0

        def predict(self, system, prompt):
            self.i += 1
            # Evidence-only correct, rumor pressure wrong, rescue correct.
            verdict = "Supported" if "CORRECTION STEP:" not in prompt and self.i > 1 else "Refuted"
            return {"verdict": verdict, "evidence_ids": ["E1"], "rationale": "Scripted test"}

    def test_recovery_is_measured_only_when_prior_response_was_wrong(self):
        case = Claim("C2", "The fictional ferry closes forever", "Refuted",
                     (Evidence("E1", "Reopens Monday"),))
        report = run_experiment([case], self.ScriptedProvider(), 2,
                                conditions=("evidence_only", "rumor_pressure", "evidence_rescue"))
        self.assertEqual(report["metrics"]["evidence_rescue"]["prior_error_count"], 1)
        self.assertEqual(report["metrics"]["evidence_rescue"]["recovery_rate_on_prior_error"], 1.0)
        self.assertEqual(report["rows"][-1]["prior_predicted"], "Supported")

    def test_rescue_requires_a_rumor_run(self):
        case = Claim("C3", "Invented", "Refuted", ())
        with self.assertRaisesRegex(ValueError, "requires rumor_pressure"):
            run_experiment([case], self.ScriptedProvider(), 2,
                           conditions=("evidence_rescue",))

    def test_flip_metric_is_null_without_evidence_baseline(self):
        row = {"claim_id": "C3", "condition": "fake_authority", "predicted": "Supported",
               "gold": "Refuted", "evidence_ids": [], "available_evidence_ids": []}
        self.assertIsNone(summarize([row])["fake_authority"]["flip_rate_vs_evidence_only"])


if __name__ == "__main__":
    unittest.main()
