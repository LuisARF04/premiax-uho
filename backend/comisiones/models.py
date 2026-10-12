from django.db import models


class Comision(models.Model):
    nombre = models.CharField(max_length=200)
    jefe = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, related_name='comisiones_dirigidas')
    premios = models.ManyToManyField('premios.Premio', related_name='comisiones', blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class MiembroComision(models.Model):
    comision = models.ForeignKey(Comision, on_delete=models.CASCADE, related_name='miembros')
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='comisiones_miembro')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comision', 'usuario')

    def __str__(self):
        return f'{self.usuario} en {self.comision}'


class AsignacionRevision(models.Model):
    """Revisión de una propuesta asignada por el jefe de comisión a un miembro (RF-016)."""
    propuesta = models.ForeignKey('propuestas.Propuesta', on_delete=models.CASCADE, related_name='revisiones')
    miembro = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='revisiones_asignadas')
    asignado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, related_name='revisiones_encargadas')
    criterio = models.TextField(blank=True)
    puntuacion = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Puntuación de 1 a 10.')
    revisada = models.BooleanField(default=False)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('propuesta', 'miembro')
        ordering = ['fecha_asignacion']

    def __str__(self):
        return f'{self.miembro} revisa {self.propuesta_id}'
