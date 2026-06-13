from django import forms
from django.contrib.auth import authenticate

from .models import User

# ─── Cadastro ────────────────────────────────────────────────────────────────

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
        fields = ["name", "age", "email"]
        widgets = {
            "name":  forms.TextInput(attrs={"placeholder": "Digite seu nome"}),
            "age":   forms.NumberInput(attrs={"placeholder": "Digite sua idade", "min": 1, "max": 120}),
            "email": forms.EmailInput(attrs={"placeholder": "Digite seu e-mail"}),
        }
        labels = {
            "name":  "Nome",
            "age":   "Idade",
            "email": "E-mail",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_age(self):
        age = self.cleaned_data["age"]
        if age < 1 or age > 120:
            raise forms.ValidationError("Informe uma idade válida.")
        return age

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


# ─── Login ───────────────────────────────────────────────────────────────────

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