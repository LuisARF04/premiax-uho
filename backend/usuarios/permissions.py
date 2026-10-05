from rest_framework.permissions import BasePermission

from .models import Rol, nivel_rol


def hay_privilegio(usuario, rol_minimo: str) -> bool:
    if not usuario or not usuario.is_authenticated:
        return False
    return nivel_rol(usuario.rol) <= nivel_rol(rol_minimo)


class IsRoleAtLeast(BasePermission):
    """Uso: permission_classes = [IsRoleAtLeast(Rol.ADMIN)] a través de una fábrica."""
    rol_minimo = Rol.USUARIO

    def has_permission(self, request, view):
        return hay_privilegio(request.user, self.rol_minimo)


def rol_minimo(rol):
    return type('IsRoleAtLeastDynamic', (IsRoleAtLeast,), {'rol_minimo': rol})


IsAdmin = rol_minimo(Rol.ADMIN)
IsSuperadmin = rol_minimo(Rol.SUPERADMIN)
IsGestorGlobal = rol_minimo(Rol.GESTOR_GLOBAL)
IsJefeComision = rol_minimo(Rol.JEFE_COMISION)
IsJefeArea = rol_minimo(Rol.JEFE_AREA)
IsJefeDepartamento = rol_minimo(Rol.JEFE_DEPARTAMENTO)
