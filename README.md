# Galchanskiy Studio

Сайт студии по `spec.md` и `design.png`: Flask, Jinja2, HTML, CSS, локальные SVG и шрифты. Без базы данных, Node.js и внешних CDN. JavaScript не требуется: переходы, hover и плавная прокрутка реализованы CSS с учётом `prefers-reduced-motion`.

## Запуск

Нужен Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app wsgi run --host 127.0.0.1 --port 5000
```

Открыть http://127.0.0.1:5000. Debug по умолчанию выключен. В конфигурации и `.env.example` заданы `LIBRARY_URL=https://library.galchanskiy-studio.com` и `GITHUB_URL=https://github.com/GaLcHaNsKi`. Их можно переопределить в `.env`; при пустом URL Library показывает временную подпись, а GitHub скрыт. Разрешены абсолютные HTTP(S) адреса без учётных данных. Переменные окружения имеют приоритет над `.env`.

## Настройки и контент

- `app/config.py` — настройки и значения по умолчанию.
- `app/routes.py` — проекты, возможности тюнера и маршруты.
- `app/templates/` — шаблоны страниц; `app/static/css/style.css` — оформление.
- `STUDIO_NAME`, `LIBRARY_URL`, `GITHUB_URL` — название и ссылки.
- `GUITAR_TUNER_APK_PATH` — абсолютный путь либо путь от корня проекта. По умолчанию `guitar-tuner.apk` в корне проекта.
- `GUITAR_TUNER_VERSION=0.1.0`, `GUITAR_TUNER_MIN_ANDROID=8.0` — данные из AndroidManifest.xml предоставленного APK (minSdk 26).
- `GUITAR_TUNER_RELEASE_DATE` — необязательная дата выпуска, скрыта, пока не задана. Дата файла не используется как дата выпуска.
- `GUITAR_TUNER_SCREENSHOTS` в `app/config.py` — список путей относительно `app/static/`, например `('images/tuner-main.webp', 'images/tuner-bass.webp')`. Первый показывается в рамке телефона, остальные — в галерее. Используйте реальные скриншоты. Добавлен предоставленный скриншот `images/tuner-screenshot.jpg`. При пустом списке отображается временная заглушка.

Предоставленный `guitar-tuner.apk` находится в корне проекта и включён в Git. При развёртывании убедитесь, что он присутствует на сервере. Если в существующем `.env` указан старый путь, обновите `GUITAR_TUNER_APK_PATH` на `guitar-tuner.apk`. Если файл отсутствует, страница показывает «Скоро будет доступно», а маршрут скачивания возвращает 404. Размер вычисляется из файла. При обновлении замените APK атомарно и обновите версию в `.env`, затем перезапустите Gunicorn.

## Маршруты

| Адрес | Назначение |
| --- | --- |
| `/` | Главная |
| `/projects/guitar-tuner` | Страница Android-приложения |
| `/downloads/guitar-tuner.apk` | Скачивание локального APK, поддержка Range/HEAD и корректный Content-Disposition |
| `/health` | JSON `{"status":"ok"}` |

Отдельной страницы Library нет: её карточка ведёт прямо на настроенный сайт. APK не доступен через static; произвольные пути из запроса не принимаются. Cookies и аналитика не используются. CSP разрешает только локальные ресурсы. Статика кэшируется на сутки, APK требует перепроверки перед повторным использованием.

## Тесты

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Проверяются маршруты, кириллица, ссылки, отсутствие APK, содержимое и HTTP-заголовки скачивания, Range, отсутствие произвольной выдачи файлов, валидация URL, локальные ресурсы и настройки галереи. Результаты и ограничения проверки — в `TEST_RESULTS.md`.

## Развёртывание на Ubuntu / существующем VPS

Никакие настройки сервера автоматически не изменяются. Примеры в `deploy/` нужно адаптировать к свободному порту, пользователю, домену и месту установки. Не заменяйте конфигурации существующих приложений.

1. Скопируйте проект, создайте `.venv`, установите `requirements.txt`, заполните `.env` и загрузите APK. Пользователю процесса нужны права чтения проекта и APK.
2. Проверьте приложение вручную:

   ```bash
   .venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8010 wsgi:app
   curl --fail http://127.0.0.1:8010/health
   ```

3. Адаптируйте `deploy/galchanskiy-studio.service.example` и установите как отдельный systemd-сервис. После этого выполните `sudo systemctl daemon-reload` и `sudo systemctl enable --now galchanskiy-studio`.
4. Добавьте отдельный Nginx virtual host по `deploy/nginx.conf.example`, подключите его согласно принятой на сервере схеме. Проверьте `sudo nginx -t` перед `sudo systemctl reload nginx`.
5. Подключите HTTPS средствами, уже используемыми на VPS. Gunicorn должен оставаться на loopback. Flask debug и `flask run` не использовать в production.

Логи: `journalctl -u galchanskiy-studio -f`. Health-check: `/health`. Docker и дополнительные сервисы не нужны.

## Визуальная проверка

Контрольные ширины: 320, 375, 768, 1024, 1440 px. Проверить обе страницы, отсутствие горизонтального скролла, фокус клавиатуры, загрузку APK, режим reduced motion и работу без внешней сети. Декоративный редактор скрывается на телефонах; карточки становятся вертикальными. Указанные проверки в реальном браузере требуют отдельного прохода, если браузер недоступен в сессии агента.

Inter и JetBrains Mono распространяются локально в WOFF2; лицензии SIL Open Font License находятся рядом в `app/static/fonts/`.
