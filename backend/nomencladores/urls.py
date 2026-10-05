from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('categorias-docentes', views.CategoriaDocenteViewSet, basename='categoria-docente')
router.register('categorias-cientificas', views.CategoriaCientificaViewSet, basename='categoria-cientifica')
router.register('cargos', views.CargoViewSet, basename='cargo')
router.register('carreras', views.CarreraViewSet, basename='carrera')

urlpatterns = router.urls
