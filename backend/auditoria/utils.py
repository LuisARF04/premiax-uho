from .models import LogAuditoria


def registrar(usuario, accion, modulo, detalle='', request=None):
    ip = None
    if request is not None:
        ip = request.META.get('REMOTE_ADDR')
    LogAuditoria.objects.create(usuario=usuario, accion=accion, modulo=modulo, detalle=detalle, ip=ip)
