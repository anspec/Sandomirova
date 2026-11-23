#!/usr/bin/env python3
"""Shared helpers for docs/content-inventory.csv → paths, sizes, full rows."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY_CSV = ROOT / "docs" / "content-inventory.csv"
FULL_CSV = ROOT / "docs" / "content-inventory.full.csv"
PHOTO = ROOT / "photo"
INDEX_HTML = ROOT / "index.html"
MAIN_JS = ROOT / "assets" / "js" / "main.js"

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP")

# Shortest side below this → weak
MIN_SHORT_SIDE = 1000
# Hero / wide covers
MIN_HERO_WIDTH = 1600
# Bytes above this → heavy
HEAVY_BYTES = 2_500_000

SECTION_PREFIX = {
    "site": "meta",
    "header": "header",
    "hero": "hero",
    "services": "services",
    "process": "process",
    "portfolio": "portfolio",
    "featured-works": "portfolio",
    "about": "about",
    "awards": "awards",
    "professional-recognition": "awards",
    "contact": "contact",
    "footer": "footer",
}

# Card-level keys (title/lead) → default cover stem under photo/
SERVICE_COVERS = {
    "services/mural-painting": "services/mural-painting/classical-mural-portrait",
    "services/mosaic": "services/mosaic/mosaic-panel-assembly",
    "services/stained-glass": "services/stained-glass/botanical-glass-panel",
    "services/author-collections": "services/author-collections/glass-vessels-collection",
    "services/light-compositions": "services/light-compositions/floral-glass-chandelier",
}

PROCESS_COVERS = {
    "process/idea-and-concept": "process/idea-and-concept/stained-glass-design-window",
    "process/material": "process/material/surface-texture-samples",
    "process/execution": "process/execution/on-site-stained-glass-installation",
    "process/acceptance": "process/acceptance/completed-vitrazh-interior",
}

TEXT_ONLY_PREFIXES = (
    "site/",
    "header/",
    "portfolio/title",
    "portfolio/lead",
    "portfolio/cta",
    "awards/title",
    "about/title",
    "about/name",
    "about/p",
    "about/stat_",
    "contact/",
    "footer/",
    "services/title",
    "services/lead",
    "process/title",
    "process/intro",
    "process/thesis_",
    "hero/h1",
    "hero/subtitle",
    "hero/tags",
    "hero/cta",
)


@dataclass
class InventoryRow:
    key: str
    photo: str = ""
    title: str = ""
    meta: str = ""
    lead: str = ""
    body: str = ""
    section: str = ""
    role: str = ""
    is_cover: str = ""
    image_path: str = ""
    txt_path: str = ""
    alt: str = ""
    on_site: str = ""
    w: str = ""
    h: str = ""
    kb: str = ""
    status: str = ""
    todo: str = ""
    notes: list[str] = field(default_factory=list)


# Excel (RU Windows): UTF-8 BOM + semicolon
CSV_ENCODING = "utf-8-sig"
CSV_DELIMITER = ";"

# Minimal CSV columns (photo = unique image basename without extension)
MINIMAL_FIELDS = ["key", "photo", "title", "meta", "lead", "body"]
OPTIONAL_MINIMAL = {"photo"}

# Directories skipped when resolving photo by basename
_SEARCH_SKIP = {
    ".git",
    ".cursor",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "deploy",
    "docs",
    "assets",
}


def normalize_photo_stem(value: str) -> str:
    """Strip path and extension → unique basename for lookup."""
    v = (value or "").strip().replace("\\", "/")
    if not v:
        return ""
    name = Path(v).name
    # drop known image extensions if user pasted full filename
    lower = name.lower()
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff"):
        if lower.endswith(ext):
            return name[: -len(ext)]
    return name


def _detect_delimiter(header: str) -> str:
    """Prefer ; for Excel RU; also support tab (Excel TSV) and comma."""
    if "\t" in header and header.count("\t") >= max(header.count(";"), header.count(",")):
        return "\t"
    if header.count(";") >= header.count(","):
        return ";"
    return ","


def load_inventory(path: Path = INVENTORY_CSV) -> list[dict[str, str]]:
    raw = path.read_bytes()
    # tolerate plain UTF-8 without BOM
    text = raw.decode("utf-8-sig")
    header = text.splitlines()[0] if text else ""
    # strip accidental BOM/quotes glued into first header cell
    header_clean = header.lstrip("\ufeff").strip().strip('"')
    delimiter = _detect_delimiter(header_clean if header_clean else header)
    # rebuild first line if Excel glued headers without delimiter
    lines = text.splitlines()
    if lines and ("keytitle" in lines[0].replace(" ", "").lower() or (
        "key" in lines[0].lower()
        and "title" in lines[0].lower()
        and delimiter not in lines[0]
        and "\t" not in lines[0]
        and ";" not in lines[0]
        and "," not in lines[0]
    )):
        # e.g. keytitlemetaleadbody → cannot parse; caller should rewrite file
        raise SystemExit(
            "Сломан заголовок CSV (колонки слиплись). "
            "Запустите: python deploy/rewrite_inventory_csv.py"
        )
    reader = csv.DictReader(lines, delimiter=delimiter)
    # normalize fieldnames (Excel sometimes adds spaces / BOM)
    if reader.fieldnames:
        reader.fieldnames = [((h or "").lstrip("\ufeff").strip()) for h in reader.fieldnames]
    required = {"key", "title", "meta", "lead", "body"}
    names = set(reader.fieldnames or [])
    if not required.issubset(names):
        raise SystemExit(
            f"CSV must have columns: {sorted(required)}; got: {sorted(names)}"
        )
    out: list[dict[str, str]] = []
    for row in reader:
        # map by normalized keys
        norm = {(k or "").strip(): (v or "").strip() for k, v in row.items() if k is not None}
        item = {k: norm.get(k, "") for k in required}
        photo_raw = ""
        for alias in ("photo", "Photo", "PHOTO", "файл", "файл_фото"):
            if alias in norm and norm[alias]:
                photo_raw = norm[alias]
                break
        item["photo"] = normalize_photo_stem(photo_raw)
        out.append(item)
    return out


def section_for_key(key: str) -> str:
    top = key.split("/", 1)[0]
    return SECTION_PREFIX.get(top, top)


def is_text_only_key(key: str) -> bool:
    if key in SERVICE_COVERS or key in PROCESS_COVERS:
        return True  # card row; cover resolved separately
    for p in TEXT_ONLY_PREFIXES:
        if key == p.rstrip("/") or key.startswith(p):
            # hero/gothic-... is media
            if key.startswith("hero/") and key not in (
                "hero/h1",
                "hero/subtitle",
                "hero/tags",
                "hero/cta",
            ):
                return False
            if key.startswith("about/author-"):
                return False
            return True
    return False


def find_image(stem_under_photo: str) -> Path | None:
    base = PHOTO / stem_under_photo
    # exact stem + known exts in same folder
    parent = base.parent
    stem = base.name
    if not parent.is_dir():
        return None
    for ext in IMAGE_EXTS:
        cand = parent / f"{stem}{ext}"
        if cand.is_file():
            return cand
    # case-insensitive fallback
    lower = stem.lower()
    for p in parent.iterdir():
        if p.is_file() and p.stem.lower() == lower and p.suffix in IMAGE_EXTS:
            return p
    return None


def _is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix in IMAGE_EXTS


def find_images_by_basename(photo_stem: str) -> list[Path]:
    """Find image files in the project whose filename stem matches photo_stem."""
    stem = normalize_photo_stem(photo_stem)
    if not stem:
        return []
    needle = stem.lower()
    hits: list[Path] = []

    search_roots = [PHOTO]
    if (ROOT / "photo1").is_dir():
        search_roots.append(ROOT / "photo1")

    for root in search_roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if not _is_image_file(p):
                continue
            if p.stem.lower() == needle:
                hits.append(p)

    if hits:
        return hits

    # broader project search (rare)
    for p in ROOT.rglob("*"):
        if any(part in _SEARCH_SKIP for part in p.parts):
            continue
        if not _is_image_file(p):
            continue
        if p.stem.lower() == needle:
            hits.append(p)
    return hits


def resolve_image_path(
    *,
    photo: str,
    key: str,
    key_stem: str | None,
) -> tuple[Path | None, list[str]]:
    """
    Resolve image file.
    Priority: column `photo` (unique basename) → fallback key path under photo/.
    """
    notes: list[str] = []
    photo = normalize_photo_stem(photo)

    if photo:
        hits = find_images_by_basename(photo)
        if not hits:
            notes.append(f"photo={photo} не найден в проекте")
            return None, notes
        if len(hits) > 1:
            # prefer photo/, then path that contains key fragment
            under_photo = [h for h in hits if PHOTO in h.parents or h.parent == PHOTO]
            pool = under_photo or hits
            if key_stem:
                keyed = [h for h in pool if key_stem.replace("\\", "/") in h.as_posix().replace("\\", "/")]
                if keyed:
                    pool = keyed
            chosen = sorted(pool, key=lambda p: len(p.parts))[0]
            notes.append(
                "ambiguous photo="
                + photo
                + " → "
                + ", ".join(rel_posix(h) for h in hits[:5])
                + (f" (+{len(hits) - 5})" if len(hits) > 5 else "")
            )
            return chosen, notes
        return hits[0], notes

    if key_stem:
        found = find_image(key_stem)
        if found:
            return found, notes
        notes.append(f"key-path photo/{key_stem}.* не найден")
    return None, notes


def media_stem_for_key(key: str) -> str | None:
    if key in SERVICE_COVERS:
        return None  # card-only
    if key in PROCESS_COVERS:
        return None
    if is_text_only_key(key):
        return None
    # strip leading photo/ if present
    k = key[6:] if key.startswith("photo/") else key
    return k


def image_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        from PIL import Image

        with Image.open(path) as im:
            return im.size
    except Exception:
        pass
    # fallback: struct parse JPEG SOF
    try:
        data = path.read_bytes()
        if data[:2] == b"\xff\xd8":
            i = 2
            while i < len(data) - 8:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h = int.from_bytes(data[i + 5 : i + 7], "big")
                    w = int.from_bytes(data[i + 7 : i + 9], "big")
                    return w, h
                length = int.from_bytes(data[i + 2 : i + 4], "big")
                i += 2 + length
        # PNG
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            w = int.from_bytes(data[16:20], "big")
            h = int.from_bytes(data[20:24], "big")
            return w, h
    except Exception:
        return None
    return None


def scan_html_image_srcs() -> set[str]:
    text = INDEX_HTML.read_text(encoding="utf-8") if INDEX_HTML.is_file() else ""
    found = set(re.findall(r"""(?:src|content)=["'](photo/[^"']+)["']""", text))
    if MAIN_JS.is_file():
        js = MAIN_JS.read_text(encoding="utf-8")
        found.update(re.findall(r"""["'](photo/[^"']+\.(?:jpg|jpeg|png|webp|JPG))["']""", js))
    return {p.replace("\\", "/") for p in found}


def rel_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def classify_status(
    *,
    image: Path | None,
    on_site: bool,
    key: str,
    w: int | None,
    h: int | None,
    size: int | None,
    body: str,
    text_only: bool,
) -> tuple[str, str]:
    notes: list[str] = []
    if text_only:
        if key.startswith("contact/phone") or key.startswith("contact/email"):
            if "900" in (body + key) or "example" in (body + str(image)):
                pass
        title_placeholder = False
        return "ok", ""

    if image is None and media_stem_for_key(key):
        return "missing", "файл изображения не найден"

    if image is None:
        return "ok", ""

    if size is not None and size >= HEAVY_BYTES:
        notes.append("heavy")
    if w and h:
        short = min(w, h)
        if key.startswith("hero/") and w < MIN_HERO_WIDTH:
            notes.append("weak")
        elif short < MIN_SHORT_SIDE:
            notes.append("weak")
    if not on_site:
        notes.append("unused")
    if not body.strip():
        # check existing txt for placeholder markers
        txt = image.with_suffix(".txt")
        if txt.is_file():
            t = txt.read_text(encoding="utf-8", errors="replace")
            if "заглушка" in t.lower() or "уточнить" in t.lower():
                notes.append("placeholder")
        else:
            notes.append("placeholder")
    else:
        if "заглушка" in body.lower() or "[todo]" in body.lower():
            notes.append("placeholder")

    if "missing" in notes:
        status = "missing"
    elif "heavy" in notes and "weak" in notes:
        status = "heavy+weak"
    elif "heavy" in notes and "unused" in notes:
        status = "unused+heavy"
    elif "weak" in notes and "unused" in notes:
        status = "unused+weak"
    elif len(notes) == 1:
        status = notes[0]
    elif notes:
        status = "+".join(notes)
    else:
        status = "ok"

    todo = ""
    if "missing" in status:
        todo = "добавить файл"
    elif "weak" in status:
        todo = f"увеличить/заменить (≥{MIN_SHORT_SIDE}px короткой стороны)"
    elif "heavy" in status:
        todo = "сжать для web"
    elif "placeholder" in status:
        todo = "заполнить body"
    elif "unused" in status:
        todo = "подключить к галерее или убрать"

    return status, todo


def expand_row(raw: dict[str, str], html_srcs: set[str]) -> InventoryRow:
    key = raw["key"]
    photo = normalize_photo_stem(raw.get("photo", ""))
    row = InventoryRow(
        key=key,
        photo=photo,
        title=raw["title"],
        meta=raw["meta"],
        lead=raw["lead"],
        body=raw["body"],
        section=section_for_key(key),
    )

    text_only = is_text_only_key(key)
    cover_map = {**SERVICE_COVERS, **PROCESS_COVERS}

    if key in cover_map:
        row.role = "card"
        row.is_cover = "—"
        cover_stem = cover_map[key]
        # card may point cover via photo column, else default map
        cover_img, notes = resolve_image_path(
            photo=photo,
            key=key,
            key_stem=None if photo else cover_stem,
        )
        if not cover_img and not photo:
            cover_img = find_image(cover_stem)
        row.notes.extend(notes)
        if cover_img:
            row.image_path = rel_posix(cover_img)
            row.notes.append(f"cover→{row.image_path}")
        row.status = "ok"
        row.todo = "title/lead карточки; обложка через photo или cover-ключ"
        return row

    if text_only:
        row.role = "text"
        row.is_cover = "—"
        # optional: text row with photo (rare)
        if photo:
            image, notes = resolve_image_path(photo=photo, key=key, key_stem=None)
            row.notes.extend(notes)
            if image:
                row.image_path = rel_posix(image)
                row.txt_path = rel_posix(image.with_suffix(".txt"))
        blob = f"{row.title} {row.meta} {row.lead} {row.body}"
        if key in ("contact/phone", "contact/email", "contact/messengers") and (
            "example" in blob or "900" in blob or "уточнить" in blob.lower()
        ):
            row.status = "placeholder"
            row.todo = "реальные контакты"
        else:
            row.status = "ok"
        return row

    stem = media_stem_for_key(key)
    assert stem is not None
    image, notes = resolve_image_path(photo=photo, key=key, key_stem=stem)
    row.notes.extend(notes)

    if image:
        row.image_path = rel_posix(image)
        row.txt_path = rel_posix(image.with_suffix(".txt"))
        dims = image_dimensions(image)
        size = image.stat().st_size
        if dims:
            row.w, row.h = str(dims[0]), str(dims[1])
        row.kb = str(round(size / 1024, 1))
        on_site = row.image_path in html_srcs or any(
            row.image_path.lower() == s.lower() for s in html_srcs
        )
        # normalize HTML may use .jpg while file is .JPG
        if not on_site:
            for s in html_srcs:
                if Path(s).with_suffix("").as_posix().lower() == Path(row.image_path).with_suffix("").as_posix().lower():
                    on_site = True
                    break
        row.on_site = "yes" if on_site else "no"
        row.is_cover = "yes" if on_site else "no"
        row.role = "cover" if on_site else "gallery"
        row.alt = row.title or photo or stem.split("/")[-1]
        w = int(row.w) if row.w else None
        h = int(row.h) if row.h else None
        status, todo = classify_status(
            image=image,
            on_site=on_site,
            key=key,
            w=w,
            h=h,
            size=size,
            body=row.body,
            text_only=False,
        )
        if any(n.startswith("ambiguous") for n in row.notes):
            status = (status + "+ambiguous") if status != "ok" else "ambiguous"
            if not todo:
                todo = "уточнить уникальное имя photo"
        row.status = status
        row.todo = todo
    else:
        guess = photo or Path(stem).name
        row.image_path = f"photo/.../{guess}.jpg" if photo else f"photo/{stem}.jpg"
        row.txt_path = (
            rel_posix((PHOTO / stem).with_suffix(".txt"))
            if not photo
            else f"(рядом с найденным {guess}.jpg)"
        )
        row.on_site = "yes" if any((photo or stem) in s for s in html_srcs) else "no"
        row.is_cover = "yes" if row.on_site == "yes" else "no"
        row.role = "cover" if row.on_site == "yes" else "gallery"
        row.status = "missing"
        row.todo = (
            f"добавить файл с именем {photo}.* в photo/"
            if photo
            else "добавить изображение на диск или указать колонку photo"
        )

    return row


def expand_all(rows: list[dict[str, str]] | None = None) -> list[InventoryRow]:
    raw = rows if rows is not None else load_inventory()
    html_srcs = scan_html_image_srcs()
    return [expand_row(r, html_srcs) for r in raw]


FULL_FIELDNAMES = [
    "key",
    "photo",
    "section",
    "role",
    "is_cover",
    "title",
    "meta",
    "lead",
    "body",
    "image_path",
    "txt_path",
    "alt",
    "on_site",
    "w",
    "h",
    "kb",
    "status",
    "todo",
]


def write_csv_dicts(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> None:
    """Write CSV for Windows Excel: UTF-8 BOM + ';' delimiter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=CSV_ENCODING, newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter=CSV_DELIMITER,
            extrasaction="ignore",
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            doublequote=True,
            lineterminator="\r\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_full_csv(rows: list[InventoryRow], path: Path = FULL_CSV) -> None:
    out: list[dict[str, str]] = []
    for r in rows:
        d = asdict(r)
        d.pop("notes", None)
        out.append({k: ("" if d.get(k) is None else str(d.get(k))) for k in FULL_FIELDNAMES})
    write_csv_dicts(path, FULL_FIELDNAMES, out)


