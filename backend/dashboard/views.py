from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from comisiones.models import Comision
from ganadores.models import Ganador
from notificaciones.utils import procesar_etapas
from organizacion.models import Area
from premios.models import CategoriaPremio, EtapaProceso
from propuestas.models import EstadoPropuesta, Propuesta
from usuarios.models import Rol, Usuario
from usuarios.permissions import IsJefeComision


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_principal_view(request):
    # Sin Celery: aprovechamos la consulta del dashboard para emitir los avisos de etapa pendientes (RF-025).
    procesar_etapas()

    hoy = timezone.now().date()
    etapa_activa = EtapaProceso.objects.filter(fecha_inicio__lte=hoy, fecha_cierre__gte=hoy).order_by('orden').first()
    dias_restantes = (etapa_activa.fecha_cierre - hoy).days if etapa_activa else None

    total_propuestas = Propuesta.objects.count()
    evaluadas = Propuesta.objects.exclude(estado__in=[EstadoPropuesta.PENDIENTE_DEPARTAMENTO, EstadoPropuesta.PENDIENTE_AREA]).count()
    comisiones_activas = Comision.objects.filter(activo=True).count()

    comisiones_progreso = []
    for c in Comision.objects.filter(activo=True).annotate(total=Count('propuestas_asignadas')):
        revisadas = c.propuestas_asignadas.exclude(estado=EstadoPropuesta.EN_COMISION).count()
        comisiones_progreso.append({
            'id': c.id, 'nombre': c.nombre, 'total': c.total, 'revisadas': revisadas,
            'porcentaje': round(revisadas / c.total * 100) if c.total else 0,
        })

    ultimas = Propuesta.objects.select_related('premio', 'area').order_by('-fecha_creacion')[:6]
    ultimas_data = [{
        'id': p.id, 'candidato_nombre': p.candidato_nombre,
        'area_nombre': p.area.nombre if p.area else None,
        'premio_nombre': p.premio.nombre, 'estado': p.estado,
    } for p in ultimas]

    proximas_etapas = EtapaProceso.objects.filter(fecha_cierre__gte=hoy).order_by('fecha_cierre')[:6]
    proximas_data = [{
        'id': e.id, 'nombre': e.nombre, 'fecha_cierre': e.fecha_cierre, 'responsable': e.responsable_desc, 'estado': e.estado,
    } for e in proximas_etapas]

    return Response({
        'etapa_activa': etapa_activa.nombre if etapa_activa else None,
        'dias_restantes': dias_restantes,
        'kpis': {
            'propuestas_recibidas': total_propuestas,
            'comisiones_activas': comisiones_activas,
            'propuestas_evaluadas': evaluadas,
            'dias_restantes': dias_restantes,
        },
        'ultimas_propuestas': ultimas_data,
        'comisiones_progreso': comisiones_progreso,
        'proximas_etapas': proximas_data,
    })


@api_view(['GET'])
@permission_classes([IsJefeComision])
def dashboard_estadisticas_view(request):
    """RF-027: métricas para admin, gestor global y jefe de comisión."""
    try:
        anio = int(request.query_params.get('anio', timezone.now().year))
    except ValueError:
        anio = timezone.now().year
    propuestas_anio = Propuesta.objects.filter(anio=anio)

    por_area = list(
        propuestas_anio.exclude(area=None).values('area__nombre').annotate(total=Count('id')).order_by('-total')
    )
    por_categoria = list(
        propuestas_anio.values('premio__categoria__nombre', 'premio__categoria__tipo')
        .annotate(total=Count('id')).order_by('-total')
    )
    por_premio = list(
        propuestas_anio.values('premio__nombre', 'premio__categoria__nombre')
        .annotate(total=Count('id')).order_by('-total')
    )
    por_departamento = list(
        propuestas_anio.exclude(departamento=None)
        .values('departamento__nombre', 'departamento__area__nombre')
        .annotate(total=Count('id')).order_by('-total')[:10]
    )
    ganadores_por_categoria = list(
        Ganador.objects.filter(anio=anio).values('premio__categoria__nombre').annotate(total=Count('id')).order_by('-total')
    )
    ganadores_por_anio = list(
        Ganador.objects.values('anio', 'premio__categoria__nombre').annotate(total=Count('id')).order_by('anio', 'premio__categoria__nombre')
    )

    # Estado del proceso por área: ¿enviaron propuestas o no?
    areas_con = {r['area_id'] for r in propuestas_anio.exclude(area=None).values('area_id').distinct()}
    areas_activas = list(Area.objects.filter(activo=True).values('id', 'nombre'))
    estado_por_area = sorted(
        ({'area': a['nombre'], 'envio': a['id'] in areas_con,
          'propuestas': next((r['total'] for r in por_area if r['area__nombre'] == a['nombre']), 0)} for a in areas_activas),
        key=lambda a: (a['envio'], a['area']),
    )
    areas_totales = len(areas_activas)
    areas_con_propuesta = sum(1 for a in estado_por_area if a['envio'])

    # Participación de usuarios y roles.
    hace_7_dias = timezone.now() - timedelta(days=7)
    proponentes = set(propuestas_anio.values_list('creado_por_id', flat=True))
    participacion = []
    for rol, nombre in Rol.choices:
        usuarios = Usuario.objects.filter(activo=True, is_active=True, rol=rol)
        total = usuarios.count()
        if not total:
            continue
        participacion.append({
            'rol': nombre, 'total': total,
            'con_propuestas': usuarios.filter(id__in=proponentes).count(),
            'activos_7_dias': usuarios.filter(last_login__gte=hace_7_dias).count(),
        })

    return Response({
        'anio': anio,
        'total_propuestas': propuestas_anio.count(),
        'total_ganadores_propuestos': propuestas_anio.filter(estado=EstadoPropuesta.GANADORA_PROPUESTA).count(),
        'total_aprobados': Ganador.objects.filter(anio=anio).count(),
        'areas_participantes': areas_con_propuesta,
        'areas_sin_propuesta': max(areas_totales - areas_con_propuesta, 0),
        'propuestas_por_area': por_area,
        'propuestas_por_categoria': por_categoria,
        'propuestas_por_premio': por_premio,
        'propuestas_por_departamento': por_departamento,
        'estado_por_area': estado_por_area,
        'participacion_roles': participacion,
        'ganadores_por_categoria': ganadores_por_categoria,
        'ganadores_por_anio': ganadores_por_anio,
        'actualizado': timezone.now().isoformat(),
    })
