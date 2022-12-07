from django.contrib.auth import get_user_model
from django.db import models


TEXT_LIM = 15
User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Имя группы',
        help_text='Введите название группы',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Сокращенное название',
        help_text='Введите сокращенное название латиницей',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание группы',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Содержание',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите подходящую группу',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Прикрепите подходящую картинку'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:TEXT_LIM]


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментатор',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый пост',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:TEXT_LIM]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['author', 'user'],
                                    name='Follow_unique')
        ]
