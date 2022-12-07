import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_create_post_authorized_client(self):
        """Валидная форма создает запись в Post, пользоварель авторизован."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст в форме',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username':
                                             f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1,
                         'Пост не добавлен')
        self.assertTrue(
            Post.objects.filter(
                text='Текст в форме',
                group=self.group.id,
                author=self.user,
                image='posts/small.gif',
            ).exists(), 'Данные не совпали'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_authorized_client(self):
        """Проверка редактирования формы Post, пользователь авторизован."""
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id':
                                             f'{self.post.id}'}))
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст в форме',
                group=self.group_2.id,
                author=self.user,
            ).exists(), 'Данные не совпали'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post_guest_client(self):
        """Запрет создания записи в Post: пользователь не авторизован."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст в форме',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('users:login') + "?next="
                             + reverse('posts:post_create'))
        self.assertNotEqual(Post.objects.count(), posts_count + 1,
                            'Пост ошибочно добавлен')
        self.assertFalse(
            Post.objects.filter(
                text='Текст в форме',
                group=self.group.id,
                author=self.user,
            ).exists(), 'Данные ошибочно совпали'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_guest_client(self):
        """Запрет редактирования формы Post: пользователь не авторизован."""
        form_data = {
            'text': 'Новый текст в форме',
            'group': self.group_2.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('users:login') + "?next="
                             + reverse('posts:post_edit', args=[self.post.id]))
        self.assertFalse(
            Post.objects.filter(
                text='Новый текст в форме',
                group=self.group_2.id,
                author=self.user,
            ).exists(), 'Данные ошибочно совпали'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)


class CommentFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized_client(self):
        """Запрет комментировать неавторизованным пользователям."""
        form_data = {
            'text': 'Комментарий тест',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('users:login') + "?next="
                             + reverse('posts:add_comment',
                                       args=[self.post.id]))
        self.assertFalse(
            Comment.objects.filter(
                text='Комментарий тест',
                author=self.user,
                post=self.post
            ), 'Данные ошибочно совпали'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
