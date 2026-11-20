from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.urls import reverse


class TagQuerySet(models.QuerySet):
    def popular(self):
        return self.annotate(question_count=models.Count('questions')).order_by(
            '-question_count', 'name',
        )


class Tag(models.Model):
    name = models.CharField('название', max_length=100, unique=True)
    slug = models.SlugField('ярлык', max_length=120, unique=True, allow_unicode=True)

    objects = TagQuerySet.as_manager()

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('questions:tag', kwargs={'tag': self.slug})


def total_for(model, relation, aggregate):
    totals = model.objects.filter(**{relation: models.OuterRef('pk')}).order_by()
    totals = totals.values(relation).annotate(total=aggregate).values('total')
    return Coalesce(models.Subquery(totals), 0)


class QuestionQuerySet(models.QuerySet):
    def with_cards(self):
        return self.select_related('author__profile').prefetch_related('tags').annotate(
            rating=total_for(QuestionLike, 'question', models.Sum('value')),
            answer_count=total_for(Answer, 'question', models.Count('pk')),
        )

    def newest(self):
        return self.with_cards().order_by('-created_at', '-pk')

    def hottest(self):
        return self.with_cards().order_by('-rating', '-created_at', '-pk')

    def for_tag(self, tag):
        return self.filter(tags=tag).newest()


class Question(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='questions', verbose_name='автор',
    )
    title = models.CharField('заголовок', max_length=200)
    text = models.TextField('текст')
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='теги', blank=True)
    created_at = models.DateTimeField('дата создания', auto_now_add=True)

    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'
        indexes = [
            models.Index(fields=['-created_at', '-id'], name='question_latest_idx'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:question', kwargs={'question_id': self.pk})


class AnswerQuerySet(models.QuerySet):
    def for_question(self, question):
        return self.filter(question=question).select_related('author__profile').annotate(
            rating=total_for(AnswerLike, 'answer', models.Sum('value')),
        ).order_by('-is_correct', 'created_at', 'pk')


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answers', verbose_name='вопрос',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='answers', verbose_name='автор',
    )
    text = models.TextField('текст')
    is_correct = models.BooleanField('верный ответ', default=False)
    created_at = models.DateTimeField('дата создания', auto_now_add=True)

    objects = AnswerQuerySet.as_manager()

    class Meta:
        verbose_name = 'ответ'
        verbose_name_plural = 'ответы'
        indexes = [
            models.Index(fields=['question', '-is_correct', 'created_at', 'id'], name='answer_question_order_idx'),
        ]

    def __str__(self):
        return self.text[:80]


class VoteValue(models.IntegerChoices):
    LIKE = 1, 'Нравится'
    DISLIKE = -1, 'Не нравится'


class QuestionLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='question_votes', verbose_name='пользователь',
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='votes', verbose_name='вопрос',
    )
    value = models.SmallIntegerField('оценка', choices=VoteValue, default=VoteValue.LIKE)

    class Meta:
        verbose_name = 'оценка вопроса'
        verbose_name_plural = 'оценки вопросов'
        constraints = [
            models.UniqueConstraint(fields=['question', 'user'], name='unique_question_vote'),
            models.CheckConstraint(condition=models.Q(value__in=VoteValue.values), name='valid_question_vote'),
        ]

    def __str__(self):
        return f'{self.user.get_username()} → {self.question}'


class AnswerLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='answer_votes', verbose_name='пользователь',
    )
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name='votes', verbose_name='ответ',
    )
    value = models.SmallIntegerField('оценка', choices=VoteValue, default=VoteValue.LIKE)

    class Meta:
        verbose_name = 'оценка ответа'
        verbose_name_plural = 'оценки ответов'
        constraints = [
            models.UniqueConstraint(fields=['answer', 'user'], name='unique_answer_vote'),
            models.CheckConstraint(condition=models.Q(value__in=VoteValue.values), name='valid_answer_vote'),
        ]

    def __str__(self):
        return f'{self.user.get_username()} → {self.answer}'
