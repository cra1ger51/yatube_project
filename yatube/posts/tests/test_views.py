from django import forms
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User

POST_CREATE_LIM = 13
POST_LIM_1 = 10
POST_LIM_2 = 3


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Проверка используемых шаблонов для URL-адресов."""

        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                error = f'Ошибка: {reverse_name} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error)

    def test_context(self):
        """Проверка передаваемого в шаблоны контекста."""

        urls = (reverse('posts:index'),
                reverse('posts:group_posts',
                        kwargs={'slug': f'{self.group.slug}'}),
                reverse('posts:profile',
                        kwargs={'username': self.user.username}),
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.id})
                )
        for url in urls:
            response = self.authorized_client.get(url)
            context = {response.context['post'].text: self.post.text,
                       response.context['post'].group: self.group,
                       response.context['post'].author: self.user,
                       response.context['post'].image: self.post.image}
            for value, expected in context.items():
                self.assertEqual(value, expected)

    def test_create_post_context(self):
        """Проверка передаваемого в шаблон create_post.html контекста."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_display_correct_pages(self):
        """Проверка отображения поста на нужных страницах при создании."""

        cache.clear()
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_group_2 = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': f'{self.group_2.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        group_2 = response_group_2.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(self.post, index, 'Пост не попал на главную')
        self.assertIn(self.post, group, 'Пост не попал в группу')
        self.assertIn(self.post, profile, 'Пост не попал в профиль')
        self.assertNotIn(self.post, group_2, 'Пост попал в другую группу')

    def test_view_cache_index(self):
        """Проверка работы кеша для view-функции index."""

        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='Текст поста',
            author=self.user,
        )
        response_1 = self.authorized_client.get(reverse('posts:index'))
        posts_1 = response_1.content
        self.assertEqual(posts_1, posts)
        cache.clear()
        response_2 = self.authorized_client.get(reverse('posts:index'))
        posts_2 = response_2.content
        self.assertNotEqual(posts_1, posts_2)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        posts_created = []
        for i in range(POST_CREATE_LIM):
            posts_created.append(Post(text=f'Тестовый текст {i}',
                                 group=cls.group,
                                 author=cls.user))
        Post.objects.bulk_create(posts_created)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_count_on_different_pages(self):
        """Проверка работы паджинатора на разных страницах"""

        reverse_urls = (reverse('posts:index'),
                        reverse('posts:group_posts',
                                kwargs={'slug': self.group.slug}),
                        reverse('posts:profile',
                                kwargs={'username': self.user.username}))
        users = (self.authorized_client, self.guest_client)
        for user in users:
            for reverse_url in reverse_urls:
                with self.subTest(reverse_url=reverse_url):
                    response_page_1 = user.get(reverse_url)
                    response_page_2 = user.get(
                        reverse_url + '?page=2')
                    cache.clear()
                    context_page_obj_1 = response_page_1.context['page_obj']
                    context_page_obj_2 = response_page_2.context['page_obj']
                    error_1 = (f'Ошибка: количество постов на '
                               f'странице {reverse_url} '
                               f'не равно {POST_LIM_1}, '
                               f'Пользователь авторизован: {user.login()}')
                    error_2 = (f'Ошибка: количество постов на '
                               f'странице {reverse_url} ?page=2 '
                               f'не равно {POST_LIM_2}, '
                               f'Пользователь авторизован: {user.login()}')
                    self.assertEqual(len(context_page_obj_1),
                                     POST_LIM_1, error_1)
                    self.assertEqual(len(context_page_obj_2),
                                     POST_LIM_2, error_2)


class CommentViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='auth2')
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост',
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост2',
        )
        cls.comment = Comment.objects.create(
            author=cls.user_2,
            text='комментарий',
            post=cls.post
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)

    def test_comment_display_correct_post(self):
        """Проверка отображения комментария под постом при создании."""

        response_post_detail = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        comment = response_post_detail.context['comments']
        self.assertIn(self.comment, comment, 'Пост не попал в нужный пост')


class FollowViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='auth2')
        cls.user_3 = User.objects.create_user(username='auth3')
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(self.user_3)

    def test_follow_and_unfollow_authorized(self):
        """Тест подкиски/отписки авторизованного пользователя."""

        follow_request = Follow.objects.create(author=self.user_1,
                                               user=self.user_2)
        follow_result = Follow.objects.filter(author=self.user_1,
                                              user=self.user_2)
        self.assertIn(follow_request, follow_result)
        unfollow_request = Follow.objects.filter(author=self.user_1,
                                                 user=self.user_2).delete()
        unfollow_result = Follow.objects.filter(author=self.user_1,
                                                user=self.user_2)
        self.assertNotIn(unfollow_request, unfollow_result)
        self.assertNotEqual(follow_result, unfollow_result)

    def test_new_post_at_followers_page(self):
        """Созданный пост попадает в ленту подписчику и не попадает другим."""

        Follow.objects.create(author=self.user_1,
                              user=self.user_2)
        response_post_detail_2 = self.authorized_client_2.get(
            reverse('posts:follow_index'))
        response_post_detail_3 = self.authorized_client_3.get(
            reverse('posts:follow_index'))
        context_user_2 = response_post_detail_2.context['page_obj']
        context_user_3 = response_post_detail_3.context['page_obj']
        self.assertIn(self.post, context_user_2,
                      'Пост не попал в ленту подпичкику')
        self.assertNotIn(self.post, context_user_3,
                         'Пост попал в ленту не подписанного пользователя')

    def test_follow_itself(self):
        """Пользователь не может подписаться сам на себя."""
        result_1 = Follow.objects.filter(author=1,
                                         user=1).exists()
        self.authorized_client.post(reverse('posts:profile_follow',
                                    kwargs={'username': 1}))
        Follow.objects.filter(author=1,
                              user=1)
        follow_result = Follow.objects.filter(author=1,
                                              user=1).exists()
        self.assertEqual(result_1, follow_result)
