from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import AnswerForm, QuestionForm
from .models import Answer, Question, Tag
from .pagination import PAGE_SIZE, paginated_context


def render_question_list(request, template, questions, **context):
    questions = questions.with_viewer_vote(request.user)
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


@login_required
@require_http_methods(['POST'])
def submit_answer(request, question_id):
    return render_question(request, question_id, AnswerForm(request.POST))


@require_http_methods(['GET', 'HEAD', 'POST'])
def question_detail(request, question_id):
    if request.method == 'POST':
        return submit_answer(request, question_id)
    return render_question(request, question_id, AnswerForm())


def render_question(request, question_id, form):
    question = get_object_or_404(
        Question.objects.with_cards().with_viewer_vote(request.user), pk=question_id,
    )
    if form.is_bound and form.is_valid():
        answer = form.save(author=request.user, question=question)
        page = Answer.objects.page_for(answer, PAGE_SIZE)
        return redirect(f'{question.get_absolute_url()}?page={page}#answer-{answer.pk}')
    answers = Answer.objects.for_question(question).with_viewer_vote(request.user)
    context = paginated_context(answers, request)
    return render(request, 'questions/question.html', {
        'question': question, 'form': form,
        'can_accept_answer': request.user.pk == question.author_id,
        **context,
    })


@login_required
@require_http_methods(['GET', 'POST'])
def ask(request):
    form = QuestionForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        return redirect(form.save(author=request.user))
    return render(request, 'questions/ask.html', {'form': form})
