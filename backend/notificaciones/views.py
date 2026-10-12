from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from comisiones.models import AsignacionRevision
from premios.models import EtapaProceso
from propuestas.models import EstadoPropuesta, NivelPropuesta, Propuesta
from usuarios.models import Rol, Usuario
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


def _propuestas_sin_revisar(usuario, anio):
    """Propuestas que hoy esperan una acción de revisión de este usuario (RF-026)."""
    total = AsignacionRevision.objects.filter(miembro=usuario, revisada=False, propuesta__anio=anio).count()
    propuestas = Propuesta.objects.filter(anio=anio)
    if usuario.rol == Rol.JEFE_DEPARTAMENTO and usuario.departamento_id:
        total += propuestas.filter(
            departamento_id=usuario.departamento_id, nivel_actual=NivelPropuesta.DEPARTAMENTO,
            estado=EstadoPropuesta.PENDIENTE_DEPARTAMENTO,
        ).count()
    elif usuario.rol == Rol.JEFE_AREA and usuario.area_id:
        total += propuestas.filter(
            area_id=usuario.area_id, nivel_actual=NivelPropuesta.AREA, estado=EstadoPropuesta.PENDIENTE_AREA,
        ).count()
    elif usuario.rol == Rol.JEFE_COMISION:
        total += propuestas.filter(
            comision__in=usuario.comisiones_dirigidas.all(), estado=EstadoPropuesta.EN_COMISION,
        ).count()
    return total


@api_view(['GET'])
@permission_classes([IsGestorGlobal])
def usuarios_inactivos_view(request):
    """
    RF-026: usuarios/roles que no han entrado al sistema en el período (`dias`, 7 por defecto)
    o que tienen propuestas pendientes de revisión en el año en curso.
    """
    try:
        dias = max(1, int(request.query_params.get('dias', 7)))
    except ValueError:
        dias = 7
    ahora = timezone.now()
    limite = ahora - timedelta(days=dias)
    hoy = ahora.date()
    anio = hoy.year
    etapa = EtapaProceso.objects.filter(fecha_inicio__lte=hoy, fecha_cierre__gte=hoy).order_by('orden').first()

    por_rol = {}
    usuarios = []
    for u in Usuario.objects.filter(activo=True, is_active=True).select_related('area', 'departamento'):
        sin_ingreso = u.last_login is None or u.last_login < limite
        pendientes = _propuestas_sin_revisar(u, anio)
        resumen = por_rol.setdefault(u.rol, {
            'rol': u.rol, 'rol_nombre': u.get_rol_display(), 'total': 0, 'sin_ingreso': 0, 'propuestas_sin_revisar': 0,
        })
        resumen['total'] += 1
        resumen['sin_ingreso'] += int(sin_ingreso)
        resumen['propuestas_sin_revisar'] += pendientes

        if u.rol == Rol.USUARIO or not (sin_ingreso or pendientes):
            continue
        motivos = []
        if sin_ingreso:
            motivos.append('sin_ingreso')
        if pendientes:
            motivos.append('propuestas_sin_revisar')
        usuarios.append({
            'id': u.id, 'nombre': u.get_full_name() or u.username, 'rol': u.get_rol_display(),
            'area': u.area.nombre if u.area else None,
            'dias_inactivo': (ahora - u.last_login).days if u.last_login else None,
            'pendientes': pendientes, 'motivos': motivos,
        })

    orden = {r: i for i, r in enumerate(Rol.values)}
    return Response({
        'periodo': {'dias': dias, 'etapa_activa': etapa.nombre if etapa else None, 'anio': anio},
        'por_rol': sorted(por_rol.values(), key=lambda r: orden.get(r['rol'], 99)),
        'usuarios': sorted(usuarios, key=lambda r: (-r['pendientes'], r['nombre'])),
    })
