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


# --- Avisos automáticos de etapas (RF-025) -------------------------------------------------------

DIAS_ALERTA_FECHA_LIMITE = 3
_INTERVALO_MIN_SEGUNDOS = 600
_ultima_verificacion = 0.0


def _destinatarios_etapa(etapa, solo_fechas_limite=False):
    """La convocatoria avisa a todos los usuarios; el resto de etapas, a quienes tienen algún rol de gestión."""
    from usuarios.models import Usuario
    qs = Usuario.objects.filter(activo=True, is_active=True)
    if not etapa.es_convocatoria:
        qs = qs.exclude(rol='usuario')
    if solo_fechas_limite:
        qs = qs.filter(notif_fechas_limite=True)
    return qs


def procesar_etapas(forzar=False):
    """
    Envía (una sola vez por etapa) el aviso de inicio de etapa y la alerta preventiva de fecha límite.
    Es idempotente: puede ejecutarse desde un cron (`manage.py notificar_etapas`) o al consultar el dashboard.
    Devuelve la cantidad de avisos generados.
    """
    import time
    from django.utils import timezone
    from premios.models import EtapaProceso
    from .models import EventoEtapa

    global _ultima_verificacion
    ahora = time.monotonic()
    if not forzar and ahora - _ultima_verificacion < _INTERVALO_MIN_SEGUNDOS:
        return 0
    _ultima_verificacion = ahora

    hoy = timezone.now().date()
    enviados = 0
    for etapa in EtapaProceso.objects.filter(fecha_inicio__lte=hoy, fecha_cierre__gte=hoy):
        _, nuevo = EventoEtapa.objects.get_or_create(etapa=etapa, tipo='inicio')
        # Si la etapa ya llevaba varios días en curso cuando se activó el sistema, se registra sin avisar.
        if nuevo and (hoy - etapa.fecha_inicio).days <= 3:
            notificar_varios(
                _destinatarios_etapa(etapa), 'etapas', f'Inició la etapa: {etapa.nombre}',
                f'La etapa "{etapa.nombre}" está en curso hasta el {etapa.fecha_cierre:%d/%m/%Y}.',
            )
            enviados += 1

        dias_restantes = (etapa.fecha_cierre - hoy).days
        if dias_restantes <= DIAS_ALERTA_FECHA_LIMITE:
            _, nuevo = EventoEtapa.objects.get_or_create(etapa=etapa, tipo='alerta')
            if nuevo:
                cuando = 'hoy' if dias_restantes == 0 else f'en {dias_restantes} día(s)'
                notificar_varios(
                    _destinatarios_etapa(etapa, solo_fechas_limite=True), 'etapas',
                    f'Se acerca la fecha límite: {etapa.nombre}',
                    f'La etapa "{etapa.nombre}" cierra {cuando} ({etapa.fecha_cierre:%d/%m/%Y}).',
                )
                enviados += 1
    return enviados