def write_minimal_csv(rows: list[dict[str, str]], path: Path = INVENTORY_CSV) -> None:
    write_csv_dicts(
        path,
        MINIMAL_FIELDS,
        [{k: r.get(k, "") for k in MINIMAL_FIELDS} for r in rows],
    )


def body_to_txt(row: InventoryRow) -> str:
    """Build sidecar .txt from minimal fields (free-form friendly)."""
    lines: list[str] = []
    if row.title:
        lines.append(row.title)
    if row.meta:
        lines.append(row.meta)
    if row.lead:
        lines.append("")
        lines.append(row.lead)
    if row.body:
        lines.append("")
        lines.append(row.body.strip())
    return "\n".join(lines).strip() + "\n"


def apply_bodies(rows: list[InventoryRow], *, dry_run: bool = False) -> list[str]:
    """Write .txt for media rows with non-empty body. Returns log lines."""
    log: list[str] = []
    for r in rows:
        if not r.image_path or r.status == "missing":
            continue
        if not r.body.strip():
            continue
        target = ROOT / r.txt_path if r.txt_path else Path(r.image_path).with_suffix(".txt")
        if not target.is_absolute():
            target = ROOT / target
        text = body_to_txt(r)
        if dry_run:
            log.append(f"DRY  write {target.relative_to(ROOT).as_posix()} ({len(text)} chars)")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            log.append(f"OK   write {target.relative_to(ROOT).as_posix()}")
    return log
