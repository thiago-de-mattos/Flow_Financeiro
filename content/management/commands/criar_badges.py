from django.core.management.base import BaseCommand
from gamification.services.badges import DEFAULT_BADGES, ensure_default_badges


class Command(BaseCommand):
    help = "Cria ou atualiza as conquistas padrão"

    def handle(self, *args, **options):
        ensure_default_badges(overwrite=True)
        for badge in DEFAULT_BADGES:
            self.stdout.write(f"  ✓ {badge['title']}")
        self.stdout.write(self.style.SUCCESS("Badges prontos!"))