import json
import tempfile
import unittest
from pathlib import Path

from tools.video_names import title_from_content, title_slug


class VideoNamesTests(unittest.TestCase):
    def test_public_name_comes_from_actual_video_title(self):
        self.assertEqual(
            title_slug("Kenapa Bintang Berkedip, Tapi Planet Tidak?"),
            "kenapa-bintang-berkedip-tapi-planet-tidak",
        )
        self.assertEqual(
            title_slug("Perjalanan ke Dasar Laut Terdalam di Bumi"),
            "perjalanan-ke-dasar-laut-terdalam-di-bumi",
        )

    def test_title_slug_sanitizes_unicode_and_unsafe_characters(self):
        self.assertEqual(
            title_slug("Kenapa Ular Masuk Rumah? — 2 Cara Aman"),
            "kenapa-ular-masuk-rumah-2-cara-aman",
        )
        self.assertNotIn("/", title_slug("Apa? Ini: Ular/Rumah!"))

    def test_empty_titles_are_rejected(self):
        for value in ("", "   ", "?!—"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    title_slug(value)

    def test_content_title_is_read_without_any_episode_id(self):
        with tempfile.TemporaryDirectory() as temporary:
            content_path = Path(temporary) / "content.json"
            content_path.write_text(
                json.dumps({"title": "Kenapa Ular Masuk Rumah?", "scenes": []}),
                encoding="utf-8",
            )
            self.assertEqual(title_from_content(content_path), "Kenapa Ular Masuk Rumah?")


if __name__ == "__main__":
    unittest.main()
