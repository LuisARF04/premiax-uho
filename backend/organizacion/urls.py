from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('areas', views.AreaViewSet, basename='area')
router.register('departamentos', views.DepartamentoViewSet, basename='departamento')

urlpatterns = router.urls
