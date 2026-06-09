from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# ─── Autenticação customizada ────────────────────────────────────────────────

class UserManager(BaseUserManager):
    def create_user(self, email, name, age, password=None):
        if not email:
            raise ValueError("Email obrigatório")
        user = self.model(email=self.normalize_email(email), name=name, age=age)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, age, password):
        user = self.create_user(email, name, age, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuário do Flow Financeiro.
    Usa email como identificador principal (não username).
    """
    name       = models.CharField("Nome", max_length=150)
    age        = models.PositiveSmallIntegerField("Idade")
    email      = models.EmailField("E-mail", unique=True)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["name", "age"]

    objects = UserManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.name} ({self.email})"


# ─── Perfil e gamificação ────────────────────────────────────────────────────

class Profile(models.Model):
    """
    Dados de progresso e gamificação de cada usuário.
    Criado automaticamente via signal ao registrar o User.
    """
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    level         = models.PositiveIntegerField("Nível", default=1)
    xp_total      = models.PositiveIntegerField("XP total", default=0)
    xp_next_level = models.PositiveIntegerField("XP para próximo nível", default=100)
    coins         = models.PositiveIntegerField("Moedas", default=0)
    streak_days   = models.PositiveIntegerField("Streak (dias)", default=0)
    last_activity = models.DateField("Última atividade", null=True, blank=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return f"Perfil de {self.user.name} — Nível {self.level}"

    def add_xp(self, amount: int):
        """Adiciona XP e verifica se sobe de nível."""
        self.xp_total += amount
        while self.xp_total >= self.xp_next_level:
            self.xp_total -= self.xp_next_level
            self.level += 1
            self.xp_next_level = int(self.xp_next_level * 1.5)
        self.save()

    def update_streak(self):
        """Atualiza o streak diário."""
        today = timezone.localdate()
        if self.last_activity is None:
            self.streak_days = 1
        elif (today - self.last_activity).days == 1:
            self.streak_days += 1
        elif (today - self.last_activity).days > 1:
            self.streak_days = 1
        # Se já acessou hoje, não faz nada
        self.last_activity = today
        self.save()


# ─── Conteúdo educacional ────────────────────────────────────────────────────

class Module(models.Model):
    """
    Módulo de aprendizado (ex: 'Noções Básicas', 'Orçamento', 'Poupança').
    Representa cada parada na trilha de jogos.
    """
    title       = models.CharField("Título", max_length=100)
    description = models.TextField("Descrição", blank=True)
    icon        = models.CharField("Ícone (emoji ou nome)", max_length=50, blank=True)
    order_index = models.PositiveSmallIntegerField("Ordem", default=0)
    is_active   = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ["order_index"]

    def __str__(self):
        return f"{self.order_index}. {self.title}"


class Lesson(models.Model):
    """
    Lição dentro de um módulo. Pode ser quiz, desafio ou conteúdo teórico.
    """
    LESSON_TYPES = [
        ("quiz",      "Quiz"),
        ("challenge", "Desafio"),
        ("content",   "Conteúdo"),
    ]

    module      = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title       = models.CharField("Título", max_length=150)
    content     = models.TextField("Conteúdo / enunciado")
    lesson_type = models.CharField("Tipo", max_length=20, choices=LESSON_TYPES, default="content")
    order_index = models.PositiveSmallIntegerField("Ordem dentro do módulo", default=0)
    xp_reward   = models.PositiveIntegerField("Recompensa XP", default=10)
    coins_reward= models.PositiveIntegerField("Recompensa Moedas", default=5)

    class Meta:
        verbose_name = "Lição"
        verbose_name_plural = "Lições"
        ordering = ["module", "order_index"]

    def __str__(self):
        return f"{self.module.title} › {self.title}"


class UserLessonProgress(models.Model):
    """
    Registro de progresso de um usuário em cada lição.
    """
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="user_progress")
    completed    = models.BooleanField("Concluída", default=False)
    score        = models.PositiveSmallIntegerField("Pontuação (0-100)", default=0)
    completed_at = models.DateTimeField("Concluída em", null=True, blank=True)

    class Meta:
        verbose_name = "Progresso na lição"
        verbose_name_plural = "Progressos nas lições"
        unique_together = ("user", "lesson")

    def __str__(self):
        status = "✓" if self.completed else "…"
        return f"{status} {self.user.name} → {self.lesson.title}"


# ─── Conquistas / Badges ─────────────────────────────────────────────────────

class Badge(models.Model):
    """
    Medalha/conquista disponível na plataforma.
    """
    BADGE_CATEGORIES = [
        ("progress",  "Progresso"),
        ("streak",    "Sequência"),
        ("financial", "Financeiro"),
        ("social",    "Social"),
        ("special",   "Especial"),
    ]

    title              = models.CharField("Título", max_length=100)
    description        = models.TextField("Descrição")
    icon               = models.CharField("Ícone", max_length=100, blank=True)
    category           = models.CharField("Categoria", max_length=20, choices=BADGE_CATEGORIES)
    locked_by_default  = models.BooleanField("Bloqueada por padrão", default=True)

    class Meta:
        verbose_name = "Conquista"
        verbose_name_plural = "Conquistas"

    def __str__(self):
        return self.title


class UserBadge(models.Model):
    """
    Relação entre usuário e as conquistas que ele desbloqueou.
    """
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges")
    badge     = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="earned_by")
    earned_at = models.DateTimeField("Conquistada em", auto_now_add=True)

    class Meta:
        verbose_name = "Conquista do usuário"
        verbose_name_plural = "Conquistas dos usuários"
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user.name} desbloqueou '{self.badge.title}'"


# ─── Leaderboard ─────────────────────────────────────────────────────────────

class LeaderboardEntry(models.Model):
    """
    Entrada no ranking. Pode ser global, por amigos ou por escola.
    Recalculada periodicamente (ex: semanalmente via Celery).
    """
    SCOPE_CHOICES = [
        ("global",  "Global"),
        ("friends", "Amigos"),
        ("school",  "Escola"),
    ]

    user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leaderboard_entries")
    coins  = models.PositiveIntegerField("Moedas no período")
    rank   = models.PositiveIntegerField("Posição")
    scope  = models.CharField("Escopo", max_length=20, choices=SCOPE_CHOICES, default="global")
    period = models.DateField("Período (início da semana)")

    class Meta:
        verbose_name = "Entrada no ranking"
        verbose_name_plural = "Entradas no ranking"
        unique_together = ("user", "scope", "period")
        ordering = ["scope", "period", "rank"]

    def __str__(self):
        return f"#{self.rank} {self.user.name} — {self.get_scope_display()} ({self.period})"
