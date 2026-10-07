#!/usr/bin/env python3
"""Create public-facing artifact names from the video's actual title."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


def title_slug(title: str) -> str:
    """Return a safe, stable ASCII slug; never includes episode/run identifiers."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("judul video kosong")
    normalized = unicodedata.normalize("NFKD", title.strip())
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii").casefold()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")
    if not slug:
        raise ValueError("judul tidak menghasilkan nama berkas yang valid")
    return slug[:100].rstrip("-")


def title_from_content(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    title = data.get("title") if isinstance(data, dict) else None
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"content file tidak memiliki judul video: {path}")
    return title.strip()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("pakai: python3 tools/video_names.py <content.json>", file=sys.stderr)
        return 2
    try:
        title = title_from_content(Path(argv[1]))
        print(title_slug(title))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[GAGAL] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
