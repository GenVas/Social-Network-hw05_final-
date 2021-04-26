import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post, User

HOME_PAGE, NEW_POST = reverse('index'), reverse('new_post')
LABELS = {'group': _('Вы можете выбрать группу'),
          'text': _('Напишите сообщение')}
HELP_TEXTS = {'group': 'Поле не является обязательным',
              'text': _('Придумайте текст для поста. '
                        'Поле обязательно для заполнения'), }
POST_TEST_TEXT = 'Ж' * 50
COMMENT_TEXT = 'Тестовый комментарий'
FOLLOW_INDEX_PAGE = reverse("follow_index")


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title="Тест-название",
                                         slug='test_slug',
                                         description="Тест-описание")
        cls.form = PostForm()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()
        cache.clear()

    def setUp(self):
        # первый клиент автор поста
        self.guest_client = Client()
        self.user = User.objects.create_user(username='IvanovI')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.username = self.user.username
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        # второй клиент не автор поста
        self.authorized_client_2 = Client()
        self.user_2 = User.objects.create_user(username='PetrovP')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.username_2 = self.user_2.username

        self.post = Post.objects.create(text=POST_TEST_TEXT,
                                        group=self.group,
                                        author=self.user)
        self.edit_page = reverse('post_edit', args=[self.username,
                                                    self.post.id, ])
        self.COMMENT_PAGE = reverse('add_comment', args=[self.username,
                                                         self.post.id, ])

# Тест для проверки формы создания нового поста (страница /new/)
    def test_post_created_through_valid_form(self):
        """Валидная форма создает запись в Post"""
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
            'group': self.group.pk,
            'text': 'тестовая публикация',
            'image': uploaded,
        }
        form = PostForm(form_data)
        self.assertTrue(form.is_valid())

        posts_count = Post.objects.count()
        self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        post_object = Post.objects.filter(text=form_data['text'],
                                          group=form_data['group'],
                                          author=self.user.id,
                                          image='posts/small.gif')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(post_object.exists())

# Тест для проверки формы создания нового комментария
    def test_comment_created_by_auth_and_unauth_users(self):
        '''Комментировать могут только зарегистрированные пользователи'''
        comment_text_2 = 'Текст коммента авторизированного пользователя'
        comment_text_unauth = 'Текст коммента НЕавторизированного пользователя'
        post2 = Post.objects.create(text=comment_text_unauth,
                                    group=self.group,
                                    author=self.user_2)
        comments_count = Comment.objects.count()
        form_data = {'text': COMMENT_TEXT, }
        self.authorized_client.post(
            self.COMMENT_PAGE, data=form_data, follow=True)
        self.guest_client.post(
            self.COMMENT_PAGE, data=form_data, follow=True)
        comment_object = Comment.objects.filter(
            text=form_data['text'], author=self.user, post=self.post.id,)
        comment_object2 = Comment.objects.filter(
            text=comment_text_2, author=self.user, post=post2.id,)
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(comment_object.exists())
        self.assertFalse(comment_object2.exists())

    def test_post_not_created_for_invalid_fields(self):
        """Невалидная форма не создает запись в Post"""
        invalid_text = {
            'group': self.group.pk,
            'text': '',
        }
        invalid_group = {
            'group': 'group',
            'text': 'тестовая публикация',
        }
        invalid_data = [invalid_text, invalid_group]
        for invalid in invalid_data:
            form = PostForm(invalid)
            self.assertFalse(form.is_valid())
            posts_count = Post.objects.count()
            self.authorized_client.post(
                reverse('new_post'),
                data=invalid_text,
                follow=True
            )
            try:
                post_object = Post.objects.filter(
                    text=invalid['text'],
                    group=invalid['group'],
                    author=self.user.id
                ).count()
            except ValueError:
                continue
            self.assertEqual(post_object, 0)
            self.assertEqual(Post.objects.count(), posts_count)

