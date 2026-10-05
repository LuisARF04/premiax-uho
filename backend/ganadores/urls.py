from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('ganadores', views.GanadorViewSet, basename='ganador')

urlpatterns = [
    path('publico/ganadores/', views.publico_ganadores_view),
    path('publico/ganadores/anios/', views.publico_anios_view),
] + router.urls
