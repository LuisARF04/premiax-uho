from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.TextChoices):
    SUPERADMIN = 'superadmin', 'Superadmin'
    ADMIN = 'admin', 'Admin'
    GESTOR_GLOBAL = 'gestor_global', 'Gestor Global'
    JEFE_COMISION = 'jefe_comision', 'Jefe de Comisión'
    MIEMBRO_COMISION = 'miembro_comision', 'Miembro de Comisión'
    JEFE_AREA = 'jefe_area', 'Jefe de Área'
    JEFE_DEPARTAMENTO = 'jefe_departamento', 'Jefe de Departamento'
    USUARIO = 'usuario', 'Usuario'


# Orden descendente de privilegios (índice 0 = mayor privilegio).
ROL_JERARQUIA = [
    Rol.SUPERADMIN,
    Rol.ADMIN,
    Rol.GESTOR_GLOBAL,
    Rol.JEFE_COMISION,
    Rol.MIEMBRO_COMISION,
    Rol.JEFE_AREA,
    Rol.JEFE_DEPARTAMENTO,
    Rol.USUARIO,
]


def nivel_rol(rol: str) -> int:
    """Menor número = mayor privilegio. Rol desconocido = mínimo privilegio."""
    try:
        return ROL_JERARQUIA.index(rol)
    except ValueError:
        return len(ROL_JERARQUIA)


class TipoUsuarioAGA(models.TextChoices):
    TRABAJADOR = 'trabajador', 'Trabajador'
    INSTITUCIONAL = 'institucional', 'Institucional'
    ESTUDIANTE = 'estudiante', 'Estudiante'


class Usuario(AbstractUser):
    """
    Usuario del sistema. En producción los datos base (nombre, correo, cargo)
    provienen de AGA_AUTH; aquí se simula ese registro automático.
    """
    correo_institucional = models.EmailField(unique=True, blank=True, null=True)
    tipo_aga = models.CharField(max_length=20, choices=TipoUsuarioAGA.choices, default=TipoUsuarioAGA.TRABAJADOR)
    rol = models.CharField(max_length=30, choices=Rol.choices, default=Rol.USUARIO)
    area = models.ForeignKey('organizacion.Area', null=True, blank=True, on_delete=models.SET_NULL, related_name='usuarios')
    departamento = models.ForeignKey('organizacion.Departamento', null=True, blank=True, on_delete=models.SET_NULL, related_name='usuarios')
    categoria_docente = models.ForeignKey('nomencladores.CategoriaDocente', null=True, blank=True, on_delete=models.SET_NULL, related_name='usuarios')
    categoria_cientifica = models.ForeignKey('nomencladores.CategoriaCientifica', null=True, blank=True, on_delete=models.SET_NULL, related_name='usuarios')
    cargo = models.ForeignKey('nomencladores.Cargo', null=True, blank=True, on_delete=models.SET_NULL, related_name='usuarios')
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    foto_publica = models.BooleanField(default=True, help_text='Si su foto puede mostrarse en el landing page.')
    perfil_completo = models.BooleanField(default=False, help_text='Ya seleccionó área/departamento en primer acceso.')
    notif_email = models.BooleanField(default=True)
    notif_fechas_limite = models.BooleanField(default=True)
    notif_propuestas_elevadas = models.BooleanField(default=True)
    notif_resumen_semanal = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def nivel(self) -> int:
        return nivel_rol(self.rol)

    def tiene_privilegio_de(self, rol: str) -> bool:
        return self.nivel() <= nivel_rol(rol)

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_rol_display()})'
