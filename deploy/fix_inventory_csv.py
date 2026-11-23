#!/usr/bin/env python3
"""Repair docs/content-inventory.csv → UTF-8 BOM, ';', column photo."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_lib import (  # noqa: E402
    INVENTORY_CSV,
    MINIMAL_FIELDS,
    PHOTO,
    expand_all,
    find_images_by_basename,
    media_stem_for_key,
    normalize_photo_stem,
    write_full_csv,
    write_minimal_csv,
    _detect_delimiter,
)


TEXT_KEYS_NO_PHOTO = {
    "site/title",
    "site/description",
    "header/logo",
    "hero/h1",
    "hero/subtitle",
    "hero/tags",
    "hero/cta",
    "services/title",
    "services/lead",
    "process/title",
    "process/intro",
    "process/thesis_1",
    "process/thesis_2",
    "process/thesis_3",
    "portfolio/title",
    "portfolio/lead",
    "portfolio/cta",
    "about/title",
    "about/name",
    "about/p1",
    "about/p2",
    "about/stat_1",
    "about/stat_2",
    "about/stat_3",
    "awards/title",
    "contact/title",
    "contact/lead",
    "contact/name",
    "contact/phone",
    "contact/email",
    "contact/messengers",
    "contact/form_hint",
    "contact/privacy",
    "footer/name",
    "footer/year",
}


def read_raw_rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines:
        return []
    header = lines[0].lstrip("\ufeff").strip().strip('"')
    # glued header recovery
    glued = header.replace(" ", "").lower()
    if "key" in glued and "title" in glued and _detect_delimiter(header) == "," and header.count(",") == 0 and "\t" not in header and ";" not in header:
        # completely glued — cannot recover data mapping; raise
        raise SystemExit(f"Broken header: {header!r}")

    delim = _detect_delimiter(header)
    reader = csv.DictReader(lines, delimiter=delim)
    if reader.fieldnames:
        reader.fieldnames = [(h or "").lstrip("\ufeff").strip() for h in reader.fieldnames]
    rows: list[dict[str, str]] = []
    for row in reader:
        norm = {(k or "").strip(): (v or "").strip() for k, v in row.items() if k}
        key = norm.get("key", "")
        if not key:
            continue
        photo = normalize_photo_stem(norm.get("photo", ""))
        rows.append(
            {
                "key": key,
                "photo": photo,
                "title": norm.get("title", ""),
                "meta": norm.get("meta", ""),
                "lead": norm.get("lead", ""),
                "body": norm.get("body", ""),
            }
        )
    return rows


def suggest_photo(key: str, existing: str) -> str:
    if existing:
        return existing
    if key in TEXT_KEYS_NO_PHOTO:
        return ""
    # card keys: leave empty (cover via child / photo later)
    if key.count("/") == 1 and key.split("/")[0] in (
        "services",
        "process",
    ) and key.split("/")[1] in (
        "mural-painting",
        "mosaic",
        "stained-glass",
        "author-collections",
        "light-compositions",
        "idea-and-concept",
        "material",
        "execution",
        "acceptance",
    ):
        return ""
    stem = media_stem_for_key(key)
    if not stem:
        # about/author-photo-placeholder etc.
        if "/" in key:
            return Path(key).name
        return ""
    name = Path(stem).name
    hits = find_images_by_basename(name)
    if hits:
        return name
    # still set basename so user sees expected name
    return name


def main() -> int:
    if not INVENTORY_CSV.is_file():
        raise SystemExit(f"Missing {INVENTORY_CSV}")

    rows = read_raw_rows(INVENTORY_CSV)
    print(f"Read {len(rows)} rows from {INVENTORY_CSV.name}")

    for r in rows:
        r["photo"] = suggest_photo(r["key"], r.get("photo", ""))

    write_minimal_csv(rows, INVENTORY_CSV)
    data = INVENTORY_CSV.read_bytes()
    print(
        f"Wrote {INVENTORY_CSV.name}: BOM={data[:3]==bytes([0xEF,0xBB,0xBF])} "
        f"header={INVENTORY_CSV.read_text(encoding='utf-8-sig').splitlines()[0]!r}"
    )

    # verify parse
    from content_lib import load_inventory

    loaded = load_inventory()
    print(f"Reload OK: {len(loaded)} rows; photo filled: {sum(1 for x in loaded if x['photo'])}")

    try:
        write_full_csv(expand_all(loaded))
        print("Wrote content-inventory.full.csv")
    except PermissionError:
        alt = INVENTORY_CSV.with_name("content-inventory.full.utf8.csv")
        write_full_csv(expand_all(loaded), alt)
        print(f"full.csv locked → wrote {alt.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
