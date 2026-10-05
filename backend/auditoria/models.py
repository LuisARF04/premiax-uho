from django.db import models


class LogAuditoria(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    accion = models.CharField(max_length=200)
    modulo = models.CharField(max_length=100)
    detalle = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.fecha} - {self.usuario} - {self.accion}'
