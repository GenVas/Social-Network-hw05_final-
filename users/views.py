#  функция reverse_lazy позволяет получить URL по параметру "name"
#  функции path() берём, тоже пригодится
from django.shortcuts import render  # redirect
from django.urls import reverse_lazy
#  импортируем CreateView, чтобы создать ему наследника
#  CreateView - это из GenericViews
from django.views.generic import CreateView

from .forms import ContactForm, CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("signup")
    template_name = "signup.html"


def user_contact(request):
    form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# Шаблон для авторизационного декоратора

# def authorized_only(func):
#     def check_user(request, *args, **kwargs):
#         # Во view-функции первым аргументом передаётся объект request,
#         # в котором хранится булева переменная,
#         # определяющая, авторизован ли пользователь.
#         if request.user.is_authenticated:
#             # Возвращает вью-функцию, если пользователь авторизован.
#             return func(request, *args, **kwargs)
#         # Если пользователь не авторизован — его редиректит
#           на страницу логина.
#         return redirect('/auth/login/')
#     return check_user
