from django import forms

from .models import Comment


class CommentForm(forms.Form):
    models = Comment
    fields = ('text',)