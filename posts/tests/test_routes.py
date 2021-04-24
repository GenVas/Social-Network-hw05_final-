from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class RoutesTest(TestCase):
    def test_routes(self):
        user = User.objects.create_user(username='test_user')
        group = Group.objects.create(title='группа',
                                     description='описание',
                                     slug='group')
        post = Post.objects.create(text='тестовая публикация',
                                   group=group,
                                   author=user)

        test_urls = {
            reverse('index'): '/',
            reverse('new_post'): '/new/',
            reverse('group_posts', args=[group.slug]): f'/group/{group.slug}/',
            reverse('profile', args=[user.username]): f'/{user.username}/',
            reverse('post', args=[post.author.username,
                                  post.id]): f'/{user.username}/{post.id}/',
            reverse('post_edit', args=[post.author.username,
                                       post.id]): f'/{user.username}/'
                                                  f'{post.id}/edit/',
        }
        for page, url in test_urls.items():
            self.assertEqual(page, url)
