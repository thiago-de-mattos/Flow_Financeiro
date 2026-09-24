from datetime import date

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, name, birth_date, password=None):
        if not email:
            raise ValueError("Email obrigatório")
        user = self.model(email=self.normalize_email(email), name=name, birth_date=birth_date)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, birth_date, password):
        user = self.create_user(email, name, birth_date, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    name       = models.CharField("Nome", max_length=150)
    birth_date = models.DateField("Data de Nascimento")
    email      = models.EmailField("E-mail", unique=True)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["name", "birth_date"]

    objects = UserManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def age(self):
        hoje = date.today()
        b = self.birth_date
        return hoje.year - b.year - ((hoje.month, hoje.day) < (b.month, b.day))


class Profile(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    level         = models.PositiveIntegerField("Nível", default=1)
    xp_total      = models.PositiveIntegerField("XP total", default=0)
    xp_next_level = models.PositiveIntegerField("XP para próximo nível", default=100)
    coins         = models.PositiveIntegerField("Moedas", default=0)
    streak_days   = models.PositiveIntegerField("Streak (dias)", default=0)
    last_activity = models.DateField("Última atividade", null=True, blank=True)
    avatar        = models.CharField("Avatar", max_length=20, default="pessoa1")

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return f"Perfil de {self.user.name} — Nível {self.level}"

    def add_xp(self, amount: int):
        self.xp_total += amount
        while self.xp_total >= self.xp_next_level:
            self.xp_total -= self.xp_next_level
            self.level += 1
            self.xp_next_level = int(self.xp_next_level * 1.5)
        self.save(update_fields=["xp_total", "level", "xp_next_level"])

    def update_streak(self):
        hoje = timezone.localdate()
        if self.last_activity is None:
            self.streak_days = 1
        elif (hoje - self.last_activity).days == 1:
            self.streak_days += 1
        elif (hoje - self.last_activity).days > 1:
            self.streak_days = 1
        self.last_activity = hoje
        self.save(update_fields=["streak_days", "last_activity"])