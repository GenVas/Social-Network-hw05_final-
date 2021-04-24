from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

HOME_PAGE, NEW_POST = reverse("index"), reverse("new_post")
URL_404 = "404/"

class StaticURLTests(TestCase):
    def setUp(self):
        self.group = Group.objects.create(title="Тест-название",
                                          slug="test_slug",
                                          description="Тест-описание")
        # первый клиент автор поста
        self.guest_client = Client()
        self.user = User.objects.create_user(username="IvanovI")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.username = self.user.username
        # второй клиент не автор поста
        self.authorized_client_2 = Client()
        self.user_2 = User.objects.create_user(username="PetrovP")
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        # создание поста
        self.post = Post.objects.create(text="Ж" * 50,
                                        group=self.group,
                                        author=self.user)
        # библиотека юрлов
        self.post_id = self.post.id
        self.post_page = reverse("post", args=[self.username,
                                               self.post_id])
        self.edit_page = reverse("post_edit",
                                 args=[self.username, self.post.id, ])

    # 1. Проверка запросов к страницам
    def test_url_exists(self):
        """Проверка доступности адресов любого клиента"""
        slug = self.group.slug
        group_page = reverse("group_posts", args=[slug])
        profile_page = reverse("profile", args=[self.username])
        url_names = [
            [HOME_PAGE, self.guest_client, 200],
            [group_page, self.guest_client, 200],
            [self.post_page, self.guest_client, 200],
            [profile_page, self.guest_client, 200],
            [NEW_POST, self.guest_client, 302],
            [NEW_POST, self.authorized_client, 200],
            [self.edit_page, self.guest_client, 302],
            [self.edit_page, self.authorized_client, 200],
        ]

        for url, client, code in url_names:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_code_404__shows_correct_context(self):
        """Проверка возвращает ли сервер код 404,
        если страница не найдена."""
        self.assertEqual(self.guest_client.get(URL_404).status_code, 404)

    # 2. Проверка шаблонов
    def test_url_uses_correct_templates(self):
        """Проверка шаблонов для адресов и разных клиентов "/" """
        slug = self.group.slug
        group_page = reverse("group_posts", args=[slug])
        profile_page = reverse("profile", args=[self.username])
        url_names = [
            ["index.html", HOME_PAGE, self.guest_client],
            ["group.html", group_page, self.guest_client],
            ["post.html", self.post_page, self.guest_client],
            ["profile.html", profile_page, self.guest_client],
            ["new.html", NEW_POST, self.authorized_client],
            ["new.html", self.edit_page, self.authorized_client],
        ]

        for template, url, client in url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)

    # Проверка редиректов
    def test_redirect(self):
        """Проверка редиректов для страниц."""

        url_names = [
            [NEW_POST, self.guest_client, (reverse("login") + "?next="
                                           + NEW_POST)],
            [self.edit_page, self.guest_client, (reverse("login")
                                                 + "?next=" + self.edit_page)],
            [self.edit_page, self.authorized_client_2, self.post_page],
        ]

        for url, client, redirected in url_names:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirected)
