from rest_framework import serializers

from premiax.validators import validar_imagen
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
        # El rol solo cambia por la acción `cambiar_rol`, que aplica las reglas del ERS (RF-008).
        read_only_fields = ['username', 'email', 'correo_institucional', 'tipo_aga', 'rol', 'fecha_registro', 'last_login']

    def get_nombre_completo(self, obj):
        return obj.get_full_name() or obj.username

    def validate_foto(self, archivo):
        return validar_imagen(archivo)


class PerfilSerializer(UsuarioSerializer):
    """Autoedición del propio perfil: además del rol, tampoco se puede cambiar el estado de la cuenta."""

    class Meta(UsuarioSerializer.Meta):
        read_only_fields = UsuarioSerializer.Meta.read_only_fields + ['activo']


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
