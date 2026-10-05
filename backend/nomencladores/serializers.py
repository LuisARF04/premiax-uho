from rest_framework import serializers

from .models import Cargo, Carrera, CategoriaCientifica, CategoriaDocente


class CategoriaDocenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaDocente
        fields = ['id', 'nombre', 'activo', 'orden']


class CategoriaCientificaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaCientifica
        fields = ['id', 'nombre', 'activo', 'orden']


class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = ['id', 'nombre', 'activo', 'orden']


class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id', 'nombre', 'activo', 'orden']
