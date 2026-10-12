from django.db import models


class Notificacion(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=50, default='sistema')
    titulo = models.CharField(max_length=250)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    url_accion = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.titulo} -> {self.usuario}'


class EventoEtapa(models.Model):
    """Registro de avisos de etapa ya enviados, para no notificar dos veces lo mismo (RF-025)."""
    etapa = models.ForeignKey('premios.EtapaProceso', on_delete=models.CASCADE, related_name='eventos')
    tipo = models.CharField(max_length=20, choices=[('inicio', 'Inicio de etapa'), ('alerta', 'Alerta de fecha límite')])
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('etapa', 'tipo')
