from django.test import TestCase

from ..models import Comment, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_object_name = self.post.text
        self.assertEqual(expected_object_name, str(self.post))

    def test_verbose_name(self):
        """verbose_name модели Post в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Содержание',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_texts(self):
        """help_text модели Post в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите подходящую группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))

    def test_verbose_name(self):
        """verbose_name модели Group в полях совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Имя группы',
            'slug': 'Сокращенное название',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_texts(self):
        """help_text модели Group в полях совпадает с ожидаемым."""
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Введите сокращенное название латиницей',
            'description': 'Введите описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).help_text,
                    expected_value)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Комментарий',
            post=cls.post
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        expected_object_name = self.comment.text
        self.assertEqual(expected_object_name, str(self.comment))

    def test_verbose_name(self):
        """verbose_name модели Comment в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Комментарий',
            'created': 'Дата публикации',
            'author': 'Комментатор',
            'post': 'Комментируемый пост',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_texts(self):
        """help_text модели Comment в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст комментария',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).help_text,
                    expected_value)
