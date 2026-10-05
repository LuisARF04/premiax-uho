from django.core.mail import send_mail

from .models import Notificacion


def notificar(usuario, tipo, titulo, mensaje, url_accion=''):
    """Crea una notificación interna y, si el usuario lo tiene habilitado, un correo (RF-025)."""
    Notificacion.objects.create(usuario=usuario, tipo=tipo, titulo=titulo, mensaje=mensaje, url_accion=url_accion)
    if getattr(usuario, 'notif_email', True) and usuario.email:
        try:
            send_mail(
                subject=f'[PREMIAX-UHO] {titulo}',
                message=mensaje,
                from_email='premiax-uho@uho.edu.cu',
                recipient_list=[usuario.email],
                fail_silently=True,
            )
        except Exception:
            pass


def notificar_varios(usuarios, tipo, titulo, mensaje, url_accion=''):
    for usuario in usuarios:
        notificar(usuario, tipo, titulo, mensaje, url_accion)
