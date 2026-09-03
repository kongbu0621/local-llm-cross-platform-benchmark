#!/usr/bin/env python3
"""Validate local Markdown links and anchors without network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXPLICIT_ANCHOR_RE = re.compile(r'<a\s+(?:name|id)=["\']([^"\']+)["\']\s*></a>', re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def github_slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"[^\w\- \u0080-\uffff]", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", "-", text)
    return text


def anchors_for(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    anchors = set(EXPLICIT_ANCHOR_RE.findall(text))
    counts: dict[str, int] = {}
    for heading in HEADING_RE.findall(text):
        slug = github_slug(heading)
        if not slug:
            continue
        index = counts.get(slug, 0)
        anchors.add(slug if index == 0 else f"{slug}-{index}")
        counts[slug] = index + 1
    return anchors


def parse_destination(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    # Repository links do not intentionally use Markdown titles; if one is
    # introduced, keep the first token as the destination rather than treating
    # the title as part of the path.
    return raw.split(maxsplit=1)[0]


def main() -> int:
    errors: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}

    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        text = source.read_text(encoding="utf-8")
        scan = FENCE_RE.sub("", text)
        for raw in LINK_RE.findall(scan):
            dest = parse_destination(raw)
            if not dest or dest.startswith(("http://", "https://", "mailto:", "data:")):
                continue

            if "#" in dest:
                path_part, fragment = dest.split("#", 1)
            else:
                path_part, fragment = dest, ""

            path_part = unquote(path_part)
            fragment = unquote(fragment)
            target = source if not path_part else (source.parent / path_part).resolve()

            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"link escapes repository: {source.relative_to(ROOT)} -> {dest}")
                continue

            if not target.exists():
                errors.append(f"missing local link target: {source.relative_to(ROOT)} -> {dest}")
                continue

            if fragment:
                if target.is_dir():
                    errors.append(f"anchor points at directory: {source.relative_to(ROOT)} -> {dest}")
                    continue
                if target.suffix.lower() not in {".md", ".markdown"}:
                    # GitHub does not provide Markdown-style anchors for JSON,
                    # logs, etc.; fragment links to those are almost certainly
                    # accidental in this repository.
                    errors.append(f"anchor on non-Markdown target: {source.relative_to(ROOT)} -> {dest}")
                    continue
                anchors = anchor_cache.setdefault(target, anchors_for(target))
                if fragment not in anchors:
                    errors.append(f"missing Markdown anchor: {source.relative_to(ROOT)} -> {dest}")

    if errors:
        print("MARKDOWN LINK CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("MARKDOWN LINK CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
