# AskMeNow

Учебный сервис вопросов и ответов. В ДЗ 2 страницы из ДЗ 1 перенесены в шаблоны Django. Вопросы и ответы берутся из демонстрационных данных, формы служат для показа верстки.

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

Откройте [localhost:8000](http://localhost:8000/). При необходимости можно скопировать `.env.example` в `.env` и изменить настройки. Для демонстрационных страниц миграции не требуются.

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
