from django.contrib import admin

from .models import HistorialPropuesta, Propuesta


class HistorialInline(admin.TabularInline):
    model = HistorialPropuesta
    extra = 0


@admin.register(Propuesta)
class PropuestaAdmin(admin.ModelAdmin):
    list_display = ('candidato_nombre', 'premio', 'estado', 'nivel_actual', 'anio', 'fecha_creacion')
    list_filter = ('estado', 'nivel_actual', 'anio')
    search_fields = ('candidato_nombre',)
    inlines = [HistorialInline]
