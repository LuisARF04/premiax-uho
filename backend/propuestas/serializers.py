from rest_framework import serializers

from comisiones.serializers import AsignacionRevisionSerializer
from premios.models import convocatoria_activa
from premios.serializers import PremioSerializer
from premiax.exceptions import ReglaDeNegocio
from premiax.validators import validar_documento
from usuarios.models import Rol
from usuarios.permissions import hay_privilegio
from usuarios.serializers import UsuarioMiniSerializer
from .models import HistorialPropuesta, Propuesta, VersionPropuesta


class HistorialPropuestaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    usuario_rol = serializers.CharField(source='usuario.get_rol_display', read_only=True, default=None)

    class Meta:
        model = HistorialPropuesta
        fields = ['id', 'usuario', 'usuario_nombre', 'usuario_rol', 'accion', 'descripcion', 'nivel_desde', 'nivel_hasta', 'fecha']

    def get_usuario_nombre(self, obj):
        return obj.usuario.get_full_name() if obj.usuario else 'Sistema'


class VersionPropuestaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = VersionPropuesta
        fields = ['id', 'version', 'usuario', 'usuario_nombre', 'candidato_nombre', 'resumen', 'documento', 'fecha']

    def get_usuario_nombre(self, obj):
        return obj.usuario.get_full_name() if obj.usuario else 'Sistema'


class PropuestaListSerializer(serializers.ModelSerializer):
    premio_nombre = serializers.CharField(source='premio.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='premio.categoria.nombre', read_only=True)
    area_nombre = serializers.CharField(source='area.nombre', read_only=True, default=None)
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True, default=None)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    comision_nombre = serializers.CharField(source='comision.nombre', read_only=True, default=None)

    class Meta:
        model = Propuesta
        fields = [
            'id', 'premio', 'premio_nombre', 'categoria_nombre', 'area', 'area_nombre',
            'departamento', 'departamento_nombre', 'candidato_nombre', 'estado', 'nivel_actual',
            'comision', 'comision_nombre', 'creado_por', 'creado_por_nombre', 'anio', 'version',
            'fecha_creacion', 'fecha_actualizacion', 'seleccion_comision', 'retroactiva',
        ]


class PropuestaDetalleSerializer(serializers.ModelSerializer):
    premio_detalle = PremioSerializer(source='premio', read_only=True)
    creado_por_detalle = UsuarioMiniSerializer(source='creado_por', read_only=True)
    candidato_usuario_detalle = UsuarioMiniSerializer(source='candidato_usuario', read_only=True)
    area_nombre = serializers.CharField(source='area.nombre', read_only=True, default=None)
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True, default=None)
    comision_nombre = serializers.CharField(source='comision.nombre', read_only=True, default=None)
    historial = HistorialPropuestaSerializer(many=True, read_only=True)
    versiones = VersionPropuestaSerializer(many=True, read_only=True)
    revisiones = serializers.SerializerMethodField()

    class Meta:
        model = Propuesta
        fields = [
            'id', 'premio', 'premio_detalle', 'creado_por', 'creado_por_detalle', 'area', 'area_nombre',
            'departamento', 'departamento_nombre', 'candidato_nombre', 'candidato_usuario', 'candidato_usuario_detalle',
            'resumen', 'documento', 'estado', 'nivel_actual', 'comision', 'comision_nombre',
            'seleccion_comision', 'fundamentacion_comision', 'anio', 'version', 'fecha_creacion',
            'fecha_actualizacion', 'retroactiva', 'historial', 'versiones', 'revisiones',
        ]
        read_only_fields = fields

    def get_revisiones(self, obj):
        """El jefe de comisión (y roles superiores) ven todas las revisiones; un miembro solo la suya (RF-016)."""
        request = self.context.get('request')
        usuario = getattr(request, 'user', None)
        if usuario is None or not usuario.is_authenticated:
            return []
        revisiones = obj.revisiones.select_related('miembro', 'asignado_por')
        if not hay_privilegio(usuario, Rol.JEFE_COMISION):
            revisiones = revisiones.filter(miembro=usuario)
        return AsignacionRevisionSerializer(revisiones, many=True).data


class PropuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propuesta
        fields = [
            'id', 'premio', 'candidato_nombre', 'candidato_usuario', 'resumen', 'documento',
            'area', 'departamento', 'anio', 'retroactiva', 'version',
        ]
        read_only_fields = ['version']

    def validate_documento(self, archivo):
        return validar_documento(archivo)

    def validate(self, attrs):
        """RF-018: solo premios válidos y solo durante la convocatoria."""
        usuario = self.context['request'].user
        premio = attrs['premio']
        if not premio.activo or not premio.categoria.activo:
            raise ReglaDeNegocio('El premio seleccionado no está disponible.')

        es_gestor = hay_privilegio(usuario, Rol.GESTOR_GLOBAL)
        if premio.es_por_comision:
            if not (es_gestor or usuario.comisiones_dirigidas.filter(premios=premio).exists()):
                raise ReglaDeNegocio('Este premio lo asigna directamente la comisión; no admite propuestas de usuarios.')
        elif usuario.rol == Rol.USUARIO and not convocatoria_activa():
            # Jefes y roles superiores pueden añadir propuestas durante sus etapas de revisión (RF-019/020).
            raise ReglaDeNegocio('No hay una convocatoria activa para subir propuestas.')

        if attrs.get('retroactiva') and not es_gestor:
            attrs['retroactiva'] = False
        return attrs


class PropuestaUpdateSerializer(serializers.ModelSerializer):
    """Campos que un revisor puede modificar/enriquecer (RF-019 y RF-020)."""

    class Meta:
        model = Propuesta
        fields = ['candidato_nombre', 'candidato_usuario', 'resumen', 'documento']

    def validate_documento(self, archivo):
        return validar_documento(archivo)
