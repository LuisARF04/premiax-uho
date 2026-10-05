from django.contrib import admin

from .models import CategoriaPremio, EtapaProceso, Premio


@admin.register(CategoriaPremio)
class CategoriaPremioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo', 'orden')


@admin.register(Premio)
class PremioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'cant_premios', 'cant_reconocimientos', 'es_por_comision', 'activo')
    list_filter = ('categoria', 'es_por_comision')


@admin.register(EtapaProceso)
class EtapaProcesoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'anio', 'fecha_inicio', 'fecha_cierre', 'orden')
    list_filter = ('anio',)
