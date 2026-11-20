from datetime import timedelta

from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class CorrectAnswerMigrationTests(TransactionTestCase):
    def test_upgrade_preserves_answers_and_keeps_earliest_mark(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        self.addCleanup(lambda: MigrationExecutor(connection).migrate(latest))
        previous = [
            ('questions', '0001_initial') if app == 'questions' else (app, name)
            for app, name in latest
        ]
        old_apps = executor.migrate(previous).apps
        user = old_apps.get_model('auth', 'User').objects.create(username='migration-author')
        Question = old_apps.get_model('questions', 'Question')
        Answer = old_apps.get_model('questions', 'Answer')
        q = Question.objects.create(author=user, title='Duplicates', text='Question')
        other = Question.objects.create(author=user, title='Single mark', text='Question')
        unmarked = Answer.objects.create(question=q, author=user, text='Unmarked')
        later = Answer.objects.create(question=q, author=user, text='Later', is_correct=True)
        first = Answer.objects.create(question=q, author=user, text='First', is_correct=True)
        tie = Answer.objects.create(question=q, author=user, text='Tie', is_correct=True)
        single = Answer.objects.create(question=other, author=user, text='Single', is_correct=True)
        Answer.objects.filter(pk__in=(first.pk, tie.pk)).update(
            created_at=later.created_at - timedelta(seconds=1),
        )

        updated_apps = MigrationExecutor(connection).migrate(latest).apps
        Answer = updated_apps.get_model('questions', 'Answer')
        self.assertEqual(
            dict(Answer.objects.values_list('pk', 'is_correct')),
            {unmarked.pk: False, later.pk: False, first.pk: True, tie.pk: False, single.pk: True},
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Answer.objects.filter(pk=later.pk).update(is_correct=True)
