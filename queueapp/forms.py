from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Prénom", required=True)
    last_name = forms.CharField(max_length=150, label="Nom", required=True)
    email = forms.EmailField(label="Adresse e-mail", required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        labels = {"username": "Nom d'utilisateur", "password1": "Mot de passe", "password2": "Confirmer le mot de passe"}
