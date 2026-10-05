from django.contrib import admin

from .models import Cargo, Carrera, CategoriaCientifica, CategoriaDocente

admin.site.register(CategoriaDocente)
admin.site.register(CategoriaCientifica)
admin.site.register(Cargo)
admin.site.register(Carrera)
