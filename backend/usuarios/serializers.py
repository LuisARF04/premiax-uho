from rest_framework import serializers

from .models import Usuario


class UsuarioMiniSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    area_nombre = serializers.CharField(source='area.nombre', read_only=True, default=None)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre_completo', 'rol', 'area', 'area_nombre']

    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username


class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    area_nombre = serializers.CharField(source='area.nombre', read_only=True, default=None)
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True, default=None)
    categoria_docente_nombre = serializers.CharField(source='categoria_docente.nombre', read_only=True, default=None)
    categoria_cientifica_nombre = serializers.CharField(source='categoria_cientifica.nombre', read_only=True, default=None)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'nombre_completo', 'email', 'correo_institucional',
            'tipo_aga', 'rol', 'rol_display', 'area', 'area_nombre', 'departamento', 'departamento_nombre',
            'categoria_docente', 'categoria_docente_nombre', 'categoria_cientifica', 'categoria_cientifica_nombre',
            'cargo', 'foto', 'foto_publica', 'perfil_completo', 'notif_email', 'notif_fechas_limite',
            'notif_propuestas_elevadas', 'notif_resumen_semanal', 'activo', 'fecha_registro', 'last_login',
        ]
        read_only_fields = ['username', 'email', 'correo_institucional', 'tipo_aga', 'fecha_registro', 'last_login']

    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username


class CompletarPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['area', 'departamento', 'categoria_docente', 'categoria_cientifica']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.perfil_completo = True
        instance.save(update_fields=['perfil_completo'])
        return instance


class CambiarRolSerializer(serializers.Serializer):
    rol = serializers.ChoiceField(choices=Usuario._meta.get_field('rol').choices)
