# Контент-таблица сайта (минимальная)

Источник правды для текстов: [`content-inventory.csv`](./content-inventory.csv).

**Windows / Excel:** UTF-8 **с BOM**, разделитель **`;`**, строки `\r\n`. Двойной щелчок в Проводнике должен показать кириллицу и отдельные колонки.

Пересобрать оба CSV:

```powershell
python deploy/rewrite_inventory_csv.py
# или
python deploy/validate_content.py --write-full
```

Если `content-inventory.full.csv` открыт в Excel — закройте его (файл блокируется). Временно актуальная полная таблица может лежать в `content-inventory.full.utf8.csv`.

## Колонки

| Колонка | Назначение |
|---------|------------|
| `key` | Ключ восстановления (логика блока сайта) |
| `photo` | **Уникальное имя файла фото без расширения** (см. ниже) |
| `title` | Заголовок / имя на карточке / в модалке |
| `meta` | Вторая строка (техника, год, роль…) |
| `lead` | Короткий текст карточки / lead секции |
| `body` | Длинный текст модалки / `.txt` рядом с фото |

Остальное (`image_path`, размеры, `on_site`, cover/gallery) **восстанавливается** скриптами в `deploy/`.

## Колонка `photo`

Добавьте в Excel столбец **`photo`** (после `key`).

- Пишите **только имя файла без расширения**, например: `gothic-stained-glass-interior`
- Не путь и не `.jpg` (если случайно укажете `.jpg` — парсер отрежет расширение)
- Имя должно быть **уникальным** в `photo/` (иначе статус `ambiguous`)
- Для текстовых строк без картинки оставьте ячейку пустой

Парсер ищет файл по проекту: сначала в `photo/`, затем `photo1/`, при необходимости шире. Находит `имя.jpg` / `.JPG` / `.jpeg` / `.png` / `.webp` и подставляет полный `image_path`. Парный `.txt` — рядом с найденным файлом.

Если `photo` пусто — запасной вариант: путь из `key` вида `featured-works/expo-85-tsukuba-glass` → `photo/featured-works/...`.

## Формат `key`

1. **Текст без фото** — логический путь: `hero/h1`, `contact/phone`, `services/title`, `process/thesis_1`…
2. **Карточка услуги / этапа** (title + lead): `services/mosaic`, `process/execution`… — обложку можно задать через `photo`
3. **Медиа-строка** — `key` остаётся логическим id блока; фактический файл задаётся колонкой **`photo`**

## Команды

```bash
# проверить пути и размеры
python deploy/validate_content.py

# восстановить полную таблицу + записать .txt из body (если body не пустой)
python deploy/sync_from_content.py

# только полная таблица, без записи файлов
python deploy/sync_from_content.py --dry-run
```

Перед деплоем: `validate_content.py` (exit ≠ 0 при битых cover-путях из HTML).

Сгенерированная полная таблица (не редактировать вручную): `content-inventory.full.csv`.
