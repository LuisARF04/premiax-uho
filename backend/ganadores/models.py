from django.db import models
from django.utils import timezone


class TipoGanador(models.TextChoices):
    PREMIO = 'premio', 'Premio'
    RECONOCIMIENTO = 'reconocimiento', 'Reconocimiento'


class Ganador(models.Model):
    propuesta = models.ForeignKey('propuestas.Propuesta', on_delete=models.SET_NULL, null=True, blank=True, related_name='ganador')
    premio = models.ForeignKey('premios.Premio', on_delete=models.CASCADE, related_name='ganadores')
    persona_nombre = models.CharField(max_length=250)
    persona_area = models.CharField(max_length=200, blank=True)
    categoria_cientifica = models.CharField(max_length=100, blank=True)
    categoria_docente = models.CharField(max_length=100, blank=True)
    foto_url = models.ImageField(upload_to='ganadores/', null=True, blank=True)
    fundamentacion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TipoGanador.choices, default=TipoGanador.PREMIO)
    anio = models.PositiveIntegerField(default=timezone.now().year)
    aprobado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='ganadores_aprobados')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    publicado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-anio', 'premio__categoria__orden']

    def __str__(self):
        return f'{self.persona_nombre} - {self.premio} ({self.anio})'
