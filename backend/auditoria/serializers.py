from rest_framework import serializers

from .models import LogAuditoria


class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    usuario_rol = serializers.CharField(source='usuario.get_rol_display', read_only=True, default=None)

    class Meta:
        model = LogAuditoria
        fields = ['id', 'usuario', 'usuario_nombre', 'usuario_rol', 'accion', 'modulo', 'detalle', 'ip', 'fecha']

    def get_usuario_nombre(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username if obj.usuario else 'Sistema'
