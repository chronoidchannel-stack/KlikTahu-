import json
import tempfile
import unittest
from pathlib import Path

from tools.resolve_video import resolve_video


def make_source(root: Path, container: str, key: str, title: str, engine: str) -> Path:
    source = root / container / key
    source.mkdir(parents=True)
    (source / "config.env").write_text("FPS=30\n", encoding="utf-8")
    (source / "content.json").write_text(
        json.dumps({"title": title, "mesin": engine, "scenes": []}),
        encoding="utf-8",
    )
    return source


class ResolveVideoTests(unittest.TestCase):
    def test_title_slug_resolves_short_while_keeping_legacy_source_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = make_source(
                root,
                "episodes",
                "ep49_bintang",
                "Kenapa Bintang Berkedip, Tapi Planet Tidak?",
                "v11",
            )
            self.assertEqual(
                resolve_video(
                    "kenapa-bintang-berkedip-tapi-planet-tidak", "shorts", root
                ),
                source,
            )

    def test_long_title_slug_and_legacy_alias_resolve(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = make_source(
                root,
                "long",
                "v02_laut_dalam",
                "Perjalanan ke Dasar Laut Terdalam di Bumi",
                "long16x9",
            )
            self.assertEqual(
                resolve_video(
                    "perjalanan-ke-dasar-laut-terdalam-di-bumi", "long", root
                ),
                source,
            )
            self.assertEqual(resolve_video("v02_laut_dalam", "long", root), source)

    def test_wrong_mode_and_path_traversal_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_source(root, "episodes", "short-key", "Contoh Video", "v11")
            with self.assertRaises(FileNotFoundError):
                resolve_video("contoh-video", "long", root)
            with self.assertRaisesRegex(ValueError, "bukan path"):
                resolve_video("../secret", "shorts", root)

    def test_duplicate_title_slug_requires_manual_resolution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            make_source(root, "episodes", "short-a", "Judul Sama", "v11")
            make_source(root, "videos", "short-b", "Judul Sama", "v11")
            with self.assertRaisesRegex(ValueError, "beberapa video"):
                resolve_video("judul-sama", "shorts", root)


if __name__ == "__main__":
    unittest.main()
