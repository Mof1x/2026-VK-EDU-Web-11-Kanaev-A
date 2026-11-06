from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.views.generic import TemplateView

from core.views import DemoFormView

from .mock_data import ANSWERS, QUESTIONS


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    try:
        return paginator.page(request.GET.get('page', 1))
    except (PageNotAnInteger, EmptyPage):
        return paginator.page(1)


class QuestionListView(TemplateView):
    template_name = 'questions/index.html'

    def get_questions(self):
        return QUESTIONS

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = paginate(self.get_questions(), self.request)
        return context


class HotQuestionListView(QuestionListView):
    template_name = 'questions/hot.html'

    def get_questions(self):
        return sorted(QUESTIONS, key=lambda question: question['rating'], reverse=True)


class TagQuestionListView(QuestionListView):
    template_name = 'questions/tag.html'

    def get_questions(self):
        tag = self.kwargs['tag']
        return [question for question in QUESTIONS if tag in question['tags']]


class QuestionDetailView(DemoFormView):
    template_name = 'questions/question.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_id = self.kwargs['question_id']
        question = next((item for item in QUESTIONS if item['id'] == question_id), None)
        if question is None:
            raise Http404('Вопрос не найден')

        context['question'] = question
        context['page'] = paginate(ANSWERS, self.request, per_page=2)
        return context


class AskView(DemoFormView):
    template_name = 'questions/ask.html'