# Тест для проверки меток полей Post
    def test_label(self):
        for title, label in LABELS.items():
            with self.subTest(title=title):
                title_label = self.form.fields[title].label
                self.assertEqual(title_label, label)

    def test_help_text(self):
        for title, label in HELP_TEXTS.items():
            with self.subTest(title=title):
                title_help_text = self.form.fields[title].help_text
                self.assertEqual(title_help_text, label)

    def test_new_and_edit_post_page_shows_correct_context(self):
        """Страница new post и edit_page сформирована правильно через форму"""
        temp_list = [NEW_POST, self.edit_page]
        for url in temp_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                    'image': forms.fields.ImageField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_post_edit_by_author(self):
        '''Редактировании поста автором поста
        осуществляется'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'text': 'ну, давай же, редактируйся! Ревьюер требует!',
            'group': new_group.pk,
        }

        self.authorized_client.post(self.edit_page,
                                    data=form_data,
                                    follow=False)

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=self.post.id)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.pk, form_data['group'])
        self.assertEqual(new_post.author.username, self.username)

    def test_post_edit_by_non_author(self):
        '''При редактировании поста не автором поста
        редактирование не осуществляется'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'text': 'это сообщение не должно переписаться в пост',
            'group': new_group.pk,
        }
        self.authorized_client_2.post(self.edit_page,
                                      data=form_data,
                                      follow=False)

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=pk_list_after[-0])
        self.assertEqual(new_post.text, self.post.text)
        self.assertEqual(new_post.group.pk, self.post.group.pk)
        self.assertEqual(new_post.author.username, self.username)

    def test_post_edit_by_guest(self):
        '''Гость не может редактировать пост'''
        pk_list_before = Post.objects.filter().values_list('pk', flat=True)
        new_group = Group.objects.create(title="новая группа",
                                         slug='test_slug2',
                                         description="Тест-описание2")
        form_data = {
            'text': 'это сообщение не должно переписаться в пост',
            'group': new_group.pk,
        }
        self.guest_client.post(self.edit_page,
                               data=form_data,
                               follow=False)

        pk_list_after = Post.objects.filter().values_list('pk', flat=True)
        self.assertEqual(set(pk_list_before), set(pk_list_after))
        new_post = Post.objects.get(pk=pk_list_after[-0])
        self.assertEqual(new_post.text, self.post.text)
        self.assertEqual(new_post.group.pk, self.post.group.pk)
        self.assertEqual(new_post.author.username, self.username)

    def test_auth_user_can_follow_other_users(self):
        """Авторизированный пользователь может
        подписаться на другого пользователя"""
        follows_before = Follow.objects.count()
        follow_page = reverse("profile_follow", args=[self.username])
        form_data = {'user': self.username_2,
                     'author': self.username}
        self.authorized_client_2.post(
            follow_page, data=form_data, follow=True)
        followed = Follow.objects.filter(user=self.user_2,
                                         author=self.user)
        self.assertEqual(Follow.objects.count(), follows_before + 1)
        self.assertTrue(followed.exists())
        response = self.authorized_client_2.get(FOLLOW_INDEX_PAGE)
        self.assertEqual(len(response.context['page']), follows_before + 1)
        response = self.authorized_client.get(FOLLOW_INDEX_PAGE)
        self.assertEqual(len(response.context['page']), follows_before)

    def test_auth_user_can_unfollow_other_users(self):
        """Авторизированный пользователь может
        отписаться другого пользователя"""
        follow_page = reverse("profile_follow", args=[self.username])
        unfollow_page = reverse("profile_unfollow", args=[self.username])
        form_data = {'user': self.username_2,
                     'author': self.username}
        self.authorized_client_2.post(
            follow_page, data=form_data, follow=True)
        following_done = Follow.objects.count()
        self.authorized_client_2.post(
            unfollow_page, data=form_data, follow=True)
        unfollowed = Follow.objects.filter(user=self.user_2,
                                           author=self.user)
        self.assertEqual(Follow.objects.count(), following_done - 1)
        self.assertFalse(unfollowed.exists())

# Тестирование кэша
    def test_сache_for_main_page(self):
        '''Создается кэш главной страницы'''
        response = self.guest_client.get(HOME_PAGE)
        Post.objects.create(
            text='заметка для кэша',
            author=self.user,
            group=self.group
        )
        response2 = self.guest_client.get(HOME_PAGE)
        self.assertEqual(response.content, response2.content)
        cache.clear()
        response3 = self.guest_client.get(HOME_PAGE)
        self.assertNotEqual(response.content, response3.content)
