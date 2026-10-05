from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auditoria.utils import registrar
from comisiones.models import Comision
from ganadores.models import Ganador
from notificaciones.utils import notificar
from usuarios.models import Rol, Usuario
from usuarios.permissions import hay_privilegio
from .models import EstadoPropuesta, HistorialPropuesta, NivelPropuesta, Propuesta
from .serializers import PropuestaCreateSerializer, PropuestaDetalleSerializer, PropuestaListSerializer


def _historial(propuesta, usuario, accion, descripcion='', nivel_desde='', nivel_hasta=''):
    HistorialPropuesta.objects.create(
        propuesta=propuesta, usuario=usuario, accion=accion, descripcion=descripcion,
        nivel_desde=nivel_desde, nivel_hasta=nivel_hasta,
    )


class PropuestaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'nivel_actual', 'premio', 'area', 'departamento', 'comision', 'anio']
    search_fields = ['candidato_nombre', 'resumen']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action == 'create':
            return PropuestaCreateSerializer
        if self.action in ('list',):
            return PropuestaListSerializer
        return PropuestaDetalleSerializer

    def get_queryset(self):
        usuario = self.request.user
        qs = Propuesta.objects.select_related(
            'premio', 'premio__categoria', 'area', 'departamento', 'comision', 'creado_por'
        ).prefetch_related('historial')

        if hay_privilegio(usuario, Rol.GESTOR_GLOBAL):
            return qs  # admin, superadmin, gestor_global ven todo

        if usuario.rol in (Rol.JEFE_COMISION, Rol.MIEMBRO_COMISION):
            comisiones_ids = list(usuario.comisiones_dirigidas.values_list('id', flat=True)) + \
                list(usuario.comisiones_miembro.values_list('comision_id', flat=True))
            return qs.filter(comision_id__in=comisiones_ids) | qs.filter(creado_por=usuario)

        if usuario.rol == Rol.JEFE_AREA:
            return qs.filter(area=usuario.area) | qs.filter(creado_por=usuario)

        if usuario.rol == Rol.JEFE_DEPARTAMENTO:
            return qs.filter(departamento=usuario.departamento) | qs.filter(creado_por=usuario)

        return qs.filter(creado_por=usuario)

    def perform_create(self, serializer):
        usuario = self.request.user
        premio = serializer.validated_data['premio']

        if premio.es_por_comision:
            comision = usuario.comisiones_dirigidas.filter(premios=premio).first()
            instance = serializer.save(
                creado_por=usuario,
                area=usuario.area,
                departamento=usuario.departamento,
                estado=EstadoPropuesta.EN_COMISION,
                nivel_actual=NivelPropuesta.COMISION,
                comision=comision,
            )
            _historial(instance, usuario, 'Creación directa por comisión', 'Premio asignado por comisión (sin propuesta de área).', '', NivelPropuesta.COMISION)
        else:
            instance = serializer.save(
                creado_por=usuario,
                area=usuario.area,
                departamento=usuario.departamento,
                estado=EstadoPropuesta.PENDIENTE_DEPARTAMENTO,
                nivel_actual=NivelPropuesta.DEPARTAMENTO,
            )
            _historial(instance, usuario, 'Creación de propuesta', f'Propuesta creada para {instance.candidato_nombre}.', '', NivelPropuesta.DEPARTAMENTO)
            if instance.departamento and instance.departamento.responsable:
                notificar(
                    instance.departamento.responsable, 'propuestas', 'Nueva propuesta recibida',
                    f'{usuario.get_full_name()} propuso a {instance.candidato_nombre} para "{premio.nombre}".',
                )
        registrar(usuario, 'Crear propuesta', 'propuestas', f'{instance.candidato_nombre} - {premio.nombre}', self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        _historial(instance, self.request.user, 'Modificación', 'La propuesta fue editada/enriquecida.')
        registrar(self.request.user, 'Editar propuesta', 'propuestas', str(instance.id), self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar propuesta', 'propuestas', str(instance.id), self.request)
        instance.delete()

    @action(detail=True, methods=['post'])
    def elevar(self, request, pk=None):
        propuesta = self.get_object()
        usuario = request.user

        if propuesta.nivel_actual == NivelPropuesta.DEPARTAMENTO:
            if not (usuario.rol == Rol.JEFE_DEPARTAMENTO or hay_privilegio(usuario, Rol.GESTOR_GLOBAL)):
                return Response({'detail': 'Solo el jefe de departamento puede elevar esta propuesta.'}, status=403)
            propuesta.nivel_actual = NivelPropuesta.AREA
            propuesta.estado = EstadoPropuesta.PENDIENTE_AREA
            propuesta.save(update_fields=['nivel_actual', 'estado'])
            _historial(propuesta, usuario, 'Elevar a Área', '', NivelPropuesta.DEPARTAMENTO, NivelPropuesta.AREA)
            if propuesta.area and propuesta.area.responsable:
                notificar(propuesta.area.responsable, 'propuestas', 'Propuesta elevada a tu área',
                          f'La propuesta de {propuesta.candidato_nombre} fue elevada para tu revisión.')

        elif propuesta.nivel_actual == NivelPropuesta.AREA:
            if not (usuario.rol == Rol.JEFE_AREA or hay_privilegio(usuario, Rol.GESTOR_GLOBAL)):
                return Response({'detail': 'Solo el jefe de área puede elevar esta propuesta.'}, status=403)
            comision = propuesta.premio.comisiones.first()
            propuesta.nivel_actual = NivelPropuesta.COMISION
            propuesta.estado = EstadoPropuesta.EN_COMISION
            propuesta.comision = comision
            propuesta.save(update_fields=['nivel_actual', 'estado', 'comision'])
            _historial(propuesta, usuario, 'Elevar a nivel Universidad / Comisión', '', NivelPropuesta.AREA, NivelPropuesta.COMISION)
            if comision and comision.jefe:
                notificar(comision.jefe, 'propuestas', 'Nueva propuesta asignada a tu comisión',
                          f'La propuesta de {propuesta.candidato_nombre} para "{propuesta.premio.nombre}" fue asignada a tu comisión.')
            gestores = Usuario.objects.filter(rol=Rol.GESTOR_GLOBAL)
            for g in gestores:
                notificar(g, 'propuestas', 'Propuesta elevada a nivel universidad',
                          f'{propuesta.candidato_nombre} - {propuesta.premio.nombre} está lista para asignación de comisión.')
        else:
            return Response({'detail': 'La propuesta no puede elevarse desde su nivel actual.'}, status=400)

        registrar(usuario, 'Elevar propuesta', 'propuestas', str(propuesta.id), request)
        return Response(PropuestaDetalleSerializer(propuesta).data)

    @action(detail=True, methods=['post'])
    def reasignar(self, request, pk=None):
        propuesta = self.get_object()
        if not hay_privilegio(request.user, Rol.GESTOR_GLOBAL):
            return Response({'detail': 'Solo el gestor global puede reasignar comisiones.'}, status=403)
        comision = Comision.objects.filter(pk=request.data.get('comision')).first()
        if not comision:
            return Response({'detail': 'Comisión no encontrada.'}, status=404)
        anterior = propuesta.comision
        propuesta.comision = comision
        propuesta.estado = EstadoPropuesta.EN_COMISION
        propuesta.nivel_actual = NivelPropuesta.COMISION
        propuesta.save(update_fields=['comision', 'estado', 'nivel_actual'])
        _historial(propuesta, request.user, 'Reasignar comisión', f'De "{anterior}" a "{comision}"')
        if comision.jefe:
            notificar(comision.jefe, 'comisiones', 'Propuesta reasignada a tu comisión',
                      f'La propuesta de {propuesta.candidato_nombre} fue reasignada a "{comision.nombre}".')
        registrar(request.user, 'Reasignar propuesta', 'propuestas', str(propuesta.id), request)
        return Response(PropuestaDetalleSerializer(propuesta).data)

    @action(detail=True, methods=['post'])
    def proponer_ganador(self, request, pk=None):
        propuesta = self.get_object()
        usuario = request.user
        if not (propuesta.comision_id and propuesta.comision.jefe_id == usuario.id):
            return Response({'detail': 'Solo el jefe de la comisión asignada puede proponer ganadores.'}, status=403)
        seleccion = request.data.get('seleccion_comision')
        if seleccion not in ('premio', 'reconocimiento'):
            return Response({'detail': 'Debe indicar seleccion_comision: premio o reconocimiento.'}, status=400)
        propuesta.seleccion_comision = seleccion
        propuesta.fundamentacion_comision = request.data.get('fundamentacion_comision', propuesta.fundamentacion_comision)
        propuesta.estado = EstadoPropuesta.GANADORA_PROPUESTA
        propuesta.save(update_fields=['seleccion_comision', 'fundamentacion_comision', 'estado'])
        _historial(propuesta, usuario, 'Propuesta de ganador por comisión', f'Seleccionado como {seleccion}.')
        registrar(usuario, 'Proponer ganador', 'propuestas', str(propuesta.id), request)
        return Response(PropuestaDetalleSerializer(propuesta).data)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        propuesta = self.get_object()
        usuario = request.user
        if not hay_privilegio(usuario, Rol.GESTOR_GLOBAL):
            return Response({'detail': 'No autorizado para aprobar.'}, status=403)
        if propuesta.estado != EstadoPropuesta.GANADORA_PROPUESTA:
            return Response({'detail': 'La propuesta no está en estado de ganadora propuesta.'}, status=400)

        candidato = propuesta.candidato_usuario
        ganador = Ganador.objects.create(
            propuesta=propuesta,
            premio=propuesta.premio,
            persona_nombre=propuesta.candidato_nombre,
            persona_area=propuesta.area.nombre if propuesta.area else '',
            categoria_docente=candidato.categoria_docente.nombre if candidato and candidato.categoria_docente else '',
            categoria_cientifica=candidato.categoria_cientifica.nombre if candidato and candidato.categoria_cientifica else '',
            fundamentacion=propuesta.fundamentacion_comision or propuesta.resumen,
            tipo=propuesta.seleccion_comision or 'premio',
            anio=propuesta.anio,
            aprobado_por=usuario,
            fecha_aprobacion=timezone.now(),
            publicado=True,
        )
        propuesta.estado = EstadoPropuesta.APROBADA
        propuesta.save(update_fields=['estado'])
        _historial(propuesta, usuario, 'Aprobación final', 'Ganador aprobado y publicado en el landing page.')
        if propuesta.creado_por:
            notificar(propuesta.creado_por, 'propuestas', 'Tu propuesta fue aprobada',
                      f'La propuesta para {propuesta.candidato_nombre} ({propuesta.premio.nombre}) fue aprobada definitivamente.')
        registrar(usuario, 'Aprobar ganador', 'propuestas', f'{propuesta.candidato_nombre} - {propuesta.premio.nombre}', request)
        return Response(PropuestaDetalleSerializer(propuesta).data)

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        propuesta = self.get_object()
        usuario = request.user
        if not hay_privilegio(usuario, Rol.GESTOR_GLOBAL):
            return Response({'detail': 'No autorizado para rechazar.'}, status=403)
        motivo = request.data.get('motivo', '')
        propuesta.estado = EstadoPropuesta.RECHAZADA
        propuesta.save(update_fields=['estado'])
        _historial(propuesta, usuario, 'Rechazo', motivo)
        if propuesta.creado_por:
            notificar(propuesta.creado_por, 'propuestas', 'Tu propuesta fue rechazada',
                      f'La propuesta para {propuesta.candidato_nombre} ({propuesta.premio.nombre}) fue rechazada. {motivo}')
        registrar(usuario, 'Rechazar propuesta', 'propuestas', str(propuesta.id), request)
        return Response(PropuestaDetalleSerializer(propuesta).data)
