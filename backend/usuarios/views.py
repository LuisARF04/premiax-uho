from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from auditoria.utils import registrar
from .models import Rol, TipoUsuarioAGA, Usuario
from .permissions import IsAdmin, IsSuperadmin, hay_privilegio
from .serializers import (
    CambiarRolSerializer, CompletarPerfilSerializer, PerfilSerializer, UsuarioMiniSerializer, UsuarioSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Simula el flujo de AGA_AUTH: valida credenciales y el tipo de usuario.
    En producción esto sería reemplazado por la redirección OAuth2/OIDC real.
    """
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    usuario = authenticate(request, username=username, password=password)
    if usuario is None:
        return Response({'detail': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)
    if usuario.tipo_aga == TipoUsuarioAGA.ESTUDIANTE:
        return Response(
            {'detail': 'Acceso denegado: los estudiantes no tienen acceso a PREMIAX-UHO.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    if not usuario.activo:
        return Response({'detail': 'Cuenta inactiva. Contacte al administrador.'}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(usuario)
    registrar(usuario, 'Inicio de sesión', 'auth', 'Login exitoso vía AGA_AUTH (simulado)', request)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'usuario': UsuarioSerializer(usuario).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    registrar(request.user, 'Cierre de sesión', 'auth', '', request)
    return Response({'detail': 'Sesión cerrada.'})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    if request.method == 'GET':
        return Response(UsuarioSerializer(request.user).data)
    serializer = PerfilSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def completar_perfil_view(request):
    serializer = CompletarPerfilSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    registrar(request.user, 'Completar perfil', 'usuarios', 'Selección de área/departamento en primer acceso', request)
    return Response(UsuarioSerializer(request.user).data)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related('area', 'departamento').all().order_by('-fecha_registro')
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rol', 'area', 'departamento', 'activo']
    search_fields = ['username', 'first_name', 'last_name', 'email']

    def get_serializer_class(self):
        if self.request.query_params.get('mini'):
            return UsuarioMiniSerializer
        return UsuarioSerializer

    @staticmethod
    def _es_rol_de_administracion(rol):
        return rol in (Rol.ADMIN, Rol.SUPERADMIN)

    def _verificar_puede_gestionar(self, objetivo):
        """Solo un superadmin puede modificar o eliminar cuentas de admin/superadmin (RF-008)."""
        if self._es_rol_de_administracion(objetivo.rol) and not hay_privilegio(self.request.user, Rol.SUPERADMIN):
            raise PermissionDenied('Solo el superadmin puede gestionar cuentas de admin o superadmin.')

    def perform_update(self, serializer):
        self._verificar_puede_gestionar(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise PermissionDenied('No puedes eliminar tu propia cuenta.')
        self._verificar_puede_gestionar(instance)
        instance.delete()

    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'El registro de usuarios es automático al iniciar sesión con AGA_AUTH; no se pueden crear manualmente.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=['patch'])
    def cambiar_rol(self, request, pk=None):
        usuario = self.get_object()
        serializer = CambiarRolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nuevo_rol = serializer.validated_data['rol']
        anterior = usuario.rol
        es_superadmin = hay_privilegio(request.user, Rol.SUPERADMIN)

        if usuario.pk == request.user.pk:
            return Response({'detail': 'No puedes cambiar tu propio rol.'}, status=403)
        if (self._es_rol_de_administracion(nuevo_rol) or self._es_rol_de_administracion(anterior)) and not es_superadmin:
            return Response(
                {'detail': 'Solo el superadmin puede asignar o retirar los roles Admin y Superadmin.'}, status=403,
            )
        if anterior == Rol.SUPERADMIN and nuevo_rol != Rol.SUPERADMIN and                 not Usuario.objects.filter(rol=Rol.SUPERADMIN, activo=True, is_active=True).exclude(pk=usuario.pk).exists():
            return Response({'detail': 'Debe existir al menos un superadmin activo en el sistema.'}, status=400)

        usuario.rol = nuevo_rol
        usuario.save(update_fields=['rol'])
        registrar(request.user, 'Modificar rol', 'usuarios', f'Rol de {usuario.username} cambiado de {anterior} a {nuevo_rol}', request)
        return Response(UsuarioSerializer(usuario).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_usuarios_view(request):
    """Búsqueda simple de usuarios por nombre, para asignar miembros de comisión, etc."""
    q = request.query_params.get('q', '')
    qs = Usuario.objects.filter(activo=True)
    if q:
        qs = qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q) | qs.filter(username__icontains=q)
    return Response(UsuarioMiniSerializer(qs[:20], many=True).data)
