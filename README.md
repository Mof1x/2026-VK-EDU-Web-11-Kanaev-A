# AskMeNow

Учебный сервис вопросов и ответов. В ДЗ 2 страницы из ДЗ 1 перенесены в шаблоны Django. Вопросы и ответы берутся из демонстрационных данных, формы служат для показа верстки.

## Настройка перед запуском

Скопируйте `.env.example` в `.env` (`Copy-Item .env.example .env` в PowerShell или `cp .env.example .env` в Linux/macOS).

Сгенерируйте ключ командой ниже и вставьте результат после `SECRET_KEY=` в `.env`.

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Если Python доступен как `python3`, используйте это имя. Если запускаете проект только через Docker, сгенерируйте ключ командой `docker run --rm python:3.14-slim python -c "import secrets; print(secrets.token_urlsafe(50))"`.

Для локального запуска оставьте `DEBUG=True` и `ALLOWED_HOSTS=localhost,127.0.0.1`. Проект требует все три переменные. Для `DEBUG` допустимы `True` и `False`.

## Локальный запуск

Понадобится Python 3.12 или новее. Выполняйте команды из корня проекта.

### Windows (PowerShell)

Активация окружения не нужна: команды обращаются к Python внутри `.venv` напрямую.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py runserver
```

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py runserver
```

Откройте [localhost:8000](http://localhost:8000/). Для демонстрационных страниц миграции не требуются.

Остановка сервера: `Ctrl+C`. Для работы с `/admin/` сначала выполните миграции: `python manage.py migrate` (используйте Python из созданного окружения).

## Запуск через Docker Compose

Нужен установленный и запущенный Docker Desktop (на Windows) или Docker Engine с Compose (на Linux).

```bash
docker compose up --build
```

Сайт будет доступен по адресу [localhost:8000](http://localhost:8000/).

## Страницы

- `/` — новые вопросы
- `/hot/` — популярные вопросы
- `/tag/python/` — вопросы по тегу
- `/question/35/` — вопрос и ответы
- `/ask/` — форма создания вопроса
- `/login/` — форма входа
- `/signup/` — форма регистрации
- `/profile/` — форма настроек профиля
