from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from core.models import Profile

from .models import Answer, AnswerLike, Question, QuestionLike, Tag, VoteValue

User = get_user_model()


class QuestionPagesTests(TestCase):
    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'
        self.author = User.objects.create_user(username='author')
        self.tag = Tag.objects.create(name='Python', slug='python')

    def add_question(self, title):
        question = Question.objects.create(author=self.author, title=title, text='Текст вопроса')
        question.tags.add(self.tag)
        return question

    def test_empty_lists_and_missing_objects(self):
        for url in ('/', '/hot/', self.tag.get_absolute_url()):
            self.assertContains(self.client.get(url), 'Пока нет ни одного вопроса')
        for url in ('/tag/missing/', '/question/42/', '/question/abc/'):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_lists_use_the_requested_order_tag_and_page(self):
        older = self.add_question('Старый вопрос')
        QuestionLike.objects.create(user=self.author, question=older, value=VoteValue.LIKE)
        fresh = [self.add_question(f'Новый вопрос {index}') for index in range(10)]
        unrelated_tag = Tag.objects.create(name='Django', slug='django')
        older.tags.add(unrelated_tag)

        page = self.client.get('/').context['page']
        self.assertEqual(page[0], fresh[-1])
        self.assertEqual(list(self.client.get('/?page=2').context['page']), [older])
        self.assertEqual(self.client.get('/?page=bad').context['page'].number, 1)
        self.assertEqual(self.client.get('/hot/').context['page'][0], older)
        self.assertEqual(list(self.client.get(unrelated_tag.get_absolute_url()).context['page']), [older])

    def test_question_pagination_limits_links_and_preserves_query_parameters(self):
        Question.objects.bulk_create([
            Question(author=self.author, title=f'Вопрос {index}', text='Текст')
            for index in range(1_000)
        ])
        for path, page in (('/', 1), ('/hot/', 50)):
            with self.subTest(path=path, page=page):
                response = self.client.get(path, {'page': page, 'source': 'review'})
                self.assertEqual(response.context['page'].number, page)
                self.assertEqual(response.context['page'].paginator.num_pages, 100)
                self.assertLessEqual(response.content.count(b'class="page-link"'), 11)
                self.assertContains(response, '…')
                self.assertContains(response, 'page=100&amp;source=review')
                self.assertContains(response, 'aria-current="page"')

    def test_detail_only_shows_answers_for_that_question(self):
        question = self.add_question('Первый вопрос')
        other = self.add_question('Второй вопрос')
        Answer.objects.create(question=other, author=self.author, text='Ответ на второй вопрос')
        self.assertContains(self.client.get(question.get_absolute_url()), 'Пока нет ни одного ответа')

        Answer.objects.bulk_create([
            Answer(question=question, author=self.author, text=f'Ответ {index}')
            for index in range(11)
        ])
        first = self.client.get(question.get_absolute_url())
        self.assertNotContains(first, 'Ответ на второй вопрос')
        self.assertEqual(len(first.context['page']), 10)
        self.assertContains(first, 'href="?page=2#answers"')
        self.assertEqual(len(self.client.get(question.get_absolute_url() + '?page=2').context['page']), 1)

    def test_query_count_does_not_grow_with_more_cards(self):
        self.add_question('Один вопрос')
        with CaptureQueriesContext(connection) as single:
            self.assertEqual(self.client.get('/').status_code, 200)
        for index in range(9):
            self.add_question(f'Вопрос {index}')
        with CaptureQueriesContext(connection) as full:
            self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(len(single), len(full))

    def test_database_rejects_duplicate_votes(self):
        question = self.add_question('Вопрос')
        answer = Answer.objects.create(question=question, author=self.author, text='Ответ')
        for model, target in ((QuestionLike, {'question': question}), (AnswerLike, {'answer': answer})):
            model.objects.create(user=self.author, **target)
            with self.assertRaises(IntegrityError), transaction.atomic():
                model.objects.create(user=self.author, value=VoteValue.DISLIKE, **target)


class FillDatabaseTests(TestCase):
    def test_small_ratio_creates_exact_counts(self):
        call_command('fill_db', 2, verbosity=0)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(Tag.objects.count(), 2)
        self.assertEqual(Question.objects.count(), 20)
        self.assertEqual(Answer.objects.count(), 200)
        self.assertEqual(QuestionLike.objects.count() + AnswerLike.objects.count(), 400)
        self.assertTrue(Question.objects.filter(answers__isnull=True).exists())
        self.assertTrue(Question.objects.with_cards().filter(answer_count__gt=10).exists())
