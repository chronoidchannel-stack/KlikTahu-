#!/usr/bin/env python3
"""LEGACY WAV archive validator/restore utility — not used by current production.

Per current owner direction, new production uses human-listenable MP3 narration.
The manifest parser remains for historical audit/tests. CLI restoration requires
an explicit --legacy-wav-restore opt-in and must not be used for new videos.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

CHUNK_SIZE = 1024 * 1024
MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
WAVE_CONTAINER_TAGS = {b"RIFF", b"RIFX", b"RF64", b"BW64"}
HEADER_RE = re.compile(r"^## ([A-Za-z0-9_-]+)/audio_raw\b")
ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([0-9,]+)\s*KB\s*\|")
TOTAL_RE = re.compile(r"^Total:\s*\*\*(\d+)\s+berkas\*\*", re.MULTILINE)


class RestoreError(Exception):
    """An archive cannot be safely restored as the expected audio set."""


@dataclass(frozen=True)
class VerifiedMember:
    key: tuple[str, str]
    info: zipfile.ZipInfo
    sha256: str


def load_manifest(manifest_path: Path) -> dict[tuple[str, str], Path]:
    """Map (episode slug, WAV filename) to its local, ignored destination."""
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RestoreError(f"manifest tidak dapat dibaca: {manifest_path}: {exc}") from exc

    result: dict[tuple[str, str], Path] = {}
    current_slug: str | None = None

    for line in text.splitlines():
        if line.startswith("## "):
            match = HEADER_RE.match(line)
            current_slug = match.group(1) if match else None
            continue
        if current_slug is None:
            continue
        row = ROW_RE.match(line)
        if not row:
            continue

        filename = row.group(1)
        if (
            PurePosixPath(filename).name != filename
            or "/" in filename
            or "\\" in filename
            or not filename.lower().endswith(".wav")
        ):
            raise RestoreError(f"nama file WAV tidak valid di manifest: {filename!r}")

        key = (current_slug, filename)
        if key in result:
            raise RestoreError(f"entri ganda di manifest: {current_slug}/audio_raw/{filename}")

        tree = "long" if re.match(r"^v\d{2}_", current_slug) else "episodes"
        result[key] = Path(tree, current_slug, "audio_raw", filename)

    if not result:
        raise RestoreError(f"tidak ada daftar WAV di manifest: {manifest_path}")

    declared_total = TOTAL_RE.search(text)
    if declared_total and int(declared_total.group(1)) != len(result):
        raise RestoreError(
            f"manifest menyatakan {declared_total.group(1)} berkas, tetapi tabel berisi {len(result)}"
        )
    return result


def _safe_member_parts(info: zipfile.ZipInfo) -> tuple[str, ...]:
    """Validate/normalize ZIP names before matching; never extract archive paths."""
    name = info.filename.replace("\\", "/")
    if not name or name.startswith("/") or "\x00" in name:
        raise RestoreError(f"path ZIP tidak aman: {info.filename!r}")

    # Harmless ./ prefixes are common in ZIPs; collapse them. Parent traversal
    # remains a hard error even though member paths are never used as destinations.
    parts = [part for part in name.split("/") if part not in {"", "."}]
    if ".." in parts or (parts and ":" in parts[0]):
        raise RestoreError(f"path ZIP tidak aman: {info.filename!r}")
    if not parts and not info.is_dir():
        raise RestoreError(f"path ZIP tidak aman: {info.filename!r}")
    return tuple(parts)


def _match_key(parts: tuple[str, ...], expected: dict[tuple[str, str], Path]) -> tuple[str, str] | None:
    # Supports archives with or without an outer folder such as "episodes/".
    for index in range(len(parts) - 2):
        if index + 3 == len(parts) and parts[index + 1] == "audio_raw":
            key = (parts[index], parts[index + 2])
            if key in expected:
                return key
    return None


def _is_wave_header(header: bytes) -> bool:
    return (
        len(header) >= 12
        and header[:4] in WAVE_CONTAINER_TAGS
        and header[8:12] == b"WAVE"
    )


def _hash_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo, label: str) -> str:
    if info.file_size < 12 or info.file_size > MAX_MEMBER_BYTES:
        raise RestoreError(
            f"ukuran WAV tidak masuk akal ({info.file_size:,} byte): {label}"
        )

    digest = hashlib.sha256()
    size = 0
    try:
        with archive.open(info, "r") as source:
            first = source.read(12)
            if not _is_wave_header(first):
                raise RestoreError(f"header bukan WAV yang dikenal: {label}")
            digest.update(first)
            size += len(first)
            while chunk := source.read(CHUNK_SIZE):
                digest.update(chunk)
                size += len(chunk)
    except (zipfile.BadZipFile, RuntimeError, EOFError, OSError) as exc:
        raise RestoreError(f"isi ZIP rusak atau terenkripsi ({label}): {exc}") from exc

    if size != info.file_size:
        raise RestoreError(f"ukuran isi tidak cocok untuk {label}: {size} != {info.file_size}")
    return digest.hexdigest()


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _restore_member(
    archive: zipfile.ZipFile,
    member: VerifiedMember,
    target: Path,
    overwrite: bool,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=".restore-audio-", suffix=".tmp", dir=target.parent)
    temporary = Path(temporary_name)
    digest = hashlib.sha256()
    size = 0

    try:
        with os.fdopen(fd, "wb") as destination, archive.open(member.info, "r") as source:
            first = source.read(12)
            if not _is_wave_header(first):
                raise RestoreError(f"header WAV berubah saat ekstraksi: {member.info.filename}")
            destination.write(first)
            digest.update(first)
            size += len(first)
            while chunk := source.read(CHUNK_SIZE):
                destination.write(chunk)
                digest.update(chunk)
                size += len(chunk)

        if size != member.info.file_size or digest.hexdigest() != member.sha256:
            raise RestoreError(f"integritas berubah saat ekstraksi: {member.info.filename}")
        if not overwrite and target.exists():
            raise RestoreError(f"file tujuan muncul saat ekstraksi; tidak ditimpa: {target}")
        os.replace(temporary, target)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        finally:
            raise


def restore_archive(
    archive_path: Path,
    repo_root: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
) -> tuple[int, int, int]:
    """Validate and restore the manifest's WAVs. Returns (written, unchanged, total)."""
    root = repo_root.resolve()
    archive_path = archive_path.expanduser().resolve()
    expected = load_manifest(root / "docs" / "audio-manifest.md")

    if not archive_path.is_file():
        raise RestoreError(f"arsip tidak ditemukan: {archive_path}")
    if not zipfile.is_zipfile(archive_path):
        raise RestoreError(f"file bukan ZIP yang valid: {archive_path}")

    with zipfile.ZipFile(archive_path, "r") as archive:
        selected: dict[tuple[str, str], zipfile.ZipInfo] = {}
        for info in archive.infolist():
            parts = _safe_member_parts(info)
            if info.is_dir():
                continue
            key = _match_key(parts, expected)
            if key is None:
                continue
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise RestoreError(f"symlink tidak diterima di arsip: {info.filename}")
            if key in selected:
                raise RestoreError(f"entri audio ganda dalam ZIP: {key[0]}/audio_raw/{key[1]}")
            selected[key] = info

        missing = sorted(set(expected) - set(selected))
        if missing:
            examples = ", ".join(f"{slug}/audio_raw/{name}" for slug, name in missing[:8])
            more = " ..." if len(missing) > 8 else ""
            raise RestoreError(f"arsip tidak lengkap: {len(missing)} WAV hilang ({examples}{more})")

        total_size = sum(info.file_size for info in selected.values())
        if total_size > MAX_TOTAL_BYTES:
            raise RestoreError(f"ukuran audio terurai melebihi batas aman: {total_size:,} byte")

        members: list[VerifiedMember] = []
        for key, info in selected.items():
            label = f"{key[0]}/audio_raw/{key[1]}"
            members.append(VerifiedMember(key, info, _hash_member(archive, info, label)))

        targets: dict[tuple[str, str], Path] = {}
        unchanged: set[tuple[str, str]] = set()
        conflicts: list[Path] = []
        for member in members:
            relative = expected[member.key]
            target = root / relative
            resolved_target = target.resolve(strict=False)
            try:
                resolved_target.relative_to(root)
            except ValueError as exc:
                raise RestoreError(f"tujuan keluar dari folder repo: {relative}") from exc

            # Episode directories are part of the repository; don't invent a target
            # if a stale manifest points to an unknown slug. Reject symlinks in the
            # destination chain so writes stay in the intended ignored folder.
            if not (root / relative.parts[0] / relative.parts[1]).is_dir():
                raise RestoreError(f"folder episode tidak ditemukan: {relative.parts[0]}/{relative.parts[1]}")
            current = root
            for part in relative.parts:
                current = current / part
                if current.is_symlink():
                    raise RestoreError(f"tujuan memuat symlink; dibatalkan: {relative}")
            targets[member.key] = target
            if target.exists():
                if not target.is_file():
                    raise RestoreError(f"tujuan bukan berkas biasa: {relative}")
                if _hash_file(target) == member.sha256:
                    unchanged.add(member.key)
                elif not overwrite:
                    conflicts.append(relative)

        if conflicts:
            sample = ", ".join(str(path) for path in conflicts[:8])
            more = " ..." if len(conflicts) > 8 else ""
            raise RestoreError(
                f"{len(conflicts)} file lokal sudah ada dan berbeda ({sample}{more}); "
                "gunakan --overwrite hanya jika memang ingin menggantinya"
            )

        planned = len(members) - len(unchanged)
        if dry_run:
            return planned, len(unchanged), len(members)

        written = 0
        for member in members:
            if member.key in unchanged:
                continue
            _restore_member(archive, member, targets[member.key], overwrite)
            written += 1
        return written, len(unchanged), len(members)


