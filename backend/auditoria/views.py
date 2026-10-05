from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from usuarios.permissions import IsAdmin
from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer


class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogAuditoria.objects.select_related('usuario').all()
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['modulo', 'usuario']
    search_fields = ['accion', 'detalle', 'usuario__username']
    ordering = ['-fecha']
