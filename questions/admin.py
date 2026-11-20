from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.forms import BaseInlineFormSet
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.html import format_html

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


ANSWER_INLINE_LIMIT = 20


class AnswerInlineFormSet(BaseInlineFormSet):
    @cached_property
    def visible_answers(self):
        # Django's base formset has already filtered by the current question.
        return super().get_queryset()[:ANSWER_INLINE_LIMIT]

    def get_queryset(self):
        return self.visible_answers


class AnswerInline(admin.TabularInline):
    model = Answer
    formset = AnswerInlineFormSet
    extra = 0
    readonly_fields = ('author', 'created_at')
    verbose_name_plural = f'Ответы (первые {ANSWER_INLINE_LIMIT})'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').order_by('pk')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('created_at',)
    list_select_related = ('author',)
    autocomplete_fields = ('author', 'tags')
    inlines = (AnswerInline,)
    ordering = ('-created_at', '-pk')
    show_full_result_count = False

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and (
            request.user.has_perm('questions.view_answer')
            or request.user.has_perm('questions.change_answer')
        ):
            return (*fields, 'answers_list')
        return fields

    @admin.display(description='Все ответы')
    def answers_list(self, obj):
        url = reverse('admin:questions_answer_changelist', query={'question__id__exact': obj.pk})
        return format_html('<a href="{}">Открыть все ответы на этот вопрос</a>', url)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_correct', 'created_at')
    search_fields = ('text', 'question__title', 'author__username')
    list_filter = ('is_correct', 'created_at')
    list_select_related = ('question', 'author')
    autocomplete_fields = ('question', 'author')
    show_full_result_count = False


class VoteAdmin(admin.ModelAdmin):
    list_filter = ('value',)
    show_full_result_count = False


@admin.register(QuestionLike)
class QuestionLikeAdmin(VoteAdmin):
    list_display = ('id', 'question', 'user', 'value')
    search_fields = ('question__title', 'user__username')
    list_select_related = ('question', 'user')
    autocomplete_fields = ('question', 'user')


@admin.register(AnswerLike)
class AnswerLikeAdmin(VoteAdmin):
    list_display = ('id', 'answer', 'user', 'value')
    search_fields = ('answer__text', 'user__username')
    list_select_related = ('answer', 'user')
    autocomplete_fields = ('answer', 'user')


class HasQuestionsFilter(admin.SimpleListFilter):
    title = 'вопросы'
    parameter_name = 'has_questions'

    def lookups(self, request, model_admin):
        return [('yes', 'Есть вопросы'), ('no', 'Нет вопросов')]

    def queryset(self, request, queryset):
        if self.value() in ('yes', 'no'):
            links = Question.tags.through.objects.filter(tag_id=OuterRef('pk'))
            has_questions = Exists(links)
            return queryset.filter(has_questions if self.value() == 'yes' else ~has_questions)
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    list_filter = (HasQuestionsFilter,)
    prepopulated_fields = {'slug': ('name',)}
