from django.contrib import admin

from .models import Comision, MiembroComision


class MiembroInline(admin.TabularInline):
    model = MiembroComision
    extra = 0


@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'jefe', 'activo')
    filter_horizontal = ('premios',)
    inlines = [MiembroInline]
