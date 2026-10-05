from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('auditoria', views.LogAuditoriaViewSet, basename='auditoria')

urlpatterns = router.urls
