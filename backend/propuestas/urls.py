from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('propuestas', views.PropuestaViewSet, basename='propuesta')

urlpatterns = router.urls
