from rest_framework import serializers

from premios.serializers import PremioSerializer
from usuarios.serializers import UsuarioMiniSerializer
from .models import Comision, MiembroComision


class MiembroComisionSerializer(serializers.ModelSerializer):
    usuario_detalle = UsuarioMiniSerializer(source='usuario', read_only=True)

    class Meta:
        model = MiembroComision
        fields = ['id', 'comision', 'usuario', 'usuario_detalle', 'fecha_asignacion']


class ComisionSerializer(serializers.ModelSerializer):
    jefe_detalle = UsuarioMiniSerializer(source='jefe', read_only=True)
    miembros = MiembroComisionSerializer(many=True, read_only=True)
    premios_detalle = PremioSerializer(source='premios', many=True, read_only=True)
    propuestas_count = serializers.IntegerField(source='propuestas_asignadas.count', read_only=True)
    propuestas_revisadas_count = serializers.SerializerMethodField()

    class Meta:
        model = Comision
        fields = [
            'id', 'nombre', 'jefe', 'jefe_detalle', 'premios', 'premios_detalle', 'miembros',
            'activo', 'propuestas_count', 'propuestas_revisadas_count',
        ]

    def get_propuestas_revisadas_count(self, obj):
        return obj.propuestas_asignadas.exclude(estado='en_comision').count()
