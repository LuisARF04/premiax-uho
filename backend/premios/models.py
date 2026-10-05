from django.db import models
from django.utils import timezone


class TipoCategoria(models.TextChoices):
    IND_DOCENTE = 'ind_docente', 'Individuales Docentes'
    IND_NO_DOCENTE = 'ind_no_docente', 'Individuales No Docentes'
    COL_DOCENTE = 'col_docente', 'Colectivos Docentes'
    COL_NO_DOCENTE = 'col_no_docente', 'Colectivos No Docentes'


class CategoriaPremio(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TipoCategoria.choices)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name_plural = 'Categorías de Premio'

    def __str__(self):
        return self.nombre


class Premio(models.Model):
    nombre = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True)
    criterios = models.TextField(blank=True)
    categoria = models.ForeignKey(CategoriaPremio, on_delete=models.CASCADE, related_name='premios')
    cant_premios = models.PositiveIntegerField(default=1)
    cant_reconocimientos = models.PositiveIntegerField(default=0)
    es_por_comision = models.BooleanField(default=False, help_text="No requiere propuesta de área; la comisión asigna directamente.")
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['categoria__orden', 'nombre']

    def __str__(self):
        return self.nombre


class EtapaProceso(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    anio = models.PositiveIntegerField(default=timezone.now().year)
    orden = models.PositiveIntegerField(default=0)
    responsable_desc = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['anio', 'orden']

    def __str__(self):
        return f'{self.nombre} ({self.anio})'

    @property
    def estado(self):
        hoy = timezone.now().date()
        if hoy < self.fecha_inicio:
            return 'proxima'
        if hoy > self.fecha_cierre:
            return 'finalizada'
        return 'en_curso'
