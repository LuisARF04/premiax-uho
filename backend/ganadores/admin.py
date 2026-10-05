from django.contrib import admin

from .models import Ganador


@admin.register(Ganador)
class GanadorAdmin(admin.ModelAdmin):
    list_display = ('persona_nombre', 'premio', 'tipo', 'anio', 'publicado')
    list_filter = ('anio', 'tipo', 'publicado')
