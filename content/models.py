from django.db import models
import unicodedata
from django.core.exceptions import ValidationError

class Module(models.Model):
    title       = models.CharField("Título", max_length=100)
    description = models.TextField("Descrição", blank=True)
    icon        = models.CharField("Ícone", max_length=50, blank=True)
    order_index = models.PositiveSmallIntegerField("Ordem", default=0)
    is_active   = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ["order_index"]

    def __str__(self):
        return f"{self.order_index}. {self.title}"


class Lesson(models.Model):
    """Uma fase da trilha."""
    module       = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title        = models.CharField("Título", max_length=150)
    topic        = models.CharField("Tema", max_length=80, blank=True)
    description  = models.TextField("Descrição", blank=True)
    order_index  = models.PositiveSmallIntegerField("Ordem no módulo", default=0)
    xp_reward    = models.PositiveIntegerField("XP ao concluir", default=20)
    coins_reward = models.PositiveIntegerField("Moedas ao concluir", default=10)

    class Meta:
        verbose_name = "Fase"
        verbose_name_plural = "Fases"
        ordering = ["module", "order_index"]

    def __str__(self):
        return f"{self.module.title} › {self.title}"


class Question(models.Model):
    KIND_TF, KIND_MC, KIND_FILL, KIND_MATCH = "tf", "mc", "fill", "match"
    KINDS = [
        (KIND_TF,    "Verdadeiro ou falso"),
        (KIND_MC,    "Múltipla escolha"),
        (KIND_FILL,  "Completar a frase"),
        (KIND_MATCH, "Associar pares"),
    ]

    lesson       = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions")
    kind         = models.CharField("Tipo", max_length=10, choices=KINDS, default=KIND_MC)
    order_index  = models.PositiveSmallIntegerField("Ordem na fase", default=0)
    statement    = models.TextField("Enunciado")
    explanation  = models.TextField("Explicação", blank=True)
    payload      = models.JSONField("Dados da pergunta", default=dict)
    xp_reward    = models.PositiveIntegerField("XP", default=10)
    coins_reward = models.PositiveIntegerField("Moedas", default=5)

    class Meta:
        verbose_name = "Pergunta"
        verbose_name_plural = "Perguntas"
        ordering = ["lesson", "order_index"]

    def __str__(self):
        return f"{self.lesson.title} › {self.get_kind_display()} #{self.order_index}"

    def clean(self):
        p = self.payload or {}

        if self.kind == self.KIND_TF:
            if not isinstance(p.get("answer"), bool):
                raise ValidationError({"payload": 'Use {"answer": true} ou {"answer": false}.'})

        elif self.kind == self.KIND_MC:
            opcoes, idx = p.get("options"), p.get("answer")
            if not isinstance(opcoes, list) or len(opcoes) < 2:
                raise ValidationError({"payload": '"options" precisa de ao menos 2 alternativas.'})
            if not isinstance(idx, int) or not (0 <= idx < len(opcoes)):
                raise ValidationError({"payload": '"answer" deve ser o índice da correta.'})

        elif self.kind == self.KIND_FILL:
            if "___" not in self.statement:
                raise ValidationError({"statement": "Use ___ para marcar a lacuna."})
            if not p.get("answer"):
                raise ValidationError({"payload": '"answer" é obrigatório.'})

        elif self.kind == self.KIND_MATCH:
            if not isinstance(p.get("pairs"), list) or len(p["pairs"]) < 2:
                raise ValidationError({"payload": '"pairs" precisa de ao menos 2 pares.'})

    def check_answer(self, resposta) -> bool:
        """Correção sempre no servidor. O gabarito nunca vai para o front."""
        p = self.payload or {}

        if self.kind == self.KIND_TF:
            return resposta is p.get("answer")

        if self.kind == self.KIND_MC:
            return resposta == p.get("answer")

        if self.kind == self.KIND_FILL:
            if not isinstance(resposta, str):
                return False
            aceitas = [p.get("answer"), *p.get("also_accept", [])]
            return self._normaliza(resposta) in {self._normaliza(a) for a in aceitas if a}

        if self.kind == self.KIND_MATCH:
            if not isinstance(resposta, dict):
                return False
            return all(str(resposta.get(str(e))) == str(d) for e, d in p.get("pairs", []))

        return False

    @staticmethod
    def _normaliza(texto) -> str:
        return "".join(
            c for c in unicodedata.normalize("NFD", str(texto).strip().lower())
            if unicodedata.category(c) != "Mn"
        )