#!/usr/bin/env python3
"""Organize photo1 assets into photo/ folder structure with Latin names and .txt sidecars."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "photo1"
DST = ROOT / "photo"

# (source filename in photo1, destination subpath under photo/, latin filename)
COPY_MAP: list[tuple[str, str, str]] = [
    # hero
    ("1736333230546.jpg", "hero", "gothic-stained-glass-interior.jpg"),
    # services
    ("1736116005664.jpg", "services/mural-painting", "classical-mural-portrait.jpg"),
    ("sborka-6.jpg", "services/mosaic", "mosaic-panel-assembly.jpg"),
    ("img817.jpg", "services/mosaic", "monumental-mosaic-composition.jpg"),
    ("author-temp.jpg", "services/stained-glass", "botanical-glass-panel.jpg"),
    ("авторский витраж.jpg", "services/stained-glass", "author-stained-glass-sample.jpg"),
    ("витраж6.jpg", "services/stained-glass", "stained-glass-detail-06.jpg"),
    ("img866.jpg", "services/author-collections", "glass-vessels-collection.jpg"),
    ("1738351795137 (1).jpg", "services/author-collections", "glass-stone-sculpture.jpg"),
    ("IMG_0872.JPG", "services/light-compositions", "floral-glass-chandelier.jpg"),
    ("1771430755334 (1).jpg", "services/light-compositions", "amber-backlit-panels.jpg"),
    ("фонтан.jpg", "services/light-compositions", "decorative-fountain-element.jpg"),
    # process
    ("1735994272625.jpg", "process/idea-and-concept", "expo-85-concept-board.jpg"),
    ("1713017318716 (1).jpg", "process/idea-and-concept", "stained-glass-design-window.jpg"),
    ("1762622980818.jpg", "process/material", "glass-metal-material-samples.jpg"),
    ("1771491265419 (1).jpg", "process/material", "surface-texture-samples.jpg"),
    ("DSCN3883.JPG", "process/execution", "on-site-stained-glass-installation.jpg"),
    ("IMG_0330.JPG", "process/execution", "workspace-execution-detail.jpg"),
    ("1734371942405 (2).jpg", "process/execution", "large-format-work-in-progress.jpg"),
    ("IMG_20171010_233611.jpg", "process/acceptance", "completed-architectural-stained-glass.jpg"),
    ("1736333230546.jpg", "process/acceptance", "completed-vitrazh-interior.jpg"),
    # featured works
    ("IMG_20171010_233611.jpg", "featured-works", "abstract-stained-glass-facade.jpg"),
    ("DSC_1506.JPG", "featured-works", "interior-monumental-solution.jpg"),
    ("img866.jpg", "featured-works", "author-glass-objects.jpg"),
    ("1735994272625.jpg", "featured-works", "expo-85-tsukuba-glass.jpg"),
    ("author-temp.jpg", "featured-works", "vitrazh-botanical-ornament.jpg"),
    ("sborka-6.jpg", "featured-works", "mosaic-assembly-featured.jpg"),
    ("1738351795137 (1).jpg", "featured-works", "glass-stone-sculpture-featured.jpg"),
    ("1713017318716 (1).jpg", "featured-works", "urban-serenity-stained-glass.jpg"),
    ("1736116005664.jpg", "featured-works", "mural-portrait-featured.jpg"),
    ("витраж птицы.jpg", "featured-works", "vitrazh-birds-composition.jpg"),
    ("1771430755334 (1).jpg", "featured-works", "amber-light-panels-featured.jpg"),
    # about
    ("author-temp.jpg", "about", "author-photo-placeholder.jpg"),
    # professional recognition
    ("1735994272625.jpg", "professional-recognition", "expo-85-recognition-board.jpg"),
    ("CCI26042023 — копия.jpg", "professional-recognition", "diploma-copy-01.jpg"),
    ("CCI26042023_0001 — копия.jpg", "professional-recognition", "diploma-copy-02.jpg"),
    ("ландшафт.JPG", "professional-recognition", "professional-award-certificate.jpg"),
]

SECTION_TITLES = {
    "hero": "Hero — главный экран",
    "services/mural-painting": "Услуга — роспись",
    "services/mosaic": "Услуга — мозаика",
    "services/stained-glass": "Услуга — витраж",
    "services/author-collections": "Услуга — авторские коллекции",
    "services/light-compositions": "Услуга — композиции со светом",
    "process/idea-and-concept": "Процесс — идея и концепция",
    "process/material": "Процесс — материал",
    "process/execution": "Процесс — исполнение",
    "process/acceptance": "Процесс — приёмка",
    "featured-works": "Избранные работы",
    "about": "Обо мне",
    "professional-recognition": "Признание профессионального сообщества",
}


def latin_stem(name: str) -> str:
    return Path(name).stem


def build_txt(subpath: str, filename: str) -> str:
    section = SECTION_TITLES.get(subpath, subpath)
    title = latin_stem(filename).replace("-", " ").title()
    return f"""Название: {title}
Раздел: {section}

Заказчик: частный заказчик / организация (уточнить)
Задача: описать, какую архитектурную или эстетическую задачу решал проект
Особенности реализации: материалы, площадь, сроки, координация смежников, нестандартные решения
Результат: кратко — что получил заказчик и как работа интегрирована в пространство

Примечание: текст-заглушка для модального окна. Заменить на финальный комментарий по проекту.
"""


def resolve_source(name: str) -> Path | None:
    direct = SRC / name
    if direct.is_file():
        return direct
    # fallback: match by size for known Cyrillic if encoding differs
    return None


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Missing source folder: {SRC}")

    # fresh photo tree (keep nothing from old flat photo/)
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir()

    copied = 0
    for src_name, subpath, latin_name in COPY_MAP:
        src = resolve_source(src_name)
        if src is None:
            print(f"SKIP missing: {src_name}")
            continue
        dest_dir = DST / subpath
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / latin_name
        shutil.copy2(src, dest_file)
        txt_path = dest_dir / f"{latin_stem(latin_name)}.txt"
        txt_path.write_text(build_txt(subpath, latin_name), encoding="utf-8")
        copied += 1
        print(f"OK {subpath}/{latin_name}")

    readme = """# photo — assets by landing section

| Folder | Landing block |
|--------|----------------|
| `hero/` | Hero |
| `services/mural-painting/` | Роспись |
| `services/mosaic/` | Мозаика |
| `services/stained-glass/` | Витраж |
| `services/author-collections/` | Авторские коллекции |
| `services/light-compositions/` | Композиции со светом |
| `process/idea-and-concept/` | Идея и концепция |
| `process/material/` | Материал |
| `process/execution/` | Исполнение |
| `process/acceptance/` | Приёмка |
| `featured-works/` | Избранные работы |
| `about/` | Обо мне |
| `professional-recognition/` | Признание профессионального сообщества |

Each image has a same-name `.txt` file for modal project details.
"""
    (DST / "README.md").write_text(readme, encoding="utf-8")
    print(f"\nCopied {copied} images with .txt sidecars into {DST}")


if __name__ == "__main__":
    main()
