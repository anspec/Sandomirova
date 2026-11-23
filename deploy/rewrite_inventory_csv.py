#!/usr/bin/env python3
"""Rewrite content-inventory CSV files for Windows Excel (UTF-8 BOM + ';')."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_lib import (  # noqa: E402
    FULL_CSV,
    INVENTORY_CSV,
    expand_all,
    write_full_csv,
    write_minimal_csv,
)

# Correct minimal rows (comma-safe; writer will quote as needed)
ROWS: list[dict[str, str]] = [
    {"key": "site/title", "title": "Тамара Владимировна Сандомирова — художник-монументалист", "meta": "", "lead": "", "body": ""},
    {
        "key": "site/description",
        "title": "",
        "meta": "",
        "lead": "",
        "body": "Монументально-декоративные решения для общественных и частных пространств: росписи, мозаики, витражи, авторские коллекции, объёмно-пространственные композиции со светом. Полный цикл проекта под одной ответственностью.",
    },
    {"key": "header/logo", "title": "Т. В. Сандомирова", "meta": "", "lead": "", "body": ""},
    {
        "key": "hero/h1",
        "title": "Монументально-декоративные решения для общественных и частных пространств",
        "meta": "",
        "lead": "",
        "body": "",
    },
    {
        "key": "hero/subtitle",
        "title": "Тамара Владимировна Сандомирова — художник-монументалист, руководитель проектов",
        "meta": "",
        "lead": "",
        "body": "",
    },
    {
        "key": "hero/tags",
        "title": "Росписи · мозаики · витражи · авторские коллекции · объёмно-пространственные композиции со светом",
        "meta": "",
        "lead": "",
        "body": "",
    },
    {"key": "hero/cta", "title": "Обсудить проект", "meta": "", "lead": "", "body": ""},
    {
        "key": "hero/gothic-stained-glass-interior",
        "title": "Gothic Stained Glass Interior",
        "meta": "Hero — главный экран",
        "lead": "",
        "body": "",
    },
    {"key": "services/title", "title": "Что создаю", "meta": "", "lead": "", "body": ""},
    {
        "key": "services/lead",
        "title": "",
        "meta": "",
        "lead": "Монументально-декоративные решения, интегрированные в архитектуру пространства",
        "body": "",
    },
    {
        "key": "services/mural-painting",
        "title": "Роспись",
        "meta": "",
        "lead": "Живопись на стенах, потолках и сложных архитектурных поверхностях",
        "body": "",
    },
    {
        "key": "services/mural-painting/classical-mural-portrait",
        "title": "Classical Mural Portrait",
        "meta": "Услуга — роспись",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/mosaic",
        "title": "Мозаика",
        "meta": "",
        "lead": "Долговечные фактурные панно из смальты, камня, стекла",
        "body": "",
    },
    {
        "key": "services/mosaic/mosaic-panel-assembly",
        "title": "Mosaic Panel Assembly",
        "meta": "Услуга — мозаика",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/mosaic/monumental-mosaic-composition",
        "title": "Monumental Mosaic Composition",
        "meta": "Услуга — мозаика",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/stained-glass",
        "title": "Витраж",
        "meta": "",
        "lead": "Световые акценты и зонирование через авторское стекло",
        "body": "",
    },
    {
        "key": "services/stained-glass/botanical-glass-panel",
        "title": "Botanical Glass Panel",
        "meta": "Услуга — витраж",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/stained-glass/author-stained-glass-sample",
        "title": "Author Stained Glass Sample",
        "meta": "Услуга — витраж",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/stained-glass/stained-glass-detail-06",
        "title": "Stained Glass Detail 06",
        "meta": "Услуга — витраж",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/author-collections",
        "title": "Авторские коллекции",
        "meta": "",
        "lead": "Серии декоративных элементов для единого стиля пространства",
        "body": "",
    },
    {
        "key": "services/author-collections/glass-vessels-collection",
        "title": "Glass Vessels Collection",
        "meta": "Услуга — авторские коллекции",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/author-collections/glass-stone-sculpture",
        "title": "Glass Stone Sculpture",
        "meta": "Услуга — авторские коллекции",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/light-compositions",
        "title": "Объёмно-пространственные композиции со светом",
        "meta": "",
        "lead": "Арт-объекты, интегрированные в архитектуру и освещение",
        "body": "",
    },
    {
        "key": "services/light-compositions/floral-glass-chandelier",
        "title": "Floral Glass Chandelier",
        "meta": "Услуга — композиции со светом",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/light-compositions/amber-backlit-panels",
        "title": "Amber Backlit Panels",
        "meta": "Услуга — композиции со светом",
        "lead": "",
        "body": "",
    },
    {
        "key": "services/light-compositions/decorative-fountain-element",
        "title": "Decorative Fountain Element",
        "meta": "Услуга — композиции со светом",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/title",
        "title": "Полный цикл — под одной ответственностью",
        "meta": "",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/intro",
        "title": "",
        "meta": "",
        "lead": "",
        "body": "Как руководитель проекта я отвечаю за каждый этап: концепцию, подбор и исполнение в материале, координацию исполнителей, контроль сроков и приёмку результата. Вы получаете предсказуемый результат в согласованные по каждому этапу сроки — без потери контроля над бюджетом.",
    },
    {
        "key": "process/thesis_1",
        "title": "Концепция",
        "meta": "",
        "lead": "Погружение в архитектуру пространства, эскиз и согласование идеи",
        "body": "",
    },
    {
        "key": "process/thesis_2",
        "title": "Материал и команда",
        "meta": "",
        "lead": "Подбор долговечных материалов, координация узкопрофильных исполнителей и смежников",
        "body": "",
    },
    {
        "key": "process/thesis_3",
        "title": "Сроки и приёмка",
        "meta": "",
        "lead": "Контроль графика, прозрачная отчётность, финальная приёмка объекта",
        "body": "",
    },
    {
        "key": "process/idea-and-concept",
        "title": "Идея и концепция",
        "meta": "шаг 1",
        "lead": "Эскиз, мудборд, привязка к архитектуре",
        "body": "",
    },
    {
        "key": "process/idea-and-concept/stained-glass-design-window",
        "title": "Stained Glass Design Window",
        "meta": "Процесс — идея и концепция",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/idea-and-concept/expo-85-concept-board",
        "title": "Expo 85 Concept Board",
        "meta": "Процесс — идея и концепция",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/material",
        "title": "Материал",
        "meta": "шаг 2",
        "lead": "Образцы фактур, согласование бюджета",
        "body": "",
    },
    {
        "key": "process/material/surface-texture-samples",
        "title": "Surface Texture Samples",
        "meta": "Процесс — материал",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/material/glass-metal-material-samples",
        "title": "Glass Metal Material Samples",
        "meta": "Процесс — материал",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/execution",
        "title": "Исполнение",
        "meta": "шаг 3",
        "lead": "Координация мастеров, строителей, электриков",
        "body": "",
    },
    {
        "key": "process/execution/on-site-stained-glass-installation",
        "title": "On-site Stained Glass Installation",
        "meta": "Процесс — исполнение",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/execution/large-format-work-in-progress",
        "title": "Large Format Work in Progress",
        "meta": "Процесс — исполнение",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/execution/workspace-execution-detail",
        "title": "Workspace Execution Detail",
        "meta": "Процесс — исполнение",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/acceptance",
        "title": "Приёмка",
        "meta": "шаг 4",
        "lead": "Контроль качества, сдача объекта в срок",
        "body": "",
    },
    {
        "key": "process/acceptance/completed-vitrazh-interior",
        "title": "Completed Vitrazh Interior",
        "meta": "Процесс — приёмка",
        "lead": "",
        "body": "",
    },
    {
        "key": "process/acceptance/completed-architectural-stained-glass",
        "title": "Completed Architectural Stained Glass",
        "meta": "Процесс — приёмка",
        "lead": "",
        "body": "",
    },
    {"key": "portfolio/title", "title": "Избранные работы", "meta": "", "lead": "", "body": ""},
    {
        "key": "portfolio/lead",
        "title": "",
        "meta": "",
        "lead": "Проекты для частных и общественных пространств — нажмите на работу, чтобы узнать подробнее",
        "body": "",
    },
    {
        "key": "portfolio/cta",
        "title": "Есть похожая задача?",
        "meta": "",
        "lead": "Расскажите о ней — подготовлю предложение.",
        "body": "",
    },
    {
        "key": "featured-works/abstract-stained-glass-facade",
        "title": "Abstract Stained Glass Facade",
        "meta": "Избранные работы",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/interior-monumental-solution",
        "title": "Interior Monumental Solution",
        "meta": "Избранные работы · частное пространство",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/mosaic-assembly-featured",
        "title": "Mosaic Assembly",
        "meta": "Избранные работы · мозаика",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/author-glass-objects",
        "title": "Author Glass Objects",
        "meta": "Избранные работы · коллекция",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/expo-85-tsukuba-glass",
        "title": "Expo 85 Tsukuba",
        "meta": "Япония · 1985 · художественное стекло",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/vitrazh-botanical-ornament",
        "title": "Vitrazh Botanical Ornament",
        "meta": "Избранные работы · витраж",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/urban-serenity-stained-glass",
        "title": "Urban Serenity Stained Glass",
        "meta": "Избранные работы · витраж",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/glass-stone-sculpture-featured",
        "title": "Glass and Stone Sculpture",
        "meta": "Избранные работы · авторский объект",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/amber-light-panels-featured",
        "title": "Amber Light Panels",
        "meta": "Избранные работы · свет",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/mural-portrait-featured",
        "title": "Mural Portrait",
        "meta": "Избранные работы · роспись",
        "lead": "",
        "body": "",
    },
    {
        "key": "featured-works/vitrazh-birds-composition",
        "title": "Vitrazh Birds Composition",
        "meta": "Избранные работы · витраж",
        "lead": "",
        "body": "",
    },
    {"key": "about/title", "title": "Обо мне", "meta": "", "lead": "", "body": ""},
    {"key": "about/name", "title": "Тамара Владимировна Сандомирова", "meta": "", "lead": "", "body": ""},
    {
        "key": "about/p1",
        "title": "",
        "meta": "",
        "lead": "",
        "body": "Я отвечаю за каждый этап лично — от первого эскиза до финальной приёмки. Это гарантирует целостность замысла и предсказуемый результат для заказчика.",
    },
    {
        "key": "about/p2",
        "title": "",
        "meta": "",
        "lead": "",
        "body": "Работаю с общественными и частными пространствами: от локальных акцентов до масштабных монументальных программ. Член Московского Союза художников.",
    },
    {"key": "about/stat_1", "title": "35+", "meta": "лет в монументальном искусстве", "lead": "", "body": ""},
    {
        "key": "about/stat_2",
        "title": "Expo 85",
        "meta": "участник мировой выставки, Япония",
        "lead": "",
        "body": "",
    },
    {"key": "about/stat_3", "title": "5", "meta": "направлений: от росписи до света", "lead": "", "body": ""},
    {
        "key": "about/author-photo-placeholder",
        "title": "Портрет автора",
        "meta": "Обо мне",
        "lead": "",
        "body": "",
    },
    {
        "key": "awards/title",
        "title": "Признание профессионального сообщества",
        "meta": "",
        "lead": "",
        "body": "",
    },
    {
        "key": "professional-recognition/expo-85-recognition-board",
        "title": "Expo 85 Цукuba Япония",
        "meta": "1985 · объекты из цветного хрусталя",
        "lead": "",
        "body": "",
    },
    {
        "key": "professional-recognition/diploma-copy-01",
        "title": "Диплом участника выставки",
        "meta": "Союз художников",
        "lead": "",
        "body": "",
    },
    {
        "key": "professional-recognition/professional-award-certificate",
        "title": "Почётная грамота",
        "meta": "Профессиональное сообщество",
        "lead": "",
        "body": "",
    },
    {
        "key": "professional-recognition/Pavilion_australia",
        "title": "Pavilion Australia / Expo",
        "meta": "",
        "lead": "",
        "body": (
            "Всемирная выставка Экспо 85 город Брезбен. Австралия. Советский павильон «Отдых в эпоху технологии».\n"
            "Заказчик: Министерство стекольной промышленности СССР\n"
            "Задача: Создание единого дизайн-пространства для авторских объектов из цветного стекла в гутной технике. "
            "Необходимо учесть тематику выставки: природа, экология окружающей среды, создав монументальные объекты в цветном стекле. "
            "Разместить объекты в круговом бассейне, отделяющем подиум для модных показов от проходной зоны. "
            "Показать возможности стекольного производства, работу советских мастеров стеклодувов.\n"
            "Особенности реализации: Увеличенные размеры частей объектов, сложности в работе с большими массами расплавленного стекла "
            "при отливке в чугунные формы, количество объектов. Окраска стекла в массе редкоземельными красителями, "
            "увеличение времени отжига изделий, сжатые сроки исполнения.\n"
            "Результат: продуманный интерьер со встроенными авторскими объектами в форме осенних листьев из яркого цветного стекла "
            "в круговом бассейне с подсветкой; шары из бесцветного стекла, напоминающие капли воды; зонирование проходной зоны."
        ),
    },
    {
        "key": "professional-recognition/landshaft",
        "title": "Ландшафтный дизайн. Архитектура малых форм.",
        "meta": "",
        "lead": "Комплексные ландшафтные проекты общественных, частных пространств, парков, придворовых территорий.",
        "body": (
            "Заказчик: Государственные учреждения, частный заказчик\n"
            "Задача: Создание единого дизайн-пространства от эргономичного сочетания интерьера с ландшафтным дизайном, "
            "устройством фонтанов, архитектуры малых форм в сочетании с посадками крупномерных деревьев, цветов и кустарников. "
            "Решение ландшафтного освещения.\n"
            "Особенности реализации: фонтаны, сухие ручьи над дренажной системой, формы и декоративные элементы фасадов, "
            "МАФ для сбора верховодки, зимние посадки крупномеров, координация смежников, ландшафтное освещение, декоративное ограждение.\n"
            "Результат: гармоничная завершённая среда; решены утилитарные задачи; улучшен микроклимат; "
            "пространственное зонирование и МАФ; палитра за счёт смены цветения."
        ),
    },
    {
        "key": "contact/title",
        "title": "Если у вас есть идея проекта — готова обсудить план",
        "meta": "",
        "lead": "",
        "body": "",
    },
    {
        "key": "contact/lead",
        "title": "",
        "meta": "",
        "lead": "",
        "body": "Расскажите о цели, задачах, площади и сроках. Приложите вспомогательные файлы — подготовлю предложение.",
    },
    {
        "key": "contact/name",
        "title": "Тамара Владимировна Сандомирова",
        "meta": "Художник-монументалист · руководитель проектов",
        "lead": "",
        "body": "",
    },
    {"key": "contact/phone", "title": "+7 (900) 000-00-00", "meta": "tel:+79000000000", "lead": "", "body": ""},
    {"key": "contact/email", "title": "info@example.ru", "meta": "mailto:info@example.ru", "lead": "", "body": ""},
    {
        "key": "contact/messengers",
        "title": "Telegram · WhatsApp",
        "meta": "",
        "lead": "уточнить контакты",
        "body": "",
    },
    {
        "key": "contact/form_hint",
        "title": "",
        "meta": "",
        "lead": "Отвечу в течение одного рабочего дня",
        "body": "",
    },
    {
        "key": "contact/privacy",
        "title": "",
        "meta": "",
        "lead": "",
        "body": "Нажимая «Отправить», вы соглашаетесь на обработку персональных данных.",
    },
    {
        "key": "footer/name",
        "title": "Тамара Владимировна Сандомирова",
        "meta": "Художник-монументалист · руководитель проектов",
        "lead": "",
        "body": "",
    },
    {"key": "footer/year", "title": "© 2026", "meta": "", "lead": "", "body": ""},
]


def main() -> int:
    write_minimal_csv(ROWS, INVENTORY_CSV)
    print(f"Wrote {INVENTORY_CSV} BOM={INVENTORY_CSV.read_bytes()[:3] == b'\\xef\\xbb\\xbf'!s}")
    bom = INVENTORY_CSV.read_bytes()[:3] == bytes([0xEF, 0xBB, 0xBF])
    print(f"  utf-8-sig BOM: {bom}")
    print(f"  header: {INVENTORY_CSV.read_text(encoding='utf-8-sig').splitlines()[0]}")

    expanded = expand_all(ROWS)
    targets = [FULL_CSV, FULL_CSV.with_name("content-inventory.full.utf8.csv")]
    for path in targets:
        try:
            write_full_csv(expanded, path)
            print(f"Wrote {path.relative_to(INVENTORY_CSV.parent.parent)}")
        except PermissionError:
            print(f"LOCKED skip {path.name} — закройте файл в Excel и запустите снова")
    # prefer single full name: remove alt if main succeeded
    alt = FULL_CSV.with_name("content-inventory.full.utf8.csv")
    if FULL_CSV.is_file() and FULL_CSV.read_bytes()[:3] == bytes([0xEF, 0xBB, 0xBF]):
        if alt.is_file() and alt != FULL_CSV:
            try:
                alt.unlink()
            except OSError:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
