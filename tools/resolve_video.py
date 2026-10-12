#!/usr/bin/env python3
"""Resolve a title-based public video slug to a source folder.

Legacy folder keys remain supported as internal aliases; callers should prefer
`content.json:title` slugs so public commands do not depend on episode numbers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.video_names import title_slug


def _video_mode(data: dict, container: str) -> str | None:
    if container == "episodes":
        return "shorts"
    if container == "long":
        return "long"
    if container != "videos":
        return None
    explicit = str(data.get("format", data.get("video_format", ""))).casefold()
    engine = str(data.get("mesin", "")).casefold()
    if explicit in {"short", "shorts", "vertical"} or engine in {"v11", "shorts"}:
        return "shorts"
    if explicit in {"long", "16:9", "landscape"} or engine in {"long16x9", "long"}:
        return "long"
    return None


def resolve_video(identifier: str, mode: str, root: Path) -> Path:
    mode = mode.casefold()
    if mode not in {"shorts", "long"}:
        raise ValueError("mode harus shorts atau long")
    if not identifier or identifier in {".", ".."} or "/" in identifier or "\\" in identifier:
        raise ValueError("masukkan slug judul video, bukan path")

    folders = ("episodes", "videos") if mode == "shorts" else ("long", "videos")
    matches: list[Path] = []
    for container in folders:
        parent = root / container
        if not parent.is_dir():
            continue
        for directory in sorted(parent.iterdir(), key=lambda path: path.name.casefold()):
            content_path = directory / "content.json"
            if not directory.is_dir() or not content_path.is_file() or not (directory / "config.env").is_file():
                continue
            try:
                data = json.loads(content_path.read_text(encoding="utf-8"))
                title = data.get("title", "")
            except (OSError, json.JSONDecodeError):
                continue
            if _video_mode(data, container) != mode:
                continue
            is_internal_alias = directory.name.casefold() == identifier.casefold()
            try:
                is_title_slug = title_slug(title) == identifier.casefold()
            except ValueError:
                is_title_slug = False
            if is_internal_alias or is_title_slug:
                matches.append(directory)

    unique = sorted(set(matches))
    if not unique:
        raise FileNotFoundError(
            f"video tidak ditemukan: {identifier!r} (cari slug dari judul di mode {mode})"
        )
    if len(unique) > 1:
        choices = ", ".join(str(path.relative_to(root)) for path in unique)
        raise ValueError(f"slug cocok ke beberapa video; minta pemilik memilih: {choices}")
    return unique[0]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("pakai: python3 tools/resolve_video.py <shorts|long> <judul-slug>", file=sys.stderr)
        return 2
    root = Path(__file__).resolve().parents[1]
    try:
        print(resolve_video(argv[2], argv[1], root).relative_to(root))
    except (FileNotFoundError, ValueError) as exc:
        print(f"[GAGAL] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
