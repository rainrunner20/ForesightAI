"""Small synthetic fixtures to check stance data contracts without datasets."""
import json
import tempfile
from pathlib import Path
import unittest

from foresight_ai.stance_data import (
    LABELS, StanceExample, load_stance_split, normalize_label,
    validate_split_isolation,
)


class StanceDataTests(unittest.TestCase):
    def test_numeric_and_string_labels_match_rumoureval_tagset(self):
        self.assertEqual(LABELS, ("support", "deny", "query", "comment"))
        for i, value in enumerate(LABELS):
            self.assertEqual(normalize_label(i), i)
            self.assertEqual(normalize_label(str(i)), i)
            self.assertEqual(normalize_label(value.upper()), i)
        with self.assertRaises(ValueError):
            normalize_label("misinformation")

    def test_csv_and_jsonl_source_reply_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_file = Path(tmp) / "stance.csv"
            csv_file.write_text(
                "id,source_text,reply_text,label,thread_id\n"
                "p1,Fictional ferry closes,That is untrue,deny,thread7\n",
                encoding="utf-8",
            )
            rows = load_stance_split(csv_file)
            self.assertEqual(rows[0].label, 1)
            self.assertEqual(rows[0].thread_id, "thread7")
            self.assertIn("[REPLY]", rows[0].input_text)
            jsonl_file = Path(tmp) / "stance.jsonl"
            jsonl_file.write_text(
                json.dumps({
                    "id": "p2", "source_text": "Fictional bus changes",
                    "reply_text": "Where is the evidence?", "label": 2,
                }) + "\n", encoding="utf-8",
            )
            self.assertEqual(load_stance_split(jsonl_file)[0].label, 2)

    def test_missing_text_or_unknown_label_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "bad.json"
            file.write_text(json.dumps([
                {"source_text": "An event", "reply_text": "", "label": 3}
            ]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source_text and reply_text"):
                load_stance_split(file)

    def test_thread_leakage_is_rejected(self):
        def record(name, label=0, thread=""):
            return StanceExample(name, name, "Reply", label, thread)
        train = [record(f"train-{i}", i) for i in range(4)]
        dev = [record("same-source", 0, "thread1")]
        test = [record("same-source", 1, "thread2")]
        with self.assertRaisesRegex(ValueError, "leakage"):
            validate_split_isolation(train, dev, test)

    def test_label_balance_checked_after_isolation(self):
        train = [StanceExample("a", "Source A", "reply", 0)]
        dev = [StanceExample("b", "Source B", "reply", 1)]
        test = [StanceExample("c", "Source C", "reply", 2)]
        with self.assertRaisesRegex(ValueError, "four stance classes"):
            validate_split_isolation(train, dev, test)


if __name__ == "__main__":
    unittest.main()
