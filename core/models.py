from django.conf import settings
from django.db import models


class ProfileQuerySet(models.QuerySet):
    def top_contributors(self):
        return self.select_related('user').annotate(
            question_count=models.Count('user__questions'),
        ).filter(question_count__gt=0).order_by('-question_count', 'user__username')


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile', verbose_name='пользователь',
    )
    avatar = models.ImageField('аватар', upload_to='avatars/', blank=True)

    objects = ProfileQuerySet.as_manager()

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return self.user.get_username()
