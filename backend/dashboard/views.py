from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from comisiones.models import Comision
from ganadores.models import Ganador
from organizacion.models import Area
from premios.models import CategoriaPremio, EtapaProceso
from propuestas.models import EstadoPropuesta, Propuesta
from usuarios.permissions import IsGestorGlobal


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_principal_view(request):
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
@permission_classes([IsGestorGlobal])
def dashboard_estadisticas_view(request):
    anio = request.query_params.get('anio', timezone.now().year)
    propuestas_anio = Propuesta.objects.filter(anio=anio)

    por_area = list(
        propuestas_anio.exclude(area=None).values('area__nombre').annotate(total=Count('id')).order_by('-total')
    )
    por_categoria = list(
        propuestas_anio.values('premio__categoria__nombre', 'premio__categoria__tipo')
        .annotate(total=Count('id')).order_by('-total')
    )
    ganadores_por_categoria = list(
        Ganador.objects.filter(anio=anio).values('premio__categoria__nombre').annotate(total=Count('id')).order_by('-total')
    )
    areas_totales = Area.objects.filter(activo=True).count()
    areas_con_propuesta = propuestas_anio.exclude(area=None).values('area').distinct().count()

    return Response({
        'anio': int(anio),
        'total_propuestas': propuestas_anio.count(),
        'total_ganadores_propuestos': propuestas_anio.filter(estado=EstadoPropuesta.GANADORA_PROPUESTA).count(),
        'total_aprobados': Ganador.objects.filter(anio=anio).count(),
        'areas_participantes': areas_con_propuesta,
        'areas_sin_propuesta': max(areas_totales - areas_con_propuesta, 0),
        'propuestas_por_area': por_area,
        'propuestas_por_categoria': por_categoria,
        'ganadores_por_categoria': ganadores_por_categoria,
    })
