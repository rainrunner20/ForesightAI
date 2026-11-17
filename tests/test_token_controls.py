"""Regression tests for text length controls. No model download is needed."""
import unittest

from foresight_ai.dataset import Claim, Evidence
from foresight_ai.experiment import run_experiment
from foresight_ai.prompts import SYSTEM, make_prompt
from foresight_ai.providers import MockProvider
from foresight_ai.scenarios import CONDITIONS, make_scenario
from foresight_ai.token_controls import make_neutral_length_control, token_count


class WordCounter:
    """Test double only; real token measurements require a matching tokenizer."""
    def count(self, text: str) -> int:
        return len(text.split())


class LengthControlTests(unittest.TestCase):
    def setUp(self):
        self.claim = Claim(
            "C1", "The fictional train line permanently closes", "Refuted",
            (Evidence("E1", "The transit authority says service resumes Tuesday."),),
        )
        self.counter = WordCounter()

    def test_neutral_context_is_matched_without_gold_label(self):
        rumor = make_scenario(self.claim, "rumor_pressure", 5)
        neutral, target, actual = make_neutral_length_control(
            self.claim, rumor, self.counter,
        )
        self.assertEqual(neutral.post_count, rumor.post_count)
        self.assertLessEqual(abs(target - actual), 1)
        self.assertEqual(
            actual, token_count(SYSTEM, make_prompt(self.claim, neutral), self.counter)
        )
        for post in neutral.social_posts:
            self.assertNotIn(self.claim.text, post)
            self.assertNotIn(self.claim.gold_verdict, post)
            self.assertNotIn("TRUE", post)
            self.assertNotIn("FALSE", post)

    def test_opt_in_control_records_the_token_gap(self):
        report = run_experiment(
            [self.claim], MockProvider(), post_count=4,
            conditions=("evidence_only", "rumor_pressure", "neutral_length_control"),
            token_counter=self.counter, tokenizer_name="test-only-word-counter",
        )
        self.assertEqual(len(report["rows"]), 3)
        rumor = report["rows"][1]
        neutral = report["rows"][2]
        self.assertEqual(rumor["prompt_tokens"], neutral["neutral_target_tokens"])
        self.assertLessEqual(abs(neutral["token_gap_vs_rumor"]), 1)
        self.assertEqual(report["metadata"]["tokenizer"], "test-only-word-counter")
        self.assertEqual(report["metadata"]["synthetic_demo"], True)

    def test_control_requires_tokenizer_and_paired_rumor(self):
        with self.assertRaisesRegex(ValueError, "real tokenizer"):
            run_experiment(
                [self.claim], MockProvider(), 2,
                conditions=("rumor_pressure", "neutral_length_control"),
            )
        with self.assertRaisesRegex(ValueError, "requires rumor_pressure"):
            run_experiment(
                [self.claim], MockProvider(), 2,
                conditions=("neutral_length_control",),
                token_counter=self.counter,
            )

    def test_default_conditions_unchanged(self):
        self.assertEqual(len(CONDITIONS), 7)
        report = run_experiment([self.claim], MockProvider(), post_count=2)
        self.assertEqual(len(report["rows"]), 7)
        self.assertIsNone(report["rows"][0]["prompt_tokens"])


if __name__ == "__main__":
    unittest.main()
