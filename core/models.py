from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


def avatar_path(instance, filename):
    return f'avatars/{uuid4().hex}{Path(filename).suffix.lower()}'


def validate_avatar_size(file):
    if file.size > 2 * 1024 * 1024:
        raise ValidationError('Размер аватара не должен превышать 2 МБ.')


avatar_validators = [
    FileExtensionValidator(
        ['jpg', 'jpeg', 'png', 'webp'],
        message='Разрешены только изображения JPG, PNG и WebP.',
    ),
    validate_avatar_size,
]


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
    avatar = models.ImageField('аватар', upload_to=avatar_path, blank=True, validators=avatar_validators)

    objects = ProfileQuerySet.as_manager()

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return self.user.get_username()
