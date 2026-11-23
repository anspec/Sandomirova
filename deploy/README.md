# Деплой sandomirova.anspec.ru

Статика на VPS `epd` (200.169.179.188), Caddy.

| Параметр | Значение |
|----------|----------|
| URL | https://sandomirova.anspec.ru |
| Корень на сервере | `/var/www/sandomirova.anspec.ru` |
| Caddy | `/etc/caddy/Caddyfile` (блок в `Caddyfile.snippet`) |
| SSH | `ssh epd` |

## Контент-таблица → проверка → деплой

Минимальная таблица текстов: `docs/content-inventory.csv` (UTF-8 BOM, разделитель `;` — для Excel на Windows)  
Описание ключей: `docs/content-inventory.md`

```powershell
# 1) восстановить полную таблицу + записать .txt из непустого body
python deploy/sync_from_content.py

# 2) валидатор путей/размеров (exit 1 при битых cover из HTML)
python deploy/validate_content.py --write-full

# 3) упаковка и выкладка
.\deploy\deploy.ps1
```

Только отчёт без записи `.txt`: `python deploy/sync_from_content.py --dry-run`

## Быстрый деплой (Windows)

```powershell
python deploy/download_photo1.py   # если photo1 ещё пустая
.\deploy\deploy.ps1
```

## Вручную

```bash
# из корня репозитория
python deploy/pack.py   # или tar index.html assets photo
scp /tmp/sandomirova-deploy.tgz epd:/tmp/
ssh epd "sudo mkdir -p /var/www/sandomirova.anspec.ru && sudo tar -xzf /tmp/sandomirova-deploy.tgz -C /var/www/sandomirova.anspec.ru"
ssh epd "sudo caddy validate --config /etc/caddy/Caddyfile && sudo systemctl reload caddy"
```

## Проверка

```bash
curl -sI https://sandomirova.anspec.ru/
```

Ожидается `HTTP/2 200`.
