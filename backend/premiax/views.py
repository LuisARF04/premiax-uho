from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Raíz navegable de la API. Se sirve tanto en '/' como en '/api/' para que
    abrir el backend directamente lleve al mismo punto de entrada de la API.
    """
    def url(path):
        return request.build_absolute_uri(f'/api/{path}')

    return Response({
        'auth': {
            'login': url('auth/login/'),
            'logout': url('auth/logout/'),
            'me': url('auth/me/'),
            'completar-perfil': url('auth/completar-perfil/'),
        },
        'publico': {
            'categorias': url('publico/categorias/'),
            'calendario': url('publico/calendario/'),
            'convocatoria-activa': url('publico/convocatoria-activa/'),
            'ganadores': url('publico/ganadores/'),
            'ganadores-anios': url('publico/ganadores/anios/'),
        },
        'usuarios': url('usuarios/'),
        'usuarios-buscar': url('usuarios/buscar/'),
        'usuarios-inactivos': url('usuarios-inactivos/'),
        'areas': url('areas/'),
        'departamentos': url('departamentos/'),
        'nomencladores': {
            'categorias-docentes': url('categorias-docentes/'),
            'categorias-cientificas': url('categorias-cientificas/'),
            'cargos': url('cargos/'),
            'carreras': url('carreras/'),
        },
        'categorias-premio': url('categorias-premio/'),
        'premios': url('premios/'),
        'etapas': url('etapas/'),
        'propuestas': url('propuestas/'),
        'comisiones': url('comisiones/'),
        'comisiones-mias': url('comisiones-mias/'),
        'ganadores': url('ganadores/'),
        'notificaciones': url('notificaciones/'),
        'auditoria': url('auditoria/'),
        'dashboard': {
            'principal': url('dashboard/principal/'),
            'estadisticas': url('dashboard/estadisticas/'),
        },
        'admin-django': request.build_absolute_uri('/admin/'),
    })
