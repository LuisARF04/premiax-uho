from django.db import models


class NomencladorBase(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class CategoriaDocente(NomencladorBase):
    """Instructor, Profesor Asistente, Auxiliar, Titular..."""


class CategoriaCientifica(NomencladorBase):
    """Lic., MSc., Dr.C. ..."""


class Cargo(NomencladorBase):
    """Decano, Jefe de Departamento, Jefe de Carrera..."""


class Carrera(NomencladorBase):
    """Carreras universitarias."""
