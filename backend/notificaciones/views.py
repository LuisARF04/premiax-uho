from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.models import Usuario
from usuarios.permissions import IsGestorGlobal
from .models import Notificacion
from .serializers import NotificacionSerializer


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSerializer

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    @action(detail=True, methods=['patch'])
    def marcar_leida(self, request, pk=None):
        notif = self.get_object()
        notif.leida = True
        notif.save(update_fields=['leida'])
        return Response(NotificacionSerializer(notif).data)

    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        self.get_queryset().update(leida=True)
        return Response({'detail': 'ok'})


@api_view(['GET'])
@permission_classes([IsGestorGlobal])
def usuarios_inactivos_view(request):
    """RF-026: usuarios que no han entrado o no tienen actividad reciente."""
    limite = timezone.now() - timezone.timedelta(days=7)
    qs = Usuario.objects.filter(activo=True).exclude(rol='usuario').order_by('last_login')
    resultado = []
    for u in qs:
        if u.last_login is None or u.last_login < limite:
            dias = (timezone.now() - u.last_login).days if u.last_login else None
            resultado.append({
                'id': u.id, 'nombre': u.get_full_name() or u.username, 'rol': u.get_rol_display(),
                'area': u.area.nombre if u.area else None, 'dias_inactivo': dias,
                'pendientes': u.propuestas_creadas.exclude(estado__in=['aprobada', 'rechazada']).count()
                if hasattr(u, 'propuestas_creadas') else 0,
            })
    return Response(resultado)