def main(argv: list[str] | None = None) -> int:
    root_default = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description=(
            "LEGACY saja: audit/pulihkan arsip WAV lama. Produksi baru memakai MP3; "
            "restore WAV harus diaktifkan secara eksplisit."
        )
    )
    parser.add_argument(
        "archive",
        nargs="?",
        type=Path,
        help="lokasi ZIP; bawaan: kliktahu.zip di akar repo",
    )
    parser.add_argument("--root", type=Path, default=root_default, help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="validasi penuh tanpa menulis WAV")
    parser.add_argument("--overwrite", action="store_true", help="izinkan mengganti WAV lokal yang berbeda")
    parser.add_argument(
        "--legacy-wav-restore",
        action="store_true",
        help="opt-in manual untuk arsip lama saja; jangan dipakai untuk produksi baru",
    )
    args = parser.parse_args(argv)

    if not args.legacy_wav_restore:
        print(
            "[STOP] Restore WAV adalah workflow arsip lama. Produksi baru wajib memakai narasi MP3; "
            "jika pemilik benar-benar meminta pemulihan arsip lama, gunakan opt-in eksplisit.",
            file=sys.stderr,
        )
        return 3

    root = args.root.expanduser().resolve()
    archive_path = args.archive or (root / "kliktahu.zip")
    try:
        written, unchanged, total = restore_archive(
            archive_path, root, dry_run=args.dry_run, overwrite=args.overwrite
        )
    except (RestoreError, zipfile.BadZipFile, OSError) as exc:
        print(f"[GAGAL] {exc}", file=sys.stderr)
        return 2

    action = "akan dipulihkan" if args.dry_run else "dipulihkan"
    print(f"[OK] {total} WAV sesuai manifest; {written} {action}, {unchanged} sudah cocok.")
    print("[AMAN] Hanya WAV manifest yang ditulis; ZIP/audio tidak perlu dan tidak boleh di-commit.")
    if not args.dry_run:
        print("[CEK] Jalankan `git status --short` — arsip dan WAV harus tetap diabaikan oleh .gitignore.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
