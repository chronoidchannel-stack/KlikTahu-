#!/usr/bin/env python3
"""Keep generated media and oversized files out of the GitHub repository."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

MAX_FILE_BYTES = 50 * 1024 * 1024  # headroom below GitHub's per-file hard limit
MEDIA_SUFFIXES = {
    ".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus",
    ".aif", ".aiff", ".wma", ".amr", ".3gp", ".caf", ".au",
    ".mp4", ".mov", ".mkv", ".webm",
}
AUDIO_ARCHIVE_PREFIX = "kliktahu"


def candidate_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    paths = {
        Path(name.decode("utf-8", errors="surrogateescape"))
        for name in result.stdout.split(b"\0")
        if name
    }
    return sorted(paths, key=lambda path: str(path).casefold())


def audit(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if not path.exists() and not path.is_symlink():
            continue  # staged deletions and worktree removals
        lower_name = path.name.casefold()
        suffix = path.suffix.casefold()

        if suffix in MEDIA_SUFFIXES or "audio_raw" in {part.casefold() for part in path.parts}:
            errors.append(f"media audio/video tidak boleh dilacak: {path}")
        if lower_name.startswith(AUDIO_ARCHIVE_PREFIX) and suffix == ".zip":
            errors.append(f"arsip audio tidak boleh masuk Git: {path}")

        try:
            size = path.lstat().st_size
        except OSError as exc:
            errors.append(f"tidak dapat memeriksa ukuran {path}: {exc}")
            continue
        if size > MAX_FILE_BYTES:
            errors.append(
                f"file terlalu besar ({size / (1024 * 1024):.1f} MiB, batas repo 50 MiB): {path}"
            )
    return errors


def main() -> int:
    try:
        paths = candidate_paths()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"[GAGAL] audit Git tidak dapat dijalankan: {exc}", file=sys.stderr)
        return 2

    errors = audit(paths)
    if errors:
        print("[GAGAL] Audit repo menemukan file yang tidak boleh di-commit:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(
            "Simpan audio/video dan arsipnya di penyimpanan eksternal; jangan paksa `git add -f`.",
            file=sys.stderr,
        )
        return 1

    print(f"[OK] {len(paths)} file terlacak/lokal diperiksa; tidak ada media terlarang atau file >50 MiB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
