from .models import LogAuditoria

MUTATING_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
SKIP_PATHS = ('/api/auth/', '/api/auditoria/')


class AuditoriaMiddleware:
    """Registra automáticamente toda solicitud que modifique datos vía la API."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            path = request.path
            if (
                path.startswith('/api/')
                and request.method in MUTATING_METHODS
                and not any(path.startswith(p) for p in SKIP_PATHS)
                and 200 <= response.status_code < 400
            ):
                usuario = getattr(request, 'user', None)
                if usuario is not None and not usuario.is_authenticated:
                    usuario = None
                modulo = path.strip('/').split('/')[1] if len(path.strip('/').split('/')) > 1 else 'api'
                LogAuditoria.objects.create(
                    usuario=usuario,
                    accion=f'{request.method} {path}',
                    modulo=modulo,
                    detalle=f'status={response.status_code}',
                    ip=request.META.get('REMOTE_ADDR'),
                )
        except Exception:
            pass
        return response
