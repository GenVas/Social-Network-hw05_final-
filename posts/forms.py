from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'group': 'Вы можете выбрать группу',
            'text': 'Напишите сообщение'
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
            'text': 'Напишите комментарий'
        }
        help_texts = {
            'text': 'Придумайте комментарий для поста. '
                    'Поле обязательно для заполнения',
        }
