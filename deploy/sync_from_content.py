#!/usr/bin/env python3
"""Expand minimal content-inventory.csv → full table; optionally write .txt for deploy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_lib import (  # noqa: E402
    FULL_CSV,
    INVENTORY_CSV,
    apply_bodies,
    expand_all,
    load_inventory,
    write_full_csv,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore full content table and sync .txt sidecars from body"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write full CSV only; do not write .txt files",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write .txt sidecars for rows with non-empty body (default if not --dry-run)",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=INVENTORY_CSV,
        help="Path to minimal inventory CSV",
    )
    args = parser.parse_args()

    raw = load_inventory(args.csv)
    rows = expand_all(raw)
    write_full_csv(rows)
    print(f"Wrote full table: {FULL_CSV.relative_to(ROOT)} ({len(rows)} rows)")

    do_apply = args.apply or not args.dry_run
    if args.dry_run:
        do_apply = False

    if do_apply:
        log = apply_bodies(rows, dry_run=False)
        print(f"Applied body → .txt: {len(log)} file(s)")
        for line in log:
            print(f"  {line}")
    else:
        log = apply_bodies(rows, dry_run=True)
        print(f"Dry-run body → .txt: {len(log)} file(s) would be written")
        for line in log:
            print(f"  {line}")

    media = [r for r in rows if r.image_path]
    print(
        f"\nSummary: text={sum(1 for r in rows if r.role == 'text')} "
        f"card={sum(1 for r in rows if r.role == 'card')} "
        f"media={len(media)} "
        f"missing={sum(1 for r in rows if 'missing' in r.status)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
