from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('usuarios', views.UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('auth/login/', views.login_view),
    path('auth/logout/', views.logout_view),
    path('auth/me/', views.me_view),
    path('auth/completar-perfil/', views.completar_perfil_view),
    path('usuarios/buscar/', views.buscar_usuarios_view),
] + router.urls
