#!/usr/bin/env python3
"""Create a stable SHA256 manifest for files under a directory.

Usage:
    python scripts/sha256_manifest.py /path/to/data > manifest.sha256
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

CHUNK = 8 * 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: sha256_manifest.py DIRECTORY", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        print(f"{sha256_file(path)}  {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
