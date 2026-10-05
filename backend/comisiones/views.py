from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auditoria.utils import registrar
from notificaciones.utils import notificar
from usuarios.models import Usuario
from usuarios.permissions import IsGestorGlobal, hay_privilegio
from usuarios.models import Rol
from .models import Comision, MiembroComision
from .serializers import ComisionSerializer, MiembroComisionSerializer


class ComisionViewSet(viewsets.ModelViewSet):
    queryset = Comision.objects.select_related('jefe').prefetch_related('miembros__usuario', 'premios').all()
    serializer_class = ComisionSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsGestorGlobal()]

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Crear comisión', 'comisiones', instance.nombre, self.request)
        if instance.jefe:
            notificar(instance.jefe, 'comisiones', 'Se te asignó como jefe de comisión',
                      f'Fuiste designado jefe de la comisión "{instance.nombre}".')

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Editar comisión', 'comisiones', instance.nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar comisión', 'comisiones', instance.nombre, self.request)
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def agregar_miembro(self, request, pk=None):
        comision = self.get_object()
        if not (hay_privilegio(request.user, Rol.GESTOR_GLOBAL) or comision.jefe_id == request.user.id):
            return Response({'detail': 'No autorizado.'}, status=403)
        usuario_id = request.data.get('usuario')
        usuario = Usuario.objects.filter(pk=usuario_id).first()
        if not usuario:
            return Response({'detail': 'Usuario no encontrado.'}, status=404)
        miembro, creado = MiembroComision.objects.get_or_create(comision=comision, usuario=usuario)
        if creado:
            registrar(request.user, 'Añadir miembro a comisión', 'comisiones', f'{usuario} -> {comision}', request)
            notificar(usuario, 'comisiones', 'Fuiste añadido a una comisión', f'Formas parte de la comisión "{comision.nombre}".')
        return Response(MiembroComisionSerializer(miembro).data)

    @action(detail=True, methods=['delete'], url_path='miembros/(?P<miembro_id>[^/.]+)', permission_classes=[IsAuthenticated])
    def quitar_miembro(self, request, pk=None, miembro_id=None):
        comision = self.get_object()
        if not (hay_privilegio(request.user, Rol.GESTOR_GLOBAL) or comision.jefe_id == request.user.id):
            return Response({'detail': 'No autorizado.'}, status=403)
        MiembroComision.objects.filter(comision=comision, pk=miembro_id).delete()
        registrar(request.user, 'Quitar miembro de comisión', 'comisiones', str(miembro_id), request)
        return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_comisiones_view(request):
    """Comisiones donde el usuario es jefe o miembro."""
    qs = Comision.objects.filter(jefe=request.user) | Comision.objects.filter(miembros__usuario=request.user)
    qs = qs.distinct().select_related('jefe').prefetch_related('miembros__usuario', 'premios')
    return Response(ComisionSerializer(qs, many=True).data)
