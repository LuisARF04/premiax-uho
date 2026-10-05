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
