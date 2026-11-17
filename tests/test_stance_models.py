"""Check the trained TF-IDF research path on fabricated text only."""
import importlib.util
import tempfile
import unittest

from foresight_ai.stance_data import StanceExample, validate_split_isolation
from foresight_ai.stance_models import run_tfidf, score_stance


def fixtures(prefix: str, copies: int = 1) -> list[StanceExample]:
    phrases = (
        ("I agree that this happened", "support"),
        ("That story is false", "deny"),
        ("Is there any proof of this", "query"),
        ("Interesting discussion on this topic", "comment"),
    )
    examples = []
    for copy in range(copies):
        for label, (reply, _) in enumerate(phrases):
            name = f"{prefix}-{copy}-{label}"
            examples.append(StanceExample(
                name, f"Synthetic rumor topic {name}", reply, label,
            ))
    return examples


@unittest.skipUnless(importlib.util.find_spec("sklearn") is not None,
                     "scikit-learn is optional; dedicated CI job installs it")
class StanceTrainingTests(unittest.TestCase):
    def test_scorer_includes_all_four_classes(self):
        result = score_stance([0, 1, 2, 3], [0, 1, 2, 3])
        self.assertEqual(result["macro_f1"], 1.0)
        self.assertEqual(result["macro_f1_sdq"], 1.0)
        self.assertEqual(len(result["confusion_matrix"]), 4)

    def test_tfidf_pipeline_creates_report_and_local_artifact(self):
        train, dev, test = fixtures("train", 3), fixtures("dev"), fixtures("test")
        validate_split_isolation(train, dev, test)
        with tempfile.TemporaryDirectory() as tmp:
            report = run_tfidf(train, dev, test, output_dir=tmp)
            self.assertEqual(report["backend"], "tfidf_logistic_regression")
            self.assertEqual(report["test_size"], 4)
            self.assertEqual(len(report["test_predictions"]), 4)
            self.assertIn("macro_f1", report["test_metrics"])
            self.assertIn("comment", report["test_metrics"]["per_class"])
            from pathlib import Path
            self.assertTrue((Path(tmp) / "tfidf_model.joblib").exists())


if __name__ == "__main__":
    unittest.main()
