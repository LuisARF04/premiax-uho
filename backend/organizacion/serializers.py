from rest_framework import serializers

from .models import Area, Departamento


class DepartamentoSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source='area.nombre', read_only=True)
    responsable_nombre = serializers.SerializerMethodField()
    propuestas_count = serializers.IntegerField(source='propuestas.count', read_only=True)

    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'descripcion', 'area', 'area_nombre', 'responsable', 'responsable_nombre', 'activo', 'propuestas_count']

    def get_responsable_nombre(self, obj):
        return obj.responsable.get_full_name() if obj.responsable else None


class AreaSerializer(serializers.ModelSerializer):
    responsable_nombre = serializers.SerializerMethodField()
    departamentos_count = serializers.IntegerField(source='departamentos.count', read_only=True)
    propuestas_count = serializers.IntegerField(source='propuestas.count', read_only=True)
    departamentos = DepartamentoSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ['id', 'nombre', 'descripcion', 'responsable', 'responsable_nombre', 'activo', 'departamentos_count', 'propuestas_count', 'departamentos']

    def get_responsable_nombre(self, obj):
        return obj.responsable.get_full_name() if obj.responsable else None
