from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('categorias-premio', views.CategoriaPremioViewSet, basename='categoria-premio')
router.register('premios', views.PremioViewSet, basename='premio')
router.register('etapas', views.EtapaProcesoViewSet, basename='etapa')

urlpatterns = [
    path('publico/categorias/', views.publico_categorias_view),
    path('publico/calendario/', views.publico_calendario_view),
    path('publico/convocatoria-activa/', views.publico_convocatoria_activa_view),
] + router.urls
