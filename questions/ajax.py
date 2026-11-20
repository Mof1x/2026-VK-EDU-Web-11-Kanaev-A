from functools import wraps

from django.db import transaction
from django.http import JsonResponse
from django.views.csrf import csrf_failure as django_csrf_failure

from .forms import AcceptAnswerForm, VoteForm
from .models import Answer, Question


def json_error(message, status, *, errors=None):
    data = {'error': message}
    if errors:
        data['errors'] = errors
    return JsonResponse(data, status=status)


def authenticated_post(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.method != 'POST':
            response = json_error('Разрешён только запрос POST.', 405)
            response['Allow'] = 'POST'
            return response
        if not request.user.is_authenticated:
            return json_error('Войдите, чтобы выполнить это действие.', 401)
        return view(request, *args, **kwargs)

    return wrapped


def csrf_failure(request, reason=''):
    match = request.resolver_match
    if match and match.view_name in {
        'questions:question_vote', 'questions:answer_vote', 'questions:accept_answer',
    }:
        return json_error('Не удалось проверить запрос. Обновите страницу и попробуйте ещё раз.', 403)
    return django_csrf_failure(request, reason=reason)


def save_vote(request, model, pk):
    target = model.objects.filter(pk=pk).first()
    if target is None:
        return json_error('Объект не найден.', 404)
    form = VoteForm(request.POST)
    if not form.is_valid():
        return json_error('Недопустимая оценка.', 400, errors=form.errors.get_json_data())
    return JsonResponse(form.save(target=target, user=request.user))


@authenticated_post
def question_vote(request, question_id):
    return save_vote(request, Question, question_id)


@authenticated_post
def answer_vote(request, answer_id):
    return save_vote(request, Answer, answer_id)


@authenticated_post
@transaction.atomic
def accept_answer(request, question_id):
    question = Question.objects.select_for_update().filter(pk=question_id).first()
    if question is None:
        return json_error('Вопрос не найден.', 404)
    if question.author_id != request.user.pk:
        return json_error('Выбрать верный ответ может только автор вопроса.', 403)
    form = AcceptAnswerForm(request.POST, question=question)
    if not form.is_valid():
        return json_error('Ответ не относится к этому вопросу или не существует.', 400,
                          errors=form.errors.get_json_data())
    answer = form.save()
    return JsonResponse({'answer_id': answer.pk, 'is_correct': answer.is_correct})
