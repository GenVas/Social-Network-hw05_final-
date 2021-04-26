from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="Строка-ключ",
                            max_length=10)
    description = models.TextField(max_length=200, verbose_name="Описание")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):

    text = models.TextField(
        verbose_name="Текст",
        help_text="Придумайте текст для поста"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите название группы"
    )
    # Аргумент upload_to указывает куда загружаться пользовательским файлам
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return (f"автор: {self.author.username}, группа: {self.group}, "
                f"дата: {self.pub_date}, текст:{self.text[:15]}.")

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ("-pub_date",)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, blank=False, null=False,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Напишите комментарий"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(
        blank=False, null=False,
        verbose_name="Текст",
        help_text="Придумайте текст для поста"
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата комментария"
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow'),
        ]
