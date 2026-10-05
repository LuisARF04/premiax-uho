from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/principal/', views.dashboard_principal_view),
    path('dashboard/estadisticas/', views.dashboard_estadisticas_view),
]
