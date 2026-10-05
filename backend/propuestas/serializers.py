from rest_framework import serializers

from premios.serializers import PremioSerializer
from usuarios.serializers import UsuarioMiniSerializer
from .models import HistorialPropuesta, Propuesta


class HistorialPropuestaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    usuario_rol = serializers.CharField(source='usuario.get_rol_display', read_only=True, default=None)

    class Meta:
        model = HistorialPropuesta
        fields = ['id', 'usuario', 'usuario_nombre', 'usuario_rol', 'accion', 'descripcion', 'nivel_desde', 'nivel_hasta', 'fecha']

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
            'comision', 'comision_nombre', 'creado_por', 'creado_por_nombre', 'anio',
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

    class Meta:
        model = Propuesta
        fields = [
            'id', 'premio', 'premio_detalle', 'creado_por', 'creado_por_detalle', 'area', 'area_nombre',
            'departamento', 'departamento_nombre', 'candidato_nombre', 'candidato_usuario', 'candidato_usuario_detalle',
            'resumen', 'documento', 'estado', 'nivel_actual', 'comision', 'comision_nombre',
            'seleccion_comision', 'fundamentacion_comision', 'anio', 'fecha_creacion', 'fecha_actualizacion',
            'retroactiva', 'historial',
        ]


class PropuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Propuesta
        fields = [
            'id', 'premio', 'candidato_nombre', 'candidato_usuario', 'resumen', 'documento',
            'area', 'departamento', 'anio', 'retroactiva',
        ]
