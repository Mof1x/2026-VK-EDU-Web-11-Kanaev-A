from django.shortcuts import get_object_or_404, render

from core.views import DemoFormView

from .models import Answer, Question, Tag
from .pagination import paginated_context


def render_question_list(request, template, questions, **context):
    return render(request, template, {**paginated_context(questions, request), **context})


def newest_questions(request):
    return render_question_list(request, 'questions/index.html', Question.objects.newest())


def hot_questions(request):
    return render_question_list(request, 'questions/hot.html', Question.objects.hottest())


def tagged_questions(request, tag):
    active_tag = get_object_or_404(Tag, slug=tag)
    return render_question_list(
        request, 'questions/tag.html', Question.objects.for_tag(active_tag), tag=active_tag,
    )


def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.with_cards(), pk=question_id)
    context = paginated_context(Answer.objects.for_question(question), request)
    return render(request, 'questions/question.html', {'question': question, **context})


class AskView(DemoFormView):
    template_name = 'questions/ask.html'
