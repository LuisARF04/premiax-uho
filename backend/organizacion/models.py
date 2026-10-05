from django.db import models


class Area(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True)
    responsable = models.ForeignKey(
        'usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='areas_responsable'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='departamentos')
    responsable = models.ForeignKey(
        'usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='departamentos_responsable'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['area__nombre', 'nombre']
        unique_together = ('nombre', 'area')

    def __str__(self):
        return f'{self.nombre} ({self.area.nombre})'
