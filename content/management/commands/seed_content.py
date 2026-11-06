from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import Lesson, Module, Question
from content.seed_data import PLAY_QUESTIONS, VARIACOES


MODULOS = {
    "base": {
        "title": "Nível Base",
        "order": 1,
        "icon": "trilha",
    },
    "medio": {
        "title": "Nível Médio",
        "order": 2,
        "icon": "carteira",
    },
    "avancado": {
        "title": "Nível Avançado",
        "order": 3,
        "icon": "bank_",
    },
}


FASES = [
    ("base", 1, "Fundamentos do dinheiro", "Orçamento e poupança", [1, 2, 3, 4, 5]),
    ("base", 2, "Crédito e primeiros passos", "Crédito e investimento", [6, 7, 8, 9, 10]),
    ("medio", 1, "Renda fixa e variável", "Investimentos", [11, 12, 13, 14, 15]),
    ("medio", 2, "Estratégia de aportes", "Estratégia", [16, 17, 18, 19, 20]),
    ("avancado", 1, "Risco e comportamento", "Risco", [21, 22, 23, 24, 25]),
    ("avancado", 2, "Macro e finanças", "Macroeconomia", [26, 27, 28, 29, 30]),
]


class Command(BaseCommand):
    help = "Cria ou atualiza as fases e os quatro formatos de pergunta."

    @transaction.atomic
    def handle(self, *args, **options):
        perguntas_por_id = {
            pergunta["id"]: pergunta for pergunta in PLAY_QUESTIONS
        }

        modulos = {}

        for chave, dados in MODULOS.items():
            modulo, _ = Module.objects.update_or_create(
                order_index=dados["order"],
                defaults={
                    "title": dados["title"],
                    "icon": dados["icon"],
                    "is_active": True,
                },
            )
            modulos[chave] = modulo

        for nivel, ordem, titulo, tema, ids in FASES:
            fase, _ = Lesson.objects.update_or_create(
                module=modulos[nivel],
                order_index=ordem,
                defaults={
                    "title": titulo,
                    "topic": tema,
                    "xp_reward": 20,
                    "coins_reward": 10,
                },
            )

            tipos_gravados = []

            for posicao, pergunta_id in enumerate(ids, start=1):
                original = perguntas_por_id[pergunta_id]

                if pergunta_id in VARIACOES:
                    conteudo = VARIACOES[pergunta_id]
                else:
                    conteudo = {
                        "kind": Question.KIND_TF,
                        "statement": original["statement"],
                        "payload": {"answer": original["answer"]},
                        "explanation": original["explanation"],
                    }

                pergunta, _ = Question.objects.update_or_create(
                    lesson=fase,
                    order_index=posicao,
                    defaults={
                        **conteudo,
                        "xp_reward": original["xp"],
                        "coins_reward": original["coins"],
                    },
                )

                tipos_gravados.append(pergunta.kind)

            self.stdout.write(f"{fase.title}: {', '.join(tipos_gravados)}")

        self.stdout.write(self.style.SUCCESS("Perguntas atualizadas!"))