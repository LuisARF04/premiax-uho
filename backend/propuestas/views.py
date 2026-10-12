from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auditoria.utils import registrar
from comisiones.models import AsignacionRevision, Comision, MiembroComision
from comisiones.serializers import AsignacionRevisionSerializer
from ganadores.models import Ganador
from notificaciones.utils import notificar
from usuarios.models import Rol, Usuario
from usuarios.permissions import hay_privilegio
from .models import EstadoPropuesta, HistorialPropuesta, NivelPropuesta, Propuesta, VersionPropuesta
from .serializers import (
    PropuestaCreateSerializer, PropuestaDetalleSerializer, PropuestaListSerializer, PropuestaUpdateSerializer,
)


def _historial(propuesta, usuario, accion, descripcion='', nivel_desde='', nivel_hasta=''):
    HistorialPropuesta.objects.create(
        propuesta=propuesta, usuario=usuario, accion=accion, descripcion=descripcion,
        nivel_desde=nivel_desde, nivel_hasta=nivel_hasta,
    )


def _snapshot(propuesta, usuario):
    """Guarda la versión actual de la propuesta (contenido + documento) en su historial de versiones."""
    VersionPropuesta.objects.create(
        propuesta=propuesta, version=propuesta.version, usuario=usuario,
        candidato_nombre=propuesta.candidato_nombre, resumen=propuesta.resumen,
        documento=propuesta.documento.name if propuesta.documento else None,
    )


