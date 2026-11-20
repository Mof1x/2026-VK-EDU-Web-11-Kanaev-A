from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from questions.models import Answer, Question

from .models import Profile


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(username='admin')
        Profile.objects.create(user=cls.admin_user)
        cls.question = Question.objects.create(author=cls.admin_user, title='Вопрос', text='Текст')
        cls.answer = Answer.objects.create(question=cls.question, author=cls.admin_user, text='Ответ')

    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'
        self.client.force_login(self.admin_user)

    def test_all_models_have_admin_list_and_add_pages(self):
        for model in ('core_profile', 'questions_question', 'questions_answer',
                      'questions_tag', 'questions_questionlike', 'questions_answerlike'):
            for view in ('changelist', 'add'):
                with self.subTest(model=model, view=view):
                    self.assertEqual(self.client.get(reverse(f'admin:{model}_{view}')).status_code, 200)

    def test_user_and_question_forms_display_inlines(self):
        for route, pk, model in (
            ('admin:auth_user_change', self.admin_user.pk, Profile),
            ('admin:questions_question_change', self.question.pk, Answer),
        ):
            response = self.client.get(reverse(route, args=[pk]))
            self.assertEqual(response.status_code, 200)
            formset, = response.context['inline_admin_formsets']
            self.assertIs(formset.formset.model, model)
            self.assertEqual(formset.formset.initial_form_count(), 1)

    def test_question_with_many_answers_can_be_saved_and_all_answers_are_listed(self):
        Answer.objects.bulk_create([
            Answer(question=self.question, author=self.admin_user, text='Ответ')
            for _ in range(399)
        ])
        other_question = Question.objects.create(author=self.admin_user, title='Другой', text='Текст')
        Answer.objects.create(question=other_question, author=self.admin_user, text='Другой ответ')
        url = reverse('admin:questions_question_change', args=[self.question.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        formset = response.context['inline_admin_formsets'][0].formset
        self.assertEqual(formset.initial_form_count(), 20)

        answers_url = reverse(
            'admin:questions_answer_changelist',
            query={'question__id__exact': self.question.pk},
        )
        self.assertContains(response, f'href="{answers_url}"')
        answers = self.client.get(answers_url)
        self.assertEqual(answers.status_code, 200)
        self.assertEqual(answers.context['cl'].result_count, 400)

        data = {
            'author': self.admin_user.pk,
            'title': 'Новый заголовок',
            'text': self.question.text,
            '_save': '1',
        }
        data.update({
            field.html_name: field.value()
            for field in formset.management_form
        })
        for form in formset.initial_forms:
            data.update({
                form.add_prefix('id'): form.instance.pk,
                form.add_prefix('question'): self.question.pk,
                form.add_prefix('text'): form.instance.text,
            })
        data[formset.initial_forms[0].add_prefix('text')] = 'Изменённый ответ'
        saved = self.client.post(url, data)
        self.assertEqual(saved.status_code, 302)
        self.question.refresh_from_db()
        self.answer.refresh_from_db()
        self.assertEqual(self.question.title, 'Новый заголовок')
        self.assertEqual(self.answer.text, 'Изменённый ответ')
        self.assertEqual(self.question.answers.count(), 400)
