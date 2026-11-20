from questions.models import Tag

from .models import Profile

TAG_COLORS = ('purple', 'red', 'green', 'blue', 'yellow', 'orange', 'muted')


def sidebar(request):
    popular_tags = Tag.objects.popular()[:12]
    return {
        'sidebar_tags': [
            (tag, f'tag-color-{TAG_COLORS[index % len(TAG_COLORS)]}')
            for index, tag in enumerate(popular_tags)
        ],
        'sidebar_members': Profile.objects.top_contributors()[:5],
    }
