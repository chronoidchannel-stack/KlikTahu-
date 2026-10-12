import tempfile
import unittest
from pathlib import Path

from tools.check_repo_hygiene import audit


class RepoHygieneMediaTests(unittest.TestCase):
    def test_audio_and_video_exports_are_forbidden_from_git_candidates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for name in ("voice.mp3", "voice.wav", "mix.m4a", "final.mp4"):
                path = root / name
                path.write_bytes(b"media")
                paths.append(path)
            errors = audit(paths)
            self.assertEqual(len(errors), 4)
            self.assertTrue(all("media" in error for error in errors))

    def test_audio_raw_folder_is_forbidden_even_for_unknown_extension(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "audio_raw" / "readme.txt"
            path.parent.mkdir()
            path.write_text("local asset", encoding="utf-8")
            errors = audit([path])
            self.assertEqual(len(errors), 1)
            self.assertIn("audio_raw", errors[0])


if __name__ == "__main__":
    unittest.main()
