#!/usr/bin/env python3
"""One-off helper: extract the KlikTahu sources from the Google Drive archive.

Runs inside the transfer GitHub Actions workflow. Audio (*.wav) is excluded from
the Git tree because it is large and regenerable; it is indexed instead.
"""
from __future__ import annotations

import os
import re
import zipfile

ZIP = "transfer/incoming/kliktahu.zip"
OUT = "transfer/extracted"
QUARANTINE = "transfer/quarantine"
EXCLUDE_EXT = {".wav"}

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{12,}"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"\bya29\.[A-Za-z0-9_\-]{10,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\."),
    re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{20,}"),
]
KEYISH = re.compile(
    r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|APIKEY|CLIENT_ID|CLIENT_SECRET|AUTH)",
    re.I,
)

PLACEHOLDERS = ("your_", "xxx", "<", "changeme", "change_me", "todo")


def looks_secret(key: str, value: str) -> bool:
    if not value:
        return False
    lowered = value.lower()
    if lowered.startswith(PLACEHOLDERS):
        return False
    if any(p.search(value) for p in SECRET_PATTERNS):
        return True
    return bool(KEYISH.search(key)) and len(value) > 12


def is_env_file(name: str) -> bool:
    base = os.path.basename(name).lower()
    return base == ".env" or base.endswith(".env")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(QUARANTINE, exist_ok=True)

    zf = zipfile.ZipFile(ZIP)
    infos = [i for i in zf.infolist() if not i.is_dir()]

    written = 0
    skipped_audio = 0
    quarantined: list[tuple[str, list[str]]] = []
    wav_index: list[tuple[str, int]] = []
    env_audit: list[tuple[str, list[str], list[str]]] = []
    nested: list[tuple[str, list[tuple[str, int]]]] = []

    for info in infos:
        name = info.filename
        base = os.path.basename(name)
        ext = os.path.splitext(base)[1].lower()

        if ext in EXCLUDE_EXT:
            skipped_audio += 1
            wav_index.append((name, info.file_size))
            continue

        data = zf.read(info)

        if is_env_file(name):
            text = data.decode("utf-8", "replace")
            rows: list[str] = []
            bad: list[str] = []
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if looks_secret(key, value):
                    bad.append(key)
                    rows.append(f"{key}=<REDACTED len={len(value)}>")
                else:
                    rows.append(f"{key}={value}")
            if bad:
                quarantined.append((name, bad))
                with open(
                    os.path.join(QUARANTINE, base + ".redacted"), "w", encoding="utf-8"
                ) as fh:
                    fh.write("\n".join(rows) + "\n")
            env_audit.append((name, rows, bad))

        dest = os.path.join(OUT, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        written += 1

        if base.lower().endswith(".zip"):
            try:
                inner = zipfile.ZipFile(dest)
                nested.append(
                    (name, [(m.filename, m.file_size) for m in inner.infolist()])
                )
            except Exception as exc:  # noqa: BLE001
                nested.append((name, [(f"<unreadable: {exc}>", 0)]))

    with open("transfer/WAV_INDEX.txt", "w", encoding="utf-8") as fh:
        fh.write("# Raw audio kept out of git (still inside the Drive archive)\n")
        total = sum(s for _, s in wav_index) / 1024 / 1024
        fh.write(f"# count: {len(wav_index)}  total: {total:.1f} MiB\n")
        for name, size in sorted(wav_index):
            fh.write(f"{size:>9}  {name}\n")

    with open("transfer/ENV_AUDIT.md", "w", encoding="utf-8") as fh:
        fh.write("# .env audit\n\n")
        fh.write(f"- env files: **{len(env_audit)}**\n")
        fh.write(f"- quarantined (secret-looking values masked): **{len(quarantined)}**\n\n")
        for name, rows, bad in env_audit:
            fh.write(f"## `{name}`\n\n")
            if bad:
                fh.write(f"> QUARANTINED — secret-looking keys: {', '.join(bad)}\n\n")
            fh.write("```\n" + "\n".join(rows) + "\n```\n\n")

    report = ["# Extraction report\n"]
    report.append(f"- files written: **{written}**")
    report.append(f"- audio files skipped: **{skipped_audio}**")
    report.append(f"- env files quarantined: **{len(quarantined)}**\n")
    report.append("## Nested archives\n")
    for name, entries in nested:
        report.append(f"### `{name}` ({len(entries)} entries)\n")
        for entry, size in entries[:200]:
            report.append(f"- {size:>9}  `{entry}`")
        report.append("")
    with open("transfer/EXTRACT_REPORT.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")

    print("\n".join(report))
    print(f"written={written} skipped_audio={skipped_audio} quarantined={len(quarantined)}")


if __name__ == "__main__":
    main()
