#!/usr/bin/env python3
"""Pack static site for deploy."""

from __future__ import annotations

import os
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = Path(os.environ.get("TEMP", "/tmp")) / "sandomirova-deploy.tgz"
PHOTO_EXCLUDE_NAMES = {"narod_attachment_links.html", "dscn3851-copy.jpg", "author.jpg"}
PHOTO1_EXCLUDE = {"narod_attachment_links.html", "README.md", "_list.txt"}


def add_photo_tree(tar: tarfile.TarFile, photo_dir: Path) -> None:
    for path in sorted(photo_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in PHOTO_EXCLUDE_NAMES:
            continue
        arcname = path.relative_to(ROOT).as_posix()
        tar.add(path, arcname=arcname)


def main() -> None:
    with tarfile.open(ARCHIVE, "w:gz") as tar:
        for item in ("index.html", "assets"):
            tar.add(ROOT / item, arcname=item)
        photo_dir = ROOT / "photo"
        if photo_dir.exists():
            add_photo_tree(tar, photo_dir)
    print(f"Created {ARCHIVE} ({ARCHIVE.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
