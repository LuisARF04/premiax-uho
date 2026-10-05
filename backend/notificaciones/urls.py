from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('notificaciones', views.NotificacionViewSet, basename='notificacion')

urlpatterns = [
    path('usuarios-inactivos/', views.usuarios_inactivos_view),
] + router.urls
