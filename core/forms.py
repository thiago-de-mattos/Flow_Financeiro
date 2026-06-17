from django import forms
from django.contrib.auth import authenticate
from datetime import date

from .models import User


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Crie uma senha"}),
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Repita a senha"}),
    )

    class Meta:
        model = User
        fields = ["name", "birth_date", "email"]
        widgets = {
            "name":       forms.TextInput(attrs={"placeholder": "Digite seu nome"}),
            "birth_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "email":      forms.EmailInput(attrs={"placeholder": "Digite seu e-mail"}),
        }
        labels = {
            "name":       "Nome",
            "birth_date": "Data de Nascimento",
            "email":      "E-mail",
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]
        today = date.today()

        # Calcula idade
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

        if birth_date > today:
            raise forms.ValidationError("Data de nascimento não pode ser no futuro.")
        if age < 5:
            raise forms.ValidationError("Você precisa ter pelo menos 5 anos.")
        if age > 120:
            raise forms.ValidationError("Informe uma data de nascimento válida.")
        return birth_date

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")

        if password1:
            import re
            if len(password1) < 8:
                self.add_error("password1", "Mínimo 8 caracteres.")
            if not re.search(r'\d', password1):
                self.add_error("password1", "Inclua pelo menos um número.")
            if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password1):
                self.add_error("password1", "Inclua pelo menos um símbolo (!@#$%...).")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas não coincidem.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"placeholder": "Digite seu e-mail"}),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Digite sua senha"}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email    = cleaned.get("email", "").lower()
        password = cleaned.get("password")

        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError("E-mail ou senha inválidos.")
            if not self.user.is_active:
                raise forms.ValidationError("Esta conta está desativada.")
        return cleaned

    def get_user(self):
        return getattr(self, "user", None)