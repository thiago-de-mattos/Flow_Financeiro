from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from .models import User


# ─── Cadastro ────────────────────────────────────────────────────────────────

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
        validators=[validate_password],
    )
    password_confirm = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm your password"}),
    )

    class Meta:
        model = User
        fields = ["name", "age", "email"]
        widgets = {
            "name":  forms.TextInput(attrs={"placeholder": "Enter your name"}),
            "age":   forms.NumberInput(attrs={"placeholder": "Enter your age", "min": 1, "max": 120}),
            "email": forms.EmailInput(attrs={"placeholder": "Enter your email"}),
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
        password = cleaned.get("password")
        confirm  = cleaned.get("password_confirm")
        if password and confirm and password != confirm:
            self.add_error("password_confirm", "As senhas não coincidem.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# ─── Login ───────────────────────────────────────────────────────────────────

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email"}),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
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