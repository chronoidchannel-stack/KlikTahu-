from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.restore_audio import RestoreError, load_manifest, main, restore_archive

REPO_ROOT = Path(__file__).resolve().parents[1]


def fake_wav() -> bytes:
    return b"RIFF" + b"\x00\x00\x00\x00" + b"WAVE" + b"fmt " + b"\x00" * 16


class RestoreAudioTests(unittest.TestCase):
    def test_real_manifest_is_complete_and_unambiguous(self) -> None:
        manifest = load_manifest(REPO_ROOT / "docs" / "audio-manifest.md")
        self.assertEqual(len(manifest), 268)
        self.assertIn(("ep24_bulan_merah", "f1.wav"), manifest)
        self.assertIn(("v01_lubang_hitam", "b01.wav"), manifest)
        self.assertEqual(
            manifest[("ep24_bulan_merah", "f1.wav")],
            Path("episodes/ep24_bulan_merah/audio_raw/f1.wav"),
        )
        self.assertEqual(
            manifest[("v01_lubang_hitam", "b01.wav")],
            Path("long/v01_lubang_hitam/audio_raw/b01.wav"),
        )

    def _fixture(self, base: Path, names: tuple[str, ...] = ("f1.wav",)) -> tuple[Path, Path]:
        root = base / "repo"
        docs = root / "docs"
        episode = root / "episodes" / "ep24_bulan_merah"
        docs.mkdir(parents=True)
        episode.mkdir(parents=True)
        rows = [f"| `{name}` | 1 KB |" for name in names]
        manifest = "\n".join(
            [
                "# Manifest audio",
                "",
                f"## ep24_bulan_merah/audio_raw — {len(names)} berkas, 1.0 MiB",
                "",
                "| berkas | ukuran |",
                "|---|---:|",
                *rows,
                "",
            ]
        )
        (docs / "audio-manifest.md").write_text(manifest, encoding="utf-8")
        return root, episode

    def test_restores_only_manifest_wavs_and_is_repeatable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, episode = self._fixture(Path(temporary))
            archive_path = Path(temporary) / "kliktahu.zip"
            payload = fake_wav()
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("./backup/episodes/ep24_bulan_merah/audio_raw/f1.wav", payload)
                archive.writestr("backup/readme.txt", "ignored, not extracted")
                archive.writestr("backup/episodes/ep24_bulan_merah/audio_raw/extra.wav", payload)

            written, unchanged, total = restore_archive(archive_path, root)
            target = episode / "audio_raw" / "f1.wav"
            self.assertEqual((written, unchanged, total), (1, 0, 1))
            self.assertEqual(target.read_bytes(), payload)

            written, unchanged, total = restore_archive(archive_path, root)
            self.assertEqual((written, unchanged, total), (0, 1, 1))
            self.assertEqual(sorted(p.name for p in target.parent.iterdir()), ["f1.wav"])

    def test_incomplete_archive_fails_before_writing_anything(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, episode = self._fixture(Path(temporary), ("f1.wav", "f2.wav"))
            archive_path = Path(temporary) / "incomplete.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("ep24_bulan_merah/audio_raw/f1.wav", fake_wav())

            with self.assertRaisesRegex(RestoreError, "tidak lengkap"):
                restore_archive(archive_path, root)
            self.assertFalse((episode / "audio_raw").exists())

    def test_zip_slip_member_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, _ = self._fixture(Path(temporary))
            archive_path = Path(temporary) / "unsafe.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("ep24_bulan_merah/audio_raw/f1.wav", fake_wav())
                archive.writestr("../../outside.txt", "must never be extracted")

            with self.assertRaisesRegex(RestoreError, "path ZIP tidak aman"):
                restore_archive(archive_path, root)

    def test_overwrite_requires_explicit_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, episode = self._fixture(Path(temporary))
            archive_path = Path(temporary) / "audio.zip"
            payload = fake_wav()
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("ep24_bulan_merah/audio_raw/f1.wav", payload)
            target = episode / "audio_raw" / "f1.wav"
            target.parent.mkdir()
            target.write_bytes(fake_wav() + b"old")

            with self.assertRaisesRegex(RestoreError, "sudah ada dan berbeda"):
                restore_archive(archive_path, root)
            written, unchanged, total = restore_archive(archive_path, root, overwrite=True)
            self.assertEqual((written, unchanged, total), (1, 0, 1))
            self.assertEqual(target.read_bytes(), payload)

    def test_symlink_destination_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, episode = self._fixture(Path(temporary))
            archive_path = Path(temporary) / "audio.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("ep24_bulan_merah/audio_raw/f1.wav", fake_wav())
            elsewhere = episode / "elsewhere"
            elsewhere.mkdir()
            (episode / "audio_raw").symlink_to(elsewhere, target_is_directory=True)

            with self.assertRaisesRegex(RestoreError, "symlink"):
                restore_archive(archive_path, root)

    def test_legacy_restore_cli_is_blocked_without_explicit_opt_in(self) -> None:
        with redirect_stderr(StringIO()):
            self.assertEqual(main(["--dry-run"]), 3)


if __name__ == "__main__":

    unittest.main()
