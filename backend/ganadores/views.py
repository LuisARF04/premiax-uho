from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from auditoria.utils import registrar
from usuarios.permissions import IsGestorGlobal
from .models import Ganador
from .serializers import GanadorPublicoSerializer, GanadorSerializer


class GanadorViewSet(viewsets.ModelViewSet):
    """CRUD de ganadores: usado para registro retroactivo (RF-023) por admin/gestor global."""
    queryset = Ganador.objects.select_related('premio', 'premio__categoria').all()
    serializer_class = GanadorSerializer
    permission_classes = [IsGestorGlobal]
    filterset_fields = ['anio', 'premio', 'tipo']

    def perform_create(self, serializer):
        instance = serializer.save(publicado=True, aprobado_por=self.request.user, fecha_aprobacion=timezone.now())
        registrar(self.request.user, 'Registrar ganador retroactivo', 'ganadores', f'{instance.persona_nombre} - {instance.premio}', self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Editar ganador', 'ganadores', instance.persona_nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar ganador', 'ganadores', instance.persona_nombre, self.request)
        instance.delete()


@api_view(['GET'])
@permission_classes([AllowAny])
def publico_ganadores_view(request):
    """RF-003: galería de premiados, filtrable por año."""
    anio = request.query_params.get('anio')
    qs = Ganador.objects.filter(publicado=True).select_related('premio', 'premio__categoria')
    if anio:
        qs = qs.filter(anio=anio)
    return Response(GanadorPublicoSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def publico_anios_view(request):
    anios = list(Ganador.objects.filter(publicado=True).values_list('anio', flat=True).distinct().order_by('-anio'))
    return Response(anios)
