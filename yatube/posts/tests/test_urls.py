from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Smoke test."""

        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_eng_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон для авторизованных и
        неавторизованных пользователей.
        """

        templates_url_guest = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', args=[self.group.slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[self.user.username]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[self.post.id]):
                'posts/post_detail.html',
        }
        templates_url_auth = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', args=[self.group.slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[self.user.username]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[self.post.id]):
                'posts/post_detail.html',
            reverse('posts:post_edit', args=[self.post.id]):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        users = {self.guest_client: templates_url_guest,
                 self.authorized_client: templates_url_auth}
        for client, urls in users.items():
            for address, template in urls.items():
                with self.subTest(address=address):
                    cache.clear()
                    response = client.get(address)
                    self.assertTemplateUsed(response, template)

    def test_posts_url_exists_at_desired_location(self):
        """Проверка доступности адресов для приложения posts
        для авторизованных и неавторизованных пользователей.
        """

        urls_auth = (reverse('posts:index'),
                     reverse('posts:group_posts', args=[self.group.slug]),
                     reverse('posts:profile', args=[self.user.username]),
                     reverse('posts:post_detail', args=[self.post.id]),
                     reverse('posts:post_edit', args=[self.post.id]),
                     reverse('posts:post_create'),
                     )
        urls_guest = (reverse('posts:index'),
                      reverse('posts:group_posts', args=[self.group.slug]),
                      reverse('posts:profile', args=[self.user.username]),
                      reverse('posts:post_detail', args=[self.post.id]),
                      )
        users = {self.guest_client: urls_guest,
                 self.authorized_client: urls_auth}
        for client, urls in users.items():
            for url in urls:
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(
                        response.status_code, HTTPStatus.OK
                    )

    def test_unexisting_page(self):
        """Тест доступа к несуществующей странице."""

        unexisting_url = {
            self.guest_client: '/unexisting_page/',
            self.authorized_client: '/unexisting_page/',
        }
        for client, url in unexisting_url.items():
            with self.subTest(client=client):
                response = client.get(url)
                self.assertEqual(
                    response.status_code, HTTPStatus.NOT_FOUND
                )

    def test_posts_url_redirect_anonymous_on_admin_login(self):
        """Страницы, которые доступны только авторизованным пользователям
        перенаправят анонимного пользователя на страницу логина.
        """

        url_redirect = {reverse('posts:post_edit', args=[self.post.id]):
                        reverse('users:login') + "?next="
                        + reverse('posts:post_edit', args=[self.post.id]),
                        reverse('posts:post_create'):
                        reverse('users:login') + "?next="
                        + reverse('posts:post_create'),
                        }
        for url, redirected in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, redirected
                )
