from django.core.management.base import BaseCommand

from notificaciones.utils import procesar_etapas


class Command(BaseCommand):
    help = 'Envía los avisos de inicio de etapa y las alertas de fecha límite próximas (programar con cron una vez al día).'

    def handle(self, *args, **options):
        enviados = procesar_etapas(forzar=True)
        self.stdout.write(self.style.SUCCESS(f'Avisos de etapa generados: {enviados}'))