def _puede_editar(usuario, propuesta):
    """RF-019/020: quién puede modificar o enriquecer una propuesta según su nivel actual."""
    if propuesta.estado in (EstadoPropuesta.APROBADA, EstadoPropuesta.RECHAZADA):
        return False
    if hay_privilegio(usuario, Rol.GESTOR_GLOBAL):
        return True
    if propuesta.nivel_actual == NivelPropuesta.DEPARTAMENTO:
        if propuesta.creado_por_id == usuario.id:
            return True
        return usuario.rol == Rol.JEFE_DEPARTAMENTO and propuesta.departamento_id == usuario.departamento_id
    if propuesta.nivel_actual == NivelPropuesta.AREA:
        return usuario.rol == Rol.JEFE_AREA and propuesta.area_id == usuario.area_id
    return False


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
        if self.action in ('update', 'partial_update'):
            return PropuestaUpdateSerializer
        return PropuestaDetalleSerializer

    def get_queryset(self):
        usuario = self.request.user
        qs = Propuesta.objects.select_related(
            'premio', 'premio__categoria', 'area', 'departamento', 'comision', 'creado_por'
        ).prefetch_related('historial')

        if hay_privilegio(usuario, Rol.GESTOR_GLOBAL):
            return qs  # admin, superadmin, gestor_global ven todo

        # Cada usuario ve lo suyo, lo que le asignaron a revisar y lo de su nivel jerárquico (RF-016).
        filtro = Q(creado_por=usuario) | Q(revisiones__miembro=usuario)
        if usuario.rol == Rol.JEFE_COMISION:
            filtro |= Q(comision__in=usuario.comisiones_dirigidas.all())
        elif usuario.rol == Rol.JEFE_AREA and usuario.area_id:
            filtro |= Q(area=usuario.area_id)
        elif usuario.rol == Rol.JEFE_DEPARTAMENTO and usuario.departamento_id:
            filtro |= Q(departamento=usuario.departamento_id)
        return qs.filter(filtro).distinct()

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
        _snapshot(instance, usuario)
        registrar(usuario, 'Crear propuesta', 'propuestas', f'{instance.candidato_nombre} - {premio.nombre}', self.request)

    def update(self, request, *args, **kwargs):
        """RF-019/020: modificar/enriquecer; cada cambio de contenido o documento genera una nueva versión."""
        propuesta = self.get_object()
        if not _puede_editar(request.user, propuesta):
            return Response({'detail': 'No puedes modificar esta propuesta en su estado o nivel actual.'}, status=403)
        serializer = PropuestaUpdateSerializer(propuesta, data=request.data, partial=True, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        antes = (propuesta.candidato_nombre, propuesta.candidato_usuario_id, propuesta.resumen,
                 propuesta.documento.name if propuesta.documento else '')
        instance = serializer.save()
        despues = (instance.candidato_nombre, instance.candidato_usuario_id, instance.resumen,
                   instance.documento.name if instance.documento else '')
        if antes != despues:
            instance.version += 1
            instance.save(update_fields=['version'])
            _snapshot(instance, request.user)
            cambios = []
            if antes[:2] != despues[:2]:
                cambios.append('candidato')
            if antes[2] != despues[2]:
                cambios.append('descripción')
            if antes[3] != despues[3]:
                cambios.append('documento')
            _historial(instance, request.user, 'Modificación', f'Versión {instance.version}: se actualizó {", ".join(cambios)}.')
            registrar(request.user, 'Editar propuesta', 'propuestas', f'{instance.id} v{instance.version}', request)
        return Response(PropuestaDetalleSerializer(instance, context=self.get_serializer_context()).data)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar propuesta', 'propuestas', str(instance.id), self.request)
        instance.delete()

    def _es_jefe_de_su_comision(self, usuario, propuesta):
        return bool(propuesta.comision_id and (propuesta.comision.jefe_id == usuario.id or hay_privilegio(usuario, Rol.GESTOR_GLOBAL)))

    @action(detail=True, methods=['post'])
    def asignar_revision(self, request, pk=None):
        """RF-016: el jefe de comisión asigna la propuesta a un miembro para su revisión."""
        propuesta = self.get_object()
        if not self._es_jefe_de_su_comision(request.user, propuesta):
            return Response({'detail': 'Solo el jefe de la comisión asignada puede asignar revisiones.'}, status=403)
        if propuesta.estado != EstadoPropuesta.EN_COMISION:
            return Response({'detail': 'Solo se pueden asignar revisiones a propuestas en revisión de comisión.'}, status=400)
        miembro_id = request.data.get('miembro')
        if not MiembroComision.objects.filter(comision=propuesta.comision, usuario_id=miembro_id).exists():
            return Response({'detail': 'El usuario no es miembro de esta comisión.'}, status=400)
        revision, creada = AsignacionRevision.objects.get_or_create(
            propuesta=propuesta, miembro_id=miembro_id, defaults={'asignado_por': request.user},
        )
        if not creada:
            return Response({'detail': 'Esa propuesta ya está asignada a este miembro.'}, status=400)
        _historial(propuesta, request.user, 'Asignar revisión', f'Asignada a {revision.miembro.get_full_name()} para su revisión.')
        notificar(revision.miembro, 'comisiones', 'Se te asignó una propuesta para revisar',
                  f'Revisa la propuesta de {propuesta.candidato_nombre} para "{propuesta.premio.nombre}".',
                  url_accion=f'/app/propuestas/{propuesta.id}')
        registrar(request.user, 'Asignar revisión', 'comisiones', f'propuesta {propuesta.id} -> {revision.miembro}', request)
        return Response(AsignacionRevisionSerializer(revision).data, status=201)

    @action(detail=True, methods=['post'])
    def quitar_revision(self, request, pk=None):
        propuesta = self.get_object()
        if not self._es_jefe_de_su_comision(request.user, propuesta):
            return Response({'detail': 'No autorizado.'}, status=403)
        revision = AsignacionRevision.objects.filter(propuesta=propuesta, pk=request.data.get('revision')).first()
        if not revision:
            return Response({'detail': 'Revisión no encontrada.'}, status=404)
        _historial(propuesta, request.user, 'Quitar revisión', f'Se retiró la asignación de {revision.miembro.get_full_name()}.')
        registrar(request.user, 'Quitar revisión', 'comisiones', f'propuesta {propuesta.id} -> {revision.miembro}', request)
        revision.delete()
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def registrar_revision(self, request, pk=None):
        """RF-016: el miembro asignado deja su criterio y puntuación."""
        propuesta = self.get_object()
        revision = AsignacionRevision.objects.filter(propuesta=propuesta, miembro=request.user).first()
        if not revision:
            return Response({'detail': 'Esta propuesta no te fue asignada para revisión.'}, status=403)
        criterio = (request.data.get('criterio') or '').strip()
        if not criterio:
            return Response({'detail': 'Debe escribir su criterio sobre la propuesta.'}, status=400)
        puntuacion = request.data.get('puntuacion')
        if puntuacion in (None, ''):
            puntuacion = None
        else:
            try:
                puntuacion = int(puntuacion)
            except (TypeError, ValueError):
                return Response({'detail': 'La puntuación debe ser un número entre 1 y 10.'}, status=400)
            if not 1 <= puntuacion <= 10:
                return Response({'detail': 'La puntuación debe estar entre 1 y 10.'}, status=400)
        revision.criterio = criterio
        revision.puntuacion = puntuacion
        revision.revisada = True
        revision.fecha_revision = timezone.now()
        revision.save()
        _historial(propuesta, request.user, 'Revisión de comisión', 'Un miembro registró su criterio.')
        comision = propuesta.comision
        if comision and comision.jefe:
            notificar(comision.jefe, 'comisiones', 'Revisión completada',
                      f'{request.user.get_full_name()} revisó la propuesta de {propuesta.candidato_nombre}.',
                      url_accion=f'/app/propuestas/{propuesta.id}')
        registrar(request.user, 'Registrar revisión', 'comisiones', f'propuesta {propuesta.id}', request)
        return Response(AsignacionRevisionSerializer(revision).data)

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
