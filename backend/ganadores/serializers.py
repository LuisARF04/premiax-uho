from rest_framework import serializers

from .models import Ganador


class GanadorSerializer(serializers.ModelSerializer):
    premio_nombre = serializers.CharField(source='premio.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='premio.categoria.nombre', read_only=True)
    categoria_tipo = serializers.CharField(source='premio.categoria.tipo', read_only=True)

    class Meta:
        model = Ganador
        fields = [
            'id', 'propuesta', 'premio', 'premio_nombre', 'categoria_nombre', 'categoria_tipo',
            'persona_nombre', 'persona_area', 'categoria_cientifica', 'categoria_docente',
            'foto_url', 'fundamentacion', 'tipo', 'anio', 'aprobado_por', 'fecha_aprobacion', 'publicado',
        ]
        read_only_fields = ['aprobado_por', 'fecha_aprobacion']


class GanadorPublicoSerializer(serializers.ModelSerializer):
    premio_nombre = serializers.CharField(source='premio.nombre', read_only=True)
    categoria_nombre = serializers.CharField(source='premio.categoria.nombre', read_only=True)

    class Meta:
        model = Ganador
        fields = [
            'id', 'premio_nombre', 'categoria_nombre', 'persona_nombre', 'persona_area',
            'categoria_cientifica', 'categoria_docente', 'foto_url', 'fundamentacion', 'tipo', 'anio',
        ]
