#!/usr/bin/env python3
"""Validate docs/content-inventory.csv: paths, sizes, HTML cover refs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_lib import (  # noqa: E402
    FULL_CSV,
    expand_all,
    load_inventory,
    scan_html_image_srcs,
    write_full_csv,
    find_image,
    PHOTO,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate content inventory paths/sizes")
    parser.add_argument(
        "--write-full",
        action="store_true",
        help=f"Also write expanded table to {FULL_CSV.relative_to(ROOT)}",
    )
    args = parser.parse_args()

    raw = load_inventory()
    rows = expand_all(raw)
    html_srcs = scan_html_image_srcs()

    missing = [r for r in rows if r.status == "missing" or "missing" in r.status]
    weak = [r for r in rows if "weak" in r.status]
    heavy = [r for r in rows if "heavy" in r.status]
    placeholder = [r for r in rows if "placeholder" in r.status]
    unused = [r for r in rows if r.on_site == "no"]

    # HTML references that do not exist on disk
    broken_html: list[str] = []
    for src in sorted(html_srcs):
        p = ROOT / src
        if p.is_file():
            continue
        # try find by stem
        stem = Path(src).with_suffix("").as_posix()
        if stem.startswith("photo/"):
            stem = stem[6:]
        if find_image(stem) is None:
            broken_html.append(src)

    print(f"Inventory rows: {len(rows)}")
    print(f"HTML/JS photo refs: {len(html_srcs)}")
    print(f"Broken HTML paths: {len(broken_html)}")
    for s in broken_html:
        print(f"  MISSING  {s}")

    print(f"\nMissing inventory media: {len(missing)}")
    for r in missing:
        print(f"  MISSING  {r.key}  →  {r.image_path}")

    print(f"\nWeak (short side < 1000 or narrow hero): {len(weak)}")
    for r in weak:
        print(f"  WEAK     {r.key}  {r.w}x{r.h}  {r.kb}KB")

    print(f"\nHeavy (>= 2.5 MB): {len(heavy)}")
    for r in heavy:
        print(f"  HEAVY    {r.key}  {r.kb}KB")

    print(f"\nPlaceholder contacts/texts: {len(placeholder)}")
    for r in placeholder:
        print(f"  TODO     {r.key}  {r.todo}")

    print(f"\nUnused on site (gallery candidates): {len(unused)}")
    for r in unused:
        print(f"  UNUSED   {r.key}")

    if args.write_full:
        write_full_csv(rows)
        print(f"\nWrote {FULL_CSV.relative_to(ROOT)}")

    # Fail deploy gate: broken HTML covers or missing rows that are on_site
    critical = list(broken_html) + [
        r.key for r in missing if r.on_site == "yes" or "diploma" in r.key
    ]
    if critical:
        print(f"\nFAIL: {len(critical)} critical path issue(s)")
        return 1

    print("\nPASS: no broken cover paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
