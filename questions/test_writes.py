from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from .models import Answer, AnswerLike, Question, QuestionLike, Tag

User = get_user_model()


class QuestionWriteTests(TestCase):
    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'
        self.author = User.objects.create_user(username='author')
        self.reader = User.objects.create_user(username='reader')
        self.question = Question.objects.create(author=self.author, title='Первый вопрос', text='Текст')

    def test_ask_for_guest_and_create_question_with_existing_tag(self):
        self.assertRedirects(self.client.get('/ask/'), '/login/?next=/ask/')
        self.assertContains(self.client.get('/'), 'Войдите, чтобы задать вопрос')
        self.client.force_login(self.author)
        old_tag = Tag.objects.create(name='Python', slug='python')
        fields = {'title': 'Новый вопрос', 'text': 'Текст нового вопроса'}
        response = self.client.post('/ask/', {**fields, 'tags_text': 'one,two,three,four'})
        self.assertIn('tags_text', response.context['form'].errors)
        self.assertContains(response, 'Новый вопрос')

        response = self.client.post('/ask/', {
            **fields, 'tags_text': 'Python, python, Django', 'author': self.reader.pk,
        })
        created = Question.objects.get(title=fields['title'])
        self.assertRedirects(response, created.get_absolute_url())
        self.assertEqual(created.author_id, self.author.pk)
        self.assertEqual(set(created.tags.values_list('name', flat=True)), {'Python', 'django'})
        self.assertTrue(created.tags.filter(pk=old_tag.pk).exists())

    def test_answer_post_redirects_to_correct_page_and_anchor(self):
        url = self.question.get_absolute_url()
        self.assertContains(self.client.get(url), 'Войдите, чтобы добавить ответ')
        self.assertRedirects(self.client.post(url, {'text': 'Гость'}), f'/login/?next={url}')
        self.client.force_login(self.reader)
        self.assertIn('text', self.client.post(url, {'text': ' '}).context['form'].errors)
        Answer.objects.bulk_create([
            Answer(question=self.question, author=self.author, text='Старый ответ', is_correct=(index == 3))
            for index in range(10)
        ])
        response = self.client.post(url, {'text': 'Новый ответ', 'author': self.author.pk})
        answer = Answer.objects.get(text='Новый ответ')
        self.assertEqual(answer.author_id, self.reader.pk)
        self.assertRedirects(response, f'{url}?page=2#answer-{answer.pk}')
        self.assertContains(self.client.get(f'{url}?page=2'), f'id="answer-{answer.pk}"')


class QuestionAjaxTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author')
        cls.reader = User.objects.create_user(username='reader')
        cls.question = Question.objects.create(author=cls.author, title='Тема', text='Текст')
        cls.answer = Answer.objects.create(question=cls.question, author=cls.reader, text='Ответ')

    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'

    def test_vote_question_and_answer_is_idempotent_and_can_change(self):
        self.client.force_login(self.reader)
        for route, obj, model in (
            ('questions:question_vote', self.question, QuestionLike),
            ('questions:answer_vote', self.answer, AnswerLike),
        ):
            with self.subTest(route=route):
                url = reverse(route, args=[obj.pk])
                for value in (1, 1, -1):
                    response = self.client.post(url, {'value': value})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json(), {'rating': value, 'value': value})
                    self.assertEqual(model.objects.filter(user=self.reader).count(), 1)
                self.assertEqual(self.client.post(url, {'value': 0}).status_code, 400)
        self.assertContains(self.client.get(self.question.get_absolute_url()), 'voted-down', count=2)

    def test_ajax_requires_post_session_csrf_and_existing_object(self):
        url = reverse('questions:question_vote', args=[self.question.pk])
        client = Client(enforce_csrf_checks=True, HTTP_HOST='localhost')
        response = client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], 'POST')
        client.get('/login/')
        headers = {'X-CSRFToken': client.cookies['csrftoken'].value}
        self.assertEqual(client.post(url, {'value': 1}, headers=headers).status_code, 401)
        client.force_login(self.reader)
        missing_csrf = client.post(url, {'value': 1})
        self.assertEqual(missing_csrf.status_code, 403)
        self.assertIn('error', missing_csrf.json())
        client.get(self.question.get_absolute_url())
        headers = {'X-CSRFToken': client.cookies['csrftoken'].value}
        self.assertEqual(client.post(url, {'value': 1}, headers=headers).json()['rating'], 1)
        missing = reverse('questions:question_vote', args=[999999])
        self.assertEqual(client.post(missing, {'value': 1}, headers=headers).status_code, 404)

    def test_only_question_author_can_select_one_answer_from_that_question(self):
        url = reverse('questions:accept_answer', args=[self.question.pk])
        other = Question.objects.create(author=self.author, title='Другой', text='Текст')
        foreign_answer = Answer.objects.create(question=other, author=self.reader, text='Чужой ответ')
        second = Answer.objects.create(question=self.question, author=self.author, text='Второй ответ')

        self.assertEqual(self.client.post(url, {'answer_id': self.answer.pk}).status_code, 401)
        self.client.force_login(self.reader)
        self.assertNotContains(self.client.get(self.question.get_absolute_url()), 'data-accept-answer')
        self.assertEqual(self.client.post(url, {'answer_id': self.answer.pk}).status_code, 403)

        self.client.force_login(self.author)
        self.assertContains(self.client.get(self.question.get_absolute_url()), 'data-accept-answer')
        self.assertEqual(self.client.post(url, {'answer_id': foreign_answer.pk}).status_code, 400)
        for accepted in (self.answer, second, second):
            response = self.client.post(url, {'answer_id': accepted.pk})
            self.assertEqual(response.json(), {'answer_id': accepted.pk, 'is_correct': True})
            self.assertEqual(list(self.question.answers.filter(is_correct=True)), [accepted])

        with self.assertRaises(IntegrityError), transaction.atomic():
            self.question.answers.filter(pk=self.answer.pk).update(is_correct=True)

    def test_rendering_current_votes_does_not_add_queries_per_card(self):
        self.client.force_login(self.reader)
        QuestionLike.objects.create(question=self.question, user=self.reader)
        with CaptureQueriesContext(connection) as first:
            self.assertEqual(self.client.get('/').status_code, 200)
        Question.objects.bulk_create([
            Question(author=self.author, title=f'Вопрос {index}', text='Текст') for index in range(9)
        ])
        with CaptureQueriesContext(connection) as full:
            self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(len(first), len(full))
