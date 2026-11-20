# AskMeNow

Учебный сервис вопросов и ответов на Django и PostgreSQL. Гости читают вопросы и ответы. После регистрации можно редактировать профиль, задавать вопросы, отвечать и голосовать. Автор вопроса может выбрать один верный ответ.

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

Compose ждёт готовности PostgreSQL, применяет миграции и собирает статику при запуске `web`. Nginx проксирует запросы в Django и раздаёт `/static/` и `/media/`. Сайт доступен на [localhost:8000](http://localhost:8000/), админка — на [localhost:8000/admin/](http://localhost:8000/admin/). `docker compose down` останавливает сервисы. База и загруженные аватары сохраняются в томах `postgres_data` и `media`.

При обновлении с ДЗ3 миграция сохраняет все ответы. Если у вопроса уже было несколько верных ответов, отмеченным останется самый ранний по дате создания, а при совпадении дат — по меньшему ID. Откат схемы не восстанавливает снятые отметки.

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

1. Зарегистрируйтесь на `/signup/` и откройте настройки профиля. Загрузите JPG, PNG или WebP до 2 МБ. После сохранения аватар виден в шапке и профиле.
2. Задайте вопрос на `/ask/`, укажите теги через запятую. В отдельной сессии войдите вторым пользователем, оставьте ответ и поставьте оценку вопросу и ответу. Смена лайка на дизлайк меняет рейтинг на два пункта.
3. Вернитесь к учётной записи автора вопроса, отметьте верный ответ и перезагрузите страницу. Отметка должна сохраниться. У второго пользователя кнопка выбора верного ответа отсутствует.
4. Нажмите «Выйти» на странице вопроса. Вы останетесь на ней, а кнопки голосования и публикации ответа станут недоступными.

При `DEBUG=True` доступна Django Debug Toolbar. В автоматических тестах панель выключена.

```bash
docker compose exec -T web python manage.py check
docker compose exec -T web python manage.py makemigrations --check --dry-run
docker compose exec -T web python manage.py test
```

Django создаёт отдельную тестовую базу PostgreSQL, поэтому пользователю БД нужны права `CREATEDB`.
