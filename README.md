# 2026-VK-EDU-Web-11-Kanaev-A

Домашнее задание 1: статическая верстка сервиса вопросов и ответов (AskMeNow).

## Как открыть

Верстка полностью статическая, подключение внешних CDN не требуется (вся статика лежит локально в репозитории).

Открыть можно двумя способами:

1. Напрямую открыть файл `public/index.html` в браузере (двойным кликом).
2. Запустить локальный сервер через Python:
```bash
python -m http.server 8000
```
И открыть в браузере: `http://localhost:8000/public/index.html`

## Список страниц

Все сверстанные страницы находятся в папке `public/`:

- `index.html` — главная страница со списком вопросов, виджетами лайков и пагинацией
- `question.html` — страница вопроса со списком ответов, отметкой правильного ответа и формой
- `ask.html` — форма создания нового вопроса
- `login.html` — форма входа с сообщением об ошибке
- `signup.html` — форма регистрации с ошибкой валидации поля email
- `profile.html` — страница настроек профиля (с юзерблоком авторизованного пользователя)
- `hot.html` — популярные вопросы
- `tag.html` — вопросы по выбранному тегу
- `base.html` — базовый шаблон разметки

## Структура проекта

```text
2026-VK-EDU-Web-11-Kanaev-A/
├── .gitignore
├── README.md
└── public/
    ├── base.html
    ├── index.html
    ├── question.html
    ├── ask.html
    ├── login.html
    ├── signup.html
    ├── profile.html
    ├── hot.html
    ├── tag.html
    └── static/
        ├── css/
        │   ├── bootstrap.min.css
        │   └── custom.css
        ├── js/
        │   ├── bootstrap.bundle.min.js
        │   └── main.js
        └── img/
            ├── favicon.ico
            ├── favicon.svg
            ├── default-avatar.svg
            ├── avatar-user.svg
            ├── avatar1.svg
            ├── avatar2.svg
            └── avatar3.svg
```
