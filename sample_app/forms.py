from django import forms
from .models import Post

class SimpleForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            'Q1': forms.RadioSelect()
        }