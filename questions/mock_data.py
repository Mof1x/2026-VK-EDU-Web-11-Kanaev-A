QUESTION_EXAMPLES = [
    {
        'title': 'Как настроить маршрутизацию и отображение шаблонов?',
        'text': 'Возникли сложности с настройкой путей и передачей параметров в шаблон. '
                'Как лучше организовать каталоги с шаблонами и связать функции с URL?',
        'tags': ('web', 'python', 'django'),
        'author': 'Ivan Ivanov',
        'avatar': 'core/img/avatar1.svg',
        'rating': 5,
        'vote_state': '',
    },
    {
        'title': 'Как ускорить частые запросы к базе данных?',
        'text': 'При росте количества записей в таблице время ответа увеличивается. '
                'Какие индексы лучше использовать для ускорения выборки?',
        'tags': ('sql', 'backend', 'python'),
        'author': 'Dmitry Kozlov',
        'avatar': 'core/img/avatar2.svg',
        'rating': 9,
        'vote_state': 'voted-up',
    },
    {
        'title': 'Как подключить локальные стили и скрипты?',
        'text': 'Стили и скрипты должны подключаться локально. '
                'Как настроить раздачу статики в проекте?',
        'tags': ('html', 'css', 'bootstrap'),
        'author': 'Anna Petrova',
        'avatar': 'core/img/avatar3.svg',
        'rating': -2,
        'vote_state': 'voted-down',
    },
    {
        'title': 'Как развернуть веб-приложение на сервере?',
        'text': 'Приложение уже запускается на моём компьютере. '
                'Какие настройки нужны для запуска на сервере?',
        'tags': ('web', 'linux', 'git'),
        'author': 'Sergei Popov',
        'avatar': 'core/img/avatar1.svg',
        'rating': 4,
        'vote_state': '',
    },
    {
        'title': 'Как обновить часть страницы после запроса?',
        'text': 'Сервер возвращает данные в JSON. Как вывести их в списке на странице?',
        'tags': ('web', 'javascript', 'frontend'),
        'author': 'Alexei Smirnov',
        'avatar': 'core/img/avatar2.svg',
        'rating': 7,
        'vote_state': '',
    },
]

ANSWERS = [
    {
        'text': 'Попробуйте сначала воспроизвести проблему на небольшом примере.',
        'author': 'Alexei Smirnov',
        'avatar': 'core/img/avatar2.svg',
        'rating': 8,
        'vote_state': 'voted-up',
        'is_correct': True,
        'time': '3 часа назад',
    },
    {
        'text': 'Проверьте настройки проекта и сообщения в консоли при запуске.',
        'author': 'Anna Petrova',
        'avatar': 'core/img/avatar3.svg',
        'rating': 3,
        'time': '2 часа назад',
    },
    {
        'text': 'Посмотрите, есть ли похожий пример в документации.',
        'author': 'Sergei Popov',
        'avatar': 'core/img/avatar1.svg',
        'rating': 2,
        'time': '1 час назад',
    },
]

QUESTIONS = []
for index, question_id in enumerate(range(36, 0, -1)):
    example = QUESTION_EXAMPLES[index % len(QUESTION_EXAMPLES)]
    QUESTIONS.append({
        **example,
        'id': question_id,
        'title': f"{example['title']} (№{question_id})",
        'time': f'{index + 2} ч. назад',
        'answer_count': len(ANSWERS),
    })
