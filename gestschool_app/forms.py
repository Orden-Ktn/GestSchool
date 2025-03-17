# forms.py (dans votre application)
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username',)
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Entrez votre nom et prénom. Ex: Jean_Dupont'}),
        }  

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
