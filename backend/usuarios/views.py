from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from auditoria.utils import registrar
from .models import Rol, TipoUsuarioAGA, Usuario
from .permissions import IsAdmin, IsSuperadmin, hay_privilegio
from .serializers import (
    CambiarRolSerializer, CompletarPerfilSerializer, UsuarioMiniSerializer, UsuarioSerializer,
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
    serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
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

    @action(detail=True, methods=['patch'])
    def cambiar_rol(self, request, pk=None):
        usuario = self.get_object()
        serializer = CambiarRolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nuevo_rol = serializer.validated_data['rol']
        if nuevo_rol in (Rol.ADMIN, Rol.SUPERADMIN) and not hay_privilegio(request.user, Rol.SUPERADMIN):
            return Response({'detail': 'Solo el superadmin puede asignar el rol Admin/Superadmin.'}, status=403)
        anterior = usuario.rol
        usuario.rol = nuevo_rol
        usuario.save(update_fields=['rol'])
        registrar(request.user, 'Modificar rol', 'usuarios', f'Rol de {usuario.username} cambiado de {anterior} a {nuevo_rol}', request)
        return Response(UsuarioSerializer(usuario).data)

    def perform_create(self, serializer):
        raise Exception('El registro de usuarios es automático vía AGA_AUTH; use /api/dev/crear-usuario/ solo para datos de demo.')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_usuarios_view(request):
    """Búsqueda simple de usuarios por nombre, para asignar miembros de comisión, etc."""
    q = request.query_params.get('q', '')
    qs = Usuario.objects.filter(activo=True)
    if q:
        qs = qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q) | qs.filter(username__icontains=q)
    return Response(UsuarioMiniSerializer(qs[:20], many=True).data)
