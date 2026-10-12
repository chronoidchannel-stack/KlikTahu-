"""Keep the Long02 mapping statistic synchronized across narration, visual, and metadata."""
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_URL = (
    "https://seabed2030.org/2026/04/20/"
    "global-seabed-mapping-reaches-new-milestone-as-five-million-square-kilometres-added-in-a-year/"
)


class Long02CurrentFactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = json.loads(
            (ROOT / "long/v02_laut_dalam/content.json").read_text(encoding="utf-8")
        )
        cls.metadata = (ROOT / "long/v02_laut_dalam/METADATA.md").read_text(
            encoding="utf-8"
        )
        cls.visual = (ROOT / "long/v02_laut_dalam/visual.py").read_text(
            encoding="utf-8"
        )
        cls.outro = next(
            scene["vo"] for scene in cls.content["scenes"]
            if scene.get("visual") == "v02_naik"
        )

    def test_latest_official_source_is_cited(self):
        self.assertIn(DATA_URL, self.metadata)
        self.assertIn("per April 2026, 28,7%", self.metadata)

    def test_narration_uses_modern_mapping_coverage_not_old_quarter_stat(self):
        outro = self.outro.casefold()
        self.assertIn("dua puluh delapan koma tujuh persen", outro)
        self.assertIn("lebih dari tujuh puluh satu persen", outro)
        self.assertNotIn("seperempat", outro)

    def test_visual_numbers_and_word_anchors_match_narration(self):
        self.assertIn('C.tt("dua puluh delapan koma tujuh"', self.visual)
        self.assertIn('C.tt("lebih dari tujuh puluh satu"', self.visual)
        self.assertIn("28.7, ts", self.visual)
        self.assertIn('"71,3%"', self.visual)
        self.assertNotIn('C.tt("seperempat"', self.visual)


if __name__ == "__main__":
    unittest.main()
