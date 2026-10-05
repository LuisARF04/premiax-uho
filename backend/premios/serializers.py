from rest_framework import serializers

from .models import CategoriaPremio, EtapaProceso, Premio


class PremioSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Premio
        fields = [
            'id', 'nombre', 'descripcion', 'criterios', 'categoria', 'categoria_nombre',
            'cant_premios', 'cant_reconocimientos', 'es_por_comision', 'activo',
        ]


class PremioPublicoSerializer(serializers.ModelSerializer):
    """No expone cantidades, según RF-002."""

    class Meta:
        model = Premio
        fields = ['id', 'nombre', 'criterios']


class CategoriaPremioSerializer(serializers.ModelSerializer):
    premios = PremioSerializer(many=True, read_only=True)
    premios_count = serializers.IntegerField(source='premios.count', read_only=True)

    class Meta:
        model = CategoriaPremio
        fields = ['id', 'nombre', 'descripcion', 'tipo', 'activo', 'orden', 'premios', 'premios_count']


class CategoriaPremioPublicaSerializer(serializers.ModelSerializer):
    premios = PremioPublicoSerializer(many=True, read_only=True)

    class Meta:
        model = CategoriaPremio
        fields = ['id', 'nombre', 'descripcion', 'tipo', 'premios']


class EtapaProcesoSerializer(serializers.ModelSerializer):
    estado = serializers.CharField(read_only=True)

    class Meta:
        model = EtapaProceso
        fields = ['id', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_cierre', 'anio', 'orden', 'responsable_desc', 'estado']
