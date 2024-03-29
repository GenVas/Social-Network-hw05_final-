from django.views.generic.base import TemplateView


class AboutAuthorStaticPage(TemplateView):
    template_name = "about_author.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['just_title'] = '«Об авторе»'
        context['just_text'] = '''Автор мучительно долго шел
        к созданию этого сайта.\n За терпение и помощь благодарен своей семье,
        кошкам и работе. Фото кружки или рабочего стола\n
        выкладывать не буду - это личное :-) \n
        Профиль на GitHub: #GenVas'''
        return context


class AboutTechStaticPage(TemplateView):
    template_name = "about_tech.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['just_title'] = '«О технологиях»'
        context['just_text'] = '''Этот сайт был создан на Django,
        соответственно, написан на Python,\n для тестирования использован
        Unittest, база данных использована встренная - SQLite.'''
        return context
