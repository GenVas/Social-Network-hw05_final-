from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.urls = {'about_author.html': reverse('author'),
                     'about_tech.html': reverse('tech')
                     }

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about, tech доступен."""
        for name in self.urls.values():
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """При запросе к staticpages:about
        применяется шаблон staticpages/about.html."""
        for template, name in self.urls.items():
            with self.subTest(tempalte=template):
                response = self.guest_client.get(name)
                self.assertTemplateUsed(response, template)
