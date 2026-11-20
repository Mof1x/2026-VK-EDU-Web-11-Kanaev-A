# AskMeNow

Учебный сервис вопросов и ответов. В ДЗ3 списки вопросов, страницы тегов и ответы читаются из PostgreSQL. Данные можно добавлять через админку или командой `fill_db`. Публичные страницы предназначены для просмотра.

## Настройка окружения

Скопируйте `.env.example` в `.env.docker` и `.env.local`. Для каждого файла заполните `SECRET_KEY` случайной строкой, а в `POSTGRES_PASSWORD` задайте пароль базы. Если оба способа запуска используют один PostgreSQL, значения `POSTGRES_DB`, `POSTGRES_USER` и `POSTGRES_PASSWORD` должны совпадать.

- В `.env.docker` установите `DB_HOST=db` и `DB_PORT=5432`.
- В `.env.local` оставьте `DB_HOST=127.0.0.1` и укажите порт локального PostgreSQL.

Случайные значения можно получить командой `python -c "import secrets; print(secrets.token_urlsafe(50))"` (на Linux/macOS также `python3`). Если установлен только Docker, используйте `docker run --rm python:3.14-slim python -c "import secrets; print(secrets.token_urlsafe(50))"`.

## Запуск через Docker Compose

Выполните из корня проекта:

```bash
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Compose ждёт готовности PostgreSQL и применяет миграции при запуске `web`. Сайт доступен на [localhost:8000](http://localhost:8000/), админка — на [localhost:8000/admin/](http://localhost:8000/admin/). `docker compose down` останавливает сервисы. Данные PostgreSQL сохраняются в томе `postgres_data`.

## Запуск Django напрямую

Нужен Python 3.12+ и запущенный PostgreSQL с базой и учётными данными из `.env.local`. Чтобы запустить только PostgreSQL через Docker, выполните `docker compose up -d --wait db`. В этом режиме Django запускается снаружи контейнера, используйте совпадающие настройки PostgreSQL в обоих `.env` файлах.

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

## Демонстрационные данные

Сразу после миграций можно открыть сайт и проверить пустые списки. Чтобы добавить небольшой набор выполните:

```bash
docker compose exec web python manage.py fill_db 20
```

При локальном запуске используйте `python manage.py fill_db 20` из виртуального окружения. Команда добавляет `ratio` пользователей, профилей и тегов, `ratio × 10` вопросов, `ratio × 100` ответов и `ratio × 200` оценок. Минимальный `ratio` равен `2` из-за ограничения на уникальные оценки. Без аргумента команда использует `10001`, чтобы превысить все пороги ДЗ3. Каждый запуск добавляет новый набор, для полной проверки запустите команду на пустой базе.

После заполнения откройте `/`, `/hot/`, выберите тег в боковой панели и откройте отдельный вопрос. У части вопросов есть вторая страница ответов, у части ответов пока нет.

## Проверки

При `DEBUG=True` на локальном сайте доступна Django Debug Toolbar. Запустите `python manage.py check` для проверки настроек и `python manage.py test` для проверки моделей, страниц, админки и генератора. Django создаёт отдельную тестовую базу PostgreSQL, поэтому пользователю БД нужны права `CREATEDB`. В Docker эти команды можно выполнять с префиксом `docker compose exec web`.
