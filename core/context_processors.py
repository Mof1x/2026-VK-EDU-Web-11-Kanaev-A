SIDEBAR_TAGS = (
    ('web', 'tag-color-purple'),
    ('python', 'tag-color-red'),
    ('django', 'tag-color-green'),
    ('sql', 'tag-color-blue'),
    ('javascript', 'tag-color-yellow'),
    ('html', 'tag-color-orange'),
    ('css', 'tag-color-purple'),
    ('bootstrap', 'tag-color-blue'),
    ('git', 'tag-color-muted'),
    ('backend', 'tag-color-green'),
    ('frontend', 'tag-color-red'),
    ('linux', 'tag-color-muted'),
)

SIDEBAR_MEMBERS = (
    'Ivan Ivanov',
    'Alexei Smirnov',
    'Dmitry Kozlov',
    'Anna Petrova',
    'Sergei Popov',
)


def sidebar(request):
    return {
        'sidebar_tags': SIDEBAR_TAGS,
        'sidebar_members': SIDEBAR_MEMBERS,
    }
