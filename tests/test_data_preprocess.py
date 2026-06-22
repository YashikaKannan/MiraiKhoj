from __future__ import annotations

import unittest
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from data.preprocess import build_candidate_text, clean_candidate_text, normalize_whitespace, split_candidate_text


class PreprocessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_path = Path(r"D:\MiraiKhoj\data\raw\sample_candidates.json")
        import json

        self.sample_records = json.loads(self.sample_path.read_text(encoding="utf-8"))

    def test_normalize_whitespace(self) -> None:
        self.assertEqual(normalize_whitespace("  a   b \n c  "), "a b c")

    def test_split_candidate_text(self) -> None:
        text = "Headline: A\nSummary: B\nSkills: C"
        self.assertEqual(split_candidate_text(text), ["Headline: A", "Summary: B", "Skills: C"])

    def test_build_candidate_text_uses_actual_fields(self) -> None:
        text = build_candidate_text(self.sample_records[0])
        self.assertIn("Headline:", text)
        self.assertIn("Career History:", text)
        self.assertIn("Skills:", text)
        self.assertNotIn("current_title", text)
        self.assertNotIn("current_company", text)

    def test_clean_candidate_text(self) -> None:
        self.assertEqual(clean_candidate_text("  Hello   world  "), "Hello world")


if __name__ == "__main__":
    unittest.main()
