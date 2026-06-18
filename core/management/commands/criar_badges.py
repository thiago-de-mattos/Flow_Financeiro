from django.core.management.base import BaseCommand
from core.models import Badge

class Command(BaseCommand):
    help = "Cria as conquistas iniciais"

    def handle(self, *args, **kwargs):
        badges = [
            {
                "title": "Primeiros Passos",
                "description": "Complete sua primeira lição",
                "icon": "first_step",
                "category": "progress",
                "locked_by_default": True,
            },
            {
                "title": "Poupador",
                "description": "Junte 100 moedas",
                "icon": "save",
                "category": "financial",
                "locked_by_default": True,
            },
            {
                "title": "Organizado",
                "description": "Crie seu primeiro orçamento",
                "icon": "budgeter",
                "category": "financial",
                "locked_by_default": True,
            },
            {
                "title": "Investidor",
                "description": "Complete 3 módulos",
                "icon": "investor",
                "category": "progress",
                "locked_by_default": True,
            },
            {
                "title": "Sequência Master",
                "description": "7 dias seguidos de acesso",
                "icon": "streak_master",
                "category": "streak",
                "locked_by_default": True,
            },
            {
                "title": "Finance Pro",
                "description": "Complete 10 módulos",
                "icon": "finance_pro",
                "category": "progress",
                "locked_by_default": True,
            },
        ]

        for b in badges:
            Badge.objects.get_or_create(
                title=b["title"],
                defaults=b
            )
            self.stdout.write(f"✓ {b['title']}")

        self.stdout.write(self.style.SUCCESS("Badges criados com sucesso!"))