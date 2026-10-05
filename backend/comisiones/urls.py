from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('comisiones', views.ComisionViewSet, basename='comision')

urlpatterns = [
    path('comisiones-mias/', views.mis_comisiones_view),
] + router.urls
