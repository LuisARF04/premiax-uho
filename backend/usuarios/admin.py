from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'rol', 'area', 'departamento', 'activo')
    list_filter = ('rol', 'area', 'activo')
    fieldsets = UserAdmin.fieldsets + (
        ('PREMIAX-UHO', {
            'fields': (
                'correo_institucional', 'tipo_aga', 'rol', 'area', 'departamento',
                'categoria_docente', 'categoria_cientifica', 'cargo', 'foto', 'foto_publica',
                'perfil_completo', 'activo',
            )
        }),
    )
