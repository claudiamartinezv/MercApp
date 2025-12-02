
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

from mercapp.models import Respaldo

User = get_user_model()


class Command(BaseCommand):
    help = "Genera un respaldo de la base de datos"

    def add_arguments(self, parser):
        parser.add_argument("--usuario", type=str, required=True)
        parser.add_argument("--tipo", type=str, choices=["AUTOMATICO", "MANUAL"], default="MANUAL")
        parser.add_argument("--dir", type=str, default="backups")

    def handle(self, *args, **options):
        username = options["usuario"]
        tipo = options["tipo"]
        backup_dir = options["dir"]

        usuario = User.objects.get(username=username)

        base_dir = settings.BASE_DIR
        backup_path = os.path.join(base_dir, backup_dir)
        os.makedirs(backup_path, exist_ok=True)

        ahora = timezone.now()
        filename = f"respaldo_{ahora.strftime('%Y%m%d_%H%M%S')}.json"
        full_path = os.path.join(backup_path, filename)

        with open(full_path, "w", encoding="utf-8") as f:
            call_command("dumpdata", "--indent", "2", stdout=f)

        Respaldo.objects.create(
            fecha=ahora,
            tipo=tipo,
            ubicacion=os.path.relpath(full_path, base_dir),
            usuario=usuario,
        )

        self.stdout.write(self.style.SUCCESS(f"Respaldo creado: {full_path}"))
