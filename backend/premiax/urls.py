from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import api_root

urlpatterns = [
    path('', api_root, name='project-root'),
    path('api/', api_root, name='project-api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('usuarios.urls')),
    path('api/', include('organizacion.urls')),
    path('api/', include('nomencladores.urls')),
    path('api/', include('premios.urls')),
    path('api/', include('propuestas.urls')),
    path('api/', include('comisiones.urls')),
    path('api/', include('ganadores.urls')),
    path('api/', include('notificaciones.urls')),
    path('api/', include('auditoria.urls')),
    path('api/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
