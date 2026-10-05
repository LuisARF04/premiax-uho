import csv
import io

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auditoria.utils import registrar
from usuarios.permissions import IsAdmin
from .models import Area, Departamento
from .serializers import AreaSerializer, DepartamentoSerializer


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.select_related('responsable').prefetch_related('departamentos').all()
    serializer_class = AreaSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Crear área', 'organizacion', instance.nombre, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Editar área', 'organizacion', instance.nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar área', 'organizacion', instance.nombre, self.request)
        instance.delete()

    @action(detail=False, methods=['post'], permission_classes=[IsAdmin])
    def importar_excel(self, request):
        """
        Importación simplificada desde CSV/Excel con columnas: area,departamento
        (Se admite CSV para no requerir dependencias binarias adicionales.)
        """
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'detail': 'Debe adjuntar un archivo.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            contenido = archivo.read().decode('utf-8-sig')
            lector = csv.DictReader(io.StringIO(contenido))
            if 'area' not in (lector.fieldnames or []):
                return Response({'detail': 'El archivo debe tener columnas: area, departamento'}, status=400)
            creadas_areas, creados_deptos = 0, 0
            for fila in lector:
                nombre_area = (fila.get('area') or '').strip()
                nombre_depto = (fila.get('departamento') or '').strip()
                if not nombre_area:
                    continue
                area, creada = Area.objects.get_or_create(nombre=nombre_area)
                if creada:
                    creadas_areas += 1
                if nombre_depto:
                    _, creado = Departamento.objects.get_or_create(nombre=nombre_depto, area=area)
                    if creado:
                        creados_deptos += 1
            registrar(request.user, 'Importar Excel/CSV', 'organizacion', f'{creadas_areas} áreas, {creados_deptos} departamentos', request)
            return Response({'areas_creadas': creadas_areas, 'departamentos_creados': creados_deptos})
        except Exception as exc:
            return Response({'detail': f'Error al procesar el archivo: {exc}'}, status=400)


class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.select_related('area', 'responsable').all()
    serializer_class = DepartamentoSerializer
    filterset_fields = ['area', 'activo']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Crear departamento', 'organizacion', instance.nombre, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        registrar(self.request.user, 'Editar departamento', 'organizacion', instance.nombre, self.request)

    def perform_destroy(self, instance):
        registrar(self.request.user, 'Eliminar departamento', 'organizacion', instance.nombre, self.request)
        instance.delete()
