from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from auditoria.utils import registrar
from usuarios.permissions import IsAdmin
from .models import CategoriaPremio, EtapaProceso, Premio
from .serializers import (
    CategoriaPremioPublicaSerializer, CategoriaPremioSerializer, EtapaProcesoSerializer, PremioSerializer,
)


class CategoriaPremioViewSet(viewsets.ModelViewSet):
    queryset = CategoriaPremio.objects.prefetch_related('premios').all()
    serializer_class = CategoriaPremioSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Crear categoría de premio', 'premios', instance.nombre, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Editar categoría de premio', 'premios', instance.nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar categoría de premio', 'premios', instance.nombre, self.request)
        instance.delete()


class PremioViewSet(viewsets.ModelViewSet):
    queryset = Premio.objects.select_related('categoria').all()
    serializer_class = PremioSerializer
    filterset_fields = ['categoria', 'es_por_comision', 'activo']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Crear premio', 'premios', instance.nombre, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Editar premio', 'premios', instance.nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar premio', 'premios', instance.nombre, self.request)
        instance.delete()


class EtapaProcesoViewSet(viewsets.ModelViewSet):
    queryset = EtapaProceso.objects.all()
    serializer_class = EtapaProcesoSerializer
    filterset_fields = ['anio']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Crear etapa', 'premios', instance.nombre, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Editar etapa', 'premios', instance.nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar etapa', 'premios', instance.nombre, self.request)
        instance.delete()


@api_view(['GET'])
@permission_classes([AllowAny])
def publico_categorias_view(request):
    """RF-002: categorías y premios visibles en el landing (sin cantidades)."""
    qs = CategoriaPremio.objects.filter(activo=True).prefetch_related('premios')
    return Response(CategoriaPremioPublicaSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def publico_calendario_view(request):
    """RF-004: calendario del proceso, para el año actual (o ?anio=)."""
    anio = request.query_params.get('anio', timezone.now().year)
    qs = EtapaProceso.objects.filter(anio=anio)
    return Response(EtapaProcesoSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def publico_convocatoria_activa_view(request):
    """RF-005: indica si hay una etapa de convocatoria (subida de propuestas) activa."""
    hoy = timezone.now().date()
    activa = EtapaProceso.objects.filter(
        fecha_inicio__lte=hoy, fecha_cierre__gte=hoy, nombre__icontains='convocatoria'
    ).exists()
    return Response({'convocatoria_activa': activa})
