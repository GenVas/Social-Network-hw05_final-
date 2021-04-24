import datetime as dt

from django.test import TestCase

from posts.models import Group, Post, User

FIELD_VERBOSES = {"text": "Текст",
                  "group": "Группа", }
FIELD_HELP_TEXTS = {"text": "Придумайте текст для поста",
                    "group": "Выберите название группы", }


class PostModelTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(title="Тест-название",
                                          slug='test_slug',
                                          description="Тест-описание")
        pub_date = dt.datetime.now().date()
        author = User.objects.create_user(username='test_user')
        self.post = Post.objects.create(text="Ж" * 50,
                                        group=self.group,
                                        author=author,
                                        pub_date=pub_date)

    def test_verbose_name(self):
        """verbose_name полей text и group совпадает с ожидаемым"""

        for value, expected in FIELD_VERBOSES.items():
            with self.subTest(expected=expected):
                self.assertEqual(Post._meta.get_field(value).verbose_name,
                                 expected)

    def test_help_text_name(self):
        """help_text полей text и group совпадает с ожидаемым"""
        for value, expected in FIELD_HELP_TEXTS.items():
            with self.subTest(value=value):
                self.assertEqual(Post._meta.get_field(value).help_text,
                                 expected)

    def test_group_str_method(self):
        """__str__ метод в Group совпадает с ожидаемым"""
        str_text = self.group.title
        self.assertEqual(self.group.__str__(), str_text)

    def test_post_str_method(self):
        """__str__ метод в Post сокращает строку text до 15 символов"""
        long_text, short_text = self.post.text[:16], self.post.text[:15]
        self.assertTrue(short_text in self.post.__str__(), "менее 15 символов"
                                                           " или отсутствует")
        self.assertFalse(long_text in self.post.__str__(), "более 15 символов")
