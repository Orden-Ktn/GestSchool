from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    ),
    
class ChangeUserForm(forms.Form):
    new_username = forms.CharField(label='New Username', max_length=150)
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    


class Meta(UserCreationForm.Meta):
    fields = UserCreationForm.Meta.fields + ("nom", "password1", "password2")