from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse

User = get_user_model()


class PostQuerySet(models.QuerySet):

    def with_related_data(self):
        return self.select_related(
            'author', 'location', 'category'
        )

    def published(self):
        return self.filter(
            models.Q(pub_date__lte=timezone.now())
            & models.Q(is_published=True)
            & models.Q(category__is_published=True)
        )

    def comment_count(self):
        return self.annotate(
            comment_count=Count('comments')
        )


class PostManager(models.Manager):
    def get_queryset(self):
        return (
            PostQuerySet(self.model)
            .with_related_data()
            .published()
            .comment_count()
        )


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('-created_at', )

    def __str__(self):
        return self.title


class Category(BaseModel):
    title = models.CharField('Заголовок', max_length=settings.MAX_FIELD_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(BaseModel):
    name = models.CharField(
        'Название места',
        max_length=settings.MAX_FIELD_LENGTH
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(
        'Заголовок',
        max_length=settings.MAX_FIELD_LENGTH
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время в будущем'
                   ' — можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Фотография',
        upload_to='post_photo',
        blank=True,
    )

    objects = PostQuerySet.as_manager()
    published = PostManager()

    class Meta:
        default_related_name = 'posts'
        ordering = ('-pub_date', )
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    text = models.TextField(
        'Комментарий',
        max_length=settings.MAX_FIELD_LENGTH
    )
    publication = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Публикация'
    )
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.publication.pk})

    class Meta:
        default_related_name = 'comments'
        ordering = ('created_at',)
        verbose_name = 'коментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return f'Комментарий от {self.author} к записи "{self.publication}"'
