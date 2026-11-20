from uuid import uuid4

from django import forms
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils.text import slugify

from core.forms import StyledFieldsMixin

from .models import Answer, Question, Tag, VoteValue


class QuestionForm(StyledFieldsMixin, forms.ModelForm):
    tags_text = forms.CharField(
        label='Теги',
        required=False,
        help_text='До трёх тегов через запятую.',
        max_length=302,
    )

    class Meta:
        model = Question
        fields = ('title', 'text', 'tags_text')
        widgets = {'text': forms.Textarea(attrs={'rows': 7})}

    def clean_tags_text(self):
        names = dict.fromkeys(
            ' '.join(name.split()).casefold()
            for name in self.cleaned_data['tags_text'].split(',')
            if name.strip()
        )
        if len(names) > 3:
            raise forms.ValidationError('Укажите не больше трёх тегов.')
        if any(len(name) > 100 or not slugify(name, allow_unicode=True) for name in names):
            raise forms.ValidationError('Каждый тег должен содержать буквы или цифры и быть не длиннее 100 символов.')
        return list(names)

    @staticmethod
    def get_tag(name):
        existing = Tag.objects.filter(name__iexact=name).order_by('pk').first()
        if existing:
            return existing
        slug = slugify(name, allow_unicode=True)
        try:
            return Tag.objects.get_or_create(name=name, defaults={'slug': slug})[0]
        except IntegrityError:
            # Distinct names such as «C++» and «C#» can produce the same slug.
            unique_slug = f'{slug}-{uuid4().hex[:12]}'
            return Tag.objects.get_or_create(name=name, defaults={'slug': unique_slug})[0]

    @transaction.atomic
    def save(self, *, author):
        question = super().save(commit=False)
        question.author = author
        question.save()
        question.tags.set([self.get_tag(name) for name in self.cleaned_data['tags_text']])
        return question


class AnswerForm(StyledFieldsMixin, forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {'text': forms.Textarea(attrs={'rows': 4})}

    def save(self, *, author, question):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question
        answer.save()
        return answer


class VoteForm(forms.Form):
    value = forms.TypedChoiceField(choices=VoteValue.choices, coerce=int)

    @transaction.atomic
    def save(self, *, target, user):
        value = self.cleaned_data['value']
        target.votes.update_or_create(user=user, defaults={'value': value})
        rating = target.votes.aggregate(total=Sum('value', default=0))['total']
        return {'rating': rating, 'value': value}


class AcceptAnswerForm(forms.Form):
    answer_id = forms.IntegerField(min_value=1, max_value=2**63 - 1)

    def __init__(self, *args, question, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question

    def clean_answer_id(self):
        answer = self.question.answers.filter(pk=self.cleaned_data['answer_id']).first()
        if answer is None:
            raise forms.ValidationError('У этого вопроса нет такого ответа.')
        return answer

    def save(self):
        answer = self.cleaned_data['answer_id']
        self.question.answers.filter(is_correct=True).exclude(pk=answer.pk).update(is_correct=False)
        if not answer.is_correct:
            answer.is_correct = True
            answer.save(update_fields=['is_correct'])
        return answer
