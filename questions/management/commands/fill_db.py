from random import Random
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag, VoteValue

BATCH_SIZE = 2_000
QUESTIONS_PER_USER = 10
ANSWER_COUNTS = (0, 10, 20, 10, 10, 10, 10, 10, 10, 10)
ANSWERS_PER_USER = sum(ANSWER_COUNTS)
VOTES_PER_USER = 200
QUESTIONS_PER_BATCH = 300
DEFAULT_RATIO = 10_001


def vote_value(random):
    return VoteValue.DISLIKE if random.randrange(5) == 0 else VoteValue.LIKE


def create_posts(users, tags, content, random):
    question_titles, question_texts, answer_texts = content
    questions_total = len(users) * QUESTIONS_PER_USER
    # At small ratios there may be fewer than ten distinct voters per question.
    votes_per_question = min(len(users), 10)
    # Fill the remaining quota with one or two votes per answer.
    extra_votes_per_user = VOTES_PER_USER - QUESTIONS_PER_USER * votes_per_question - ANSWERS_PER_USER
    tag_link = Question.tags.through

    for start in range(0, questions_total, QUESTIONS_PER_BATCH):
        count = min(QUESTIONS_PER_BATCH, questions_total - start)
        questions = Question.objects.bulk_create([
            Question(
                author_id=users[index % len(users)],
                title=random.choice(question_titles),
                text=random.choice(question_texts),
            )
            for index in range(start, start + count)
        ], batch_size=BATCH_SIZE)

        tag_link.objects.bulk_create([
            tag_link(question_id=question.pk, tag_id=tag)
            for question in questions
            for tag in random.sample(tags, min(len(tags), 3))
        ], batch_size=BATCH_SIZE)
        question_votes = []
        answers = []
        for index, question in enumerate(questions, start=start):
            first_voter = random.randrange(len(users))
            question_votes.extend(
                QuestionLike(
                    question_id=question.pk,
                    user_id=users[(first_voter + offset) % len(users)],
                    value=vote_value(random),
                )
                for offset in range(votes_per_question)
            )
            answer_count = ANSWER_COUNTS[index % QUESTIONS_PER_USER]
            accepted_index = random.randrange(answer_count + 1)
            answers.extend(
                Answer(
                    question_id=question.pk,
                    author_id=random.choice(users),
                    text=random.choice(answer_texts),
                    is_correct=index == accepted_index,
                )
                for index in range(answer_count)
            )
        QuestionLike.objects.bulk_create(question_votes, batch_size=BATCH_SIZE)
        Answer.objects.bulk_create(answers, batch_size=BATCH_SIZE)

        answer_votes = []
        for index, answer in enumerate(answers, start=start // QUESTIONS_PER_USER * ANSWERS_PER_USER):
            first_voter = random.randrange(len(users))
            voter_count = 1 + (index % ANSWERS_PER_USER < extra_votes_per_user)
            answer_votes.extend(
                AnswerLike(
                    answer_id=answer.pk,
                    user_id=users[(first_voter + offset) % len(users)],
                    value=vote_value(random),
                )
                for offset in range(voter_count)
            )
        AnswerLike.objects.bulk_create(answer_votes, batch_size=BATCH_SIZE)


class Command(BaseCommand):
    help = 'Добавляет демонстрационные данные. По умолчанию создаёт полный объём ДЗ3.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, nargs='?', default=DEFAULT_RATIO)

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio < 2:
            raise CommandError('ratio должен быть ≥ 2 для нужного числа уникальных оценок.')

        fake = Faker('ru_RU')
        random = Random()
        prefix = uuid4().hex[:12]
        User = get_user_model()
        users = User.objects.bulk_create([
            User(
                username=f'demo_{prefix}_{index}',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password='!',
            )
            for index in range(ratio)
        ], batch_size=BATCH_SIZE)
        user_ids = [user.pk for user in users]
        Profile.objects.bulk_create([Profile(user_id=pk) for pk in user_ids], batch_size=BATCH_SIZE)

        tags = []
        for index in range(ratio):
            phrase = ' '.join(fake.words(nb=2))
            tags.append(Tag(
                name=f'{phrase} · {prefix}-{index}',
                slug=f'{slugify(phrase, allow_unicode=True)}-{prefix}-{index}',
            ))
        Tag.objects.bulk_create(tags, batch_size=BATCH_SIZE)

        # Reuse a varied pool instead of invoking Faker for every answer.
        pool_size = min(ratio * QUESTIONS_PER_USER, 2_000)
        content = (
            [fake.sentence(nb_words=8)[:200] for _ in range(pool_size)],
            [fake.paragraph(nb_sentences=3) for _ in range(pool_size)],
            [fake.paragraph(nb_sentences=2) for _ in range(pool_size)],
        )
        create_posts(user_ids, [tag.pk for tag in tags], content, random)

        self.stdout.write(self.style.SUCCESS(
            f'Добавлено пользователей и профилей: по {ratio}; '
            f'вопросов: {ratio * QUESTIONS_PER_USER}; '
            f'ответов: {ratio * ANSWERS_PER_USER}; '
            f'тегов: {ratio}; оценок: {ratio * VOTES_PER_USER}.'
        ))
