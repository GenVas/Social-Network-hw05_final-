from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    slug = models.SlugField(unique=True, verbose_name=_("Строка-ключ"),
                            max_length=10)
    description = models.TextField(max_length=200, verbose_name=_("Описание"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Группа")
        verbose_name_plural = _("Группы")


class Post(models.Model):

    text = models.TextField(
        verbose_name=_("Текст"),
        help_text=_("Придумайте текст для поста")
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата публикации")
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Автор")
    )
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name=_("Группа"),
        help_text=_("Выберите название группы")
    )
    # Аргумент upload_to указывает куда загружаться пользовательским файлам
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return (f"автор: {self.author.username}, группа: {self.group}, "
                f"дата: {self.pub_date}, текст:{self.text[:15]}.")

    class Meta:
        verbose_name = _("Пост")
        verbose_name_plural = _("Посты")
        ordering = ("-pub_date",)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, blank=False, null=False,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text=_("Напишите комментарий")
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(
        blank=False, null=False,
        verbose_name=_("Текст"),
        help_text=_("Придумайте текст для поста")
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата комментария")
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name="follower",
    )
    author = models.ForeignKey(
        User, on_delete=models.DO_NOTHING,
        related_name="following",
    )
