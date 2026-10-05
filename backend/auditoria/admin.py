from django.contrib import admin

from .models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion', 'modulo', 'ip')
    list_filter = ('modulo',)
    search_fields = ('accion', 'detalle')
