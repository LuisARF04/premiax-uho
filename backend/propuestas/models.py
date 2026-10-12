from django.db import models
from django.utils import timezone


class EstadoPropuesta(models.TextChoices):
    PENDIENTE_DEPARTAMENTO = 'pendiente_departamento', 'Pendiente de Departamento'
    PENDIENTE_AREA = 'pendiente_area', 'Pendiente de elevación a Área'
    EN_COMISION = 'en_comision', 'En revisión de Comisión'
    GANADORA_PROPUESTA = 'ganadora_propuesta', 'Propuesta como ganadora'
    APROBADA = 'aprobada', 'Aprobada'
    RECHAZADA = 'rechazada', 'Rechazada'


class NivelPropuesta(models.TextChoices):
    DEPARTAMENTO = 'departamento', 'Departamento'
    AREA = 'area', 'Área'
    COMISION = 'comision', 'Comisión'
    UNIVERSIDAD = 'universidad', 'Universidad'


class Propuesta(models.Model):
    premio = models.ForeignKey('premios.Premio', on_delete=models.CASCADE, related_name='propuestas')
    creado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='propuestas_creadas')
    area = models.ForeignKey('organizacion.Area', on_delete=models.SET_NULL, null=True, related_name='propuestas')
    departamento = models.ForeignKey('organizacion.Departamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='propuestas')

    candidato_nombre = models.CharField(max_length=250, help_text="Nombre del candidato (si distinto al proponente) o nombre del colectivo.")
    candidato_usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='propuestas_como_candidato')
    resumen = models.TextField()
    documento = models.FileField(upload_to='fundamentaciones/', null=True, blank=True)

    estado = models.CharField(max_length=30, choices=EstadoPropuesta.choices, default=EstadoPropuesta.PENDIENTE_DEPARTAMENTO)
    nivel_actual = models.CharField(max_length=20, choices=NivelPropuesta.choices, default=NivelPropuesta.DEPARTAMENTO)
    comision = models.ForeignKey('comisiones.Comision', on_delete=models.SET_NULL, null=True, blank=True, related_name='propuestas_asignadas')
    seleccion_comision = models.CharField(
        max_length=20, blank=True,
        choices=[('premio', 'Premio Rector'), ('reconocimiento', 'Reconocimiento')],
        help_text='Selección hecha por el jefe de comisión al proponer ganadores.'
    )
    fundamentacion_comision = models.TextField(blank=True)

    version = models.PositiveIntegerField(default=1)
    anio = models.PositiveIntegerField(default=timezone.now().year)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    retroactiva = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.candidato_nombre} - {self.premio} ({self.anio})'


class HistorialPropuesta(models.Model):
    propuesta = models.ForeignKey(Propuesta, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    nivel_desde = models.CharField(max_length=20, blank=True)
    nivel_hasta = models.CharField(max_length=20, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f'{self.accion} - {self.propuesta}'


class VersionPropuesta(models.Model):
    """Copia de cada versión de la propuesta (RF-018): quién, cuándo y con qué contenido/documento."""
    propuesta = models.ForeignKey(Propuesta, on_delete=models.CASCADE, related_name='versiones')
    version = models.PositiveIntegerField()
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True)
    candidato_nombre = models.CharField(max_length=250)
    resumen = models.TextField()
    documento = models.FileField(upload_to='fundamentaciones/versiones/', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['version']
        unique_together = ('propuesta', 'version')

    def __str__(self):
        return f'{self.propuesta_id} v{self.version}'
