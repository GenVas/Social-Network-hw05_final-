from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'group': _('Вы можете выбрать группу'),
            'text': _('Напишите сообщение')
        }
        help_texts = {
            'group': 'Поле не является обязательным',
            'text': 'Придумайте текст для поста. '
                    'Поле обязательно для заполнения',
        }


class GroupForm(forms.ModelForm):
    '''Форма создания группы'''
    class Meta:
        model = Group
        fields = '__all__'

    def clean_group(self):
        cleaned_data = super().clean()
        title = cleaned_data['title']
        if Group.Objects.filter(title=title).exists():
            raise ValidationError(f'{title} уже существует')
        return title


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Напишите комментарий')
        }
        help_texts = {
            'text': 'Придумайте комментарий для поста. '
                    'Поле обязательно для заполнения',
        }
