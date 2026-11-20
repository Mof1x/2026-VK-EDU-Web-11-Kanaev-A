from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Profile

User = get_user_model()
PASSWORD = 'A strong sample password 741$'


def png_file(name='avatar.png'):
    image = BytesIO()
    Image.new('RGB', (8, 8), 'blue').save(image, 'PNG')
    return SimpleUploadedFile(name, image.getvalue(), content_type='image/png')


class AccountTests(TestCase):
    def setUp(self):
        self.client.defaults['HTTP_HOST'] = 'localhost'
        self.user = User.objects.create_user(
            username='andrei', email='before@example.com', first_name='Андрей', password=PASSWORD,
        )

    def test_login_preserves_input_and_checks_redirect(self):
        response = self.client.post('/login/', {
            'username': 'andrei', 'password': 'wrong-password', 'next': '/hot/?page=2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())
        self.assertContains(response, 'value="andrei"')
        self.assertContains(response, 'value="/hot/?page=2"')
        self.assertNotContains(response, 'wrong-password')

        for target, result in (('/hot/?page=2', '/hot/?page=2'), ('https://example.com/', '/')):
            with self.subTest(target=target):
                response = self.client.post('/login/', {
                    'username': 'andrei', 'password': PASSWORD, 'next': target,
                })
                self.assertRedirects(response, result, fetch_redirect_response=False)

    def test_logout_requires_csrf_and_stays_on_public_page(self):
        client = Client(enforce_csrf_checks=True, HTTP_HOST='localhost')
        client.force_login(self.user)
        self.assertEqual(client.get('/logout/').status_code, 405)
        self.assertEqual(client.post('/logout/').status_code, 403)
        client.get('/')
        response = client.post('/logout/', {'next': '/hot/?page=2'}, headers={
            'X-CSRFToken': client.cookies['csrftoken'].value,
        })
        self.assertRedirects(response, '/hot/?page=2', fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', client.session)

    def test_registration_validates_password_and_creates_profile(self):
        fields = {'username': 'newuser', 'email': 'new@example.com', 'first_name': 'Новый'}
        response = self.client.post('/signup/', {**fields, 'password1': '123', 'password2': '123'})
        self.assertIn('password2', response.context['form'].errors)
        self.assertContains(response, 'value="new@example.com"')
        self.assertFalse(User.objects.filter(username='newuser').exists())

        response = self.client.post('/signup/', {**fields, 'password1': PASSWORD, 'password2': PASSWORD})
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_profile_requires_login_and_updates_only_current_user(self):
        other = User.objects.create_user(username='other', email='other@example.com')
        self.assertRedirects(self.client.get('/profile/'), '/login/?next=/profile/')
        self.client.force_login(self.user)
        response = self.client.get('/profile/')
        self.assertContains(response, 'value="before@example.com"')
        self.assertNotContains(response, 'Настройки профиля сохранены.')
        self.assertContains(response, '/static/core/img/default-avatar.svg')

        response = self.client.post('/profile/', {'email': 'bad', 'first_name': 'Мой ник'})
        self.assertIn('email', response.context['form'].errors)
        self.assertContains(response, 'value="Мой ник"')

        response = self.client.post('/profile/', {
            'email': 'after@example.com', 'first_name': 'Мой ник', 'user': other.pk,
        })
        self.assertRedirects(response, '/profile/')
        self.user.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(self.user.email, 'after@example.com')
        self.assertEqual(self.user.first_name, 'Мой ник')
        self.assertEqual(other.email, 'other@example.com')
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_avatar_checks_content_extension_and_size_and_uses_media_storage(self):
        self.client.force_login(self.user)
        fields = {'email': self.user.email, 'first_name': self.user.first_name}
        with TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            image = png_file()
            oversized = SimpleUploadedFile(
                'large.png', image.read() + b'0' * (2 * 1024 * 1024), content_type='image/png',
            )
            for invalid in (
                SimpleUploadedFile('fake.png', b'not an image'),
                png_file('avatar.gif'),
                oversized,
            ):
                response = self.client.post('/profile/', {**fields, 'avatar': invalid})
                self.assertIn('avatar', response.context['form'].errors)
                self.assertFalse(Profile.objects.filter(user=self.user).exists())

            response = self.client.post('/profile/', {**fields, 'avatar': png_file('my-avatar.png')})
            self.assertRedirects(response, '/profile/')
            avatar = Profile.objects.get(user=self.user).avatar
            self.assertRegex(avatar.name, r'^avatars/[a-f0-9]{32}\.png$')
            self.assertTrue(Path(avatar.path).is_relative_to(Path(media)))
            self.assertTrue(Path(avatar.path).is_file())
            self.assertContains(self.client.get(reverse('core:profile')), avatar.url)
            self.assertContains(self.client.get('/'), f'src="{avatar.url}"')
