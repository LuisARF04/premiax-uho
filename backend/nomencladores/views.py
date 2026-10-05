from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from auditoria.utils import registrar
from usuarios.permissions import IsAdmin
from .models import Cargo, Carrera, CategoriaCientifica, CategoriaDocente
from .serializers import CargoSerializer, CarreraSerializer, CategoriaCientificaSerializer, CategoriaDocenteSerializer


class NomencladorViewSetMixin:
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, f'Crear {self.nombre_log}', 'nomencladores', instance.nombre, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, f'Editar {self.nombre_log}', 'nomencladores', instance.nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, f'Eliminar {self.nombre_log}', 'nomencladores', instance.nombre, self.request)
        instance.delete()


class CategoriaDocenteViewSet(NomencladorViewSetMixin, viewsets.ModelViewSet):
    queryset = CategoriaDocente.objects.all()
    serializer_class = CategoriaDocenteSerializer
    nombre_log = 'categoría docente'


class CategoriaCientificaViewSet(NomencladorViewSetMixin, viewsets.ModelViewSet):
    queryset = CategoriaCientifica.objects.all()
    serializer_class = CategoriaCientificaSerializer
    nombre_log = 'categoría científica'


class CargoViewSet(NomencladorViewSetMixin, viewsets.ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    nombre_log = 'cargo'


class CarreraViewSet(NomencladorViewSetMixin, viewsets.ModelViewSet):
    queryset = Carrera.objects.all()
    serializer_class = CarreraSerializer
    nombre_log = 'carrera'
