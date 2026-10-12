from django.test import TestCase
from rest_framework.test import APIClient

from usuarios.models import Rol, Usuario


def crear(username, rol):
    return Usuario.objects.create_user(username=username, password='x', rol=rol, email=f'{username}@uho.edu.cu')


class CambioDeRolesTests(TestCase):
    def setUp(self):
        self.superadmin = crear('super', Rol.SUPERADMIN)
        self.admin = crear('admin', Rol.ADMIN)
        self.otro_admin = crear('admin2', Rol.ADMIN)
        self.usuario = crear('user', Rol.USUARIO)
        self.client = APIClient()

    def login(self, u):
        self.client.force_authenticate(u)

    def cambiar(self, objetivo, rol):
        return self.client.patch(f'/api/usuarios/{objetivo.id}/cambiar_rol/', {'rol': rol}, format='json')

    def test_1_usuario_no_puede_cambiar_su_propio_rol_por_me(self):
        self.login(self.usuario)
        r = self.client.patch('/api/auth/me/', {'rol': 'superadmin', 'activo': False, 'foto_publica': False}, format='json')
        self.assertEqual(r.status_code, 200)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.rol, Rol.USUARIO)
        self.assertTrue(self.usuario.activo)
        self.assertFalse(self.usuario.foto_publica)  # lo permitido sí se guarda

    def test_2_admin_no_puede_cambiar_rol_con_patch_directo(self):
        self.login(self.admin)
        self.client.patch(f'/api/usuarios/{self.usuario.id}/', {'rol': 'admin'}, format='json')
        self.client.put(f'/api/usuarios/{self.usuario.id}/', {'rol': 'superadmin'}, format='json')
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.rol, Rol.USUARIO)

    def test_admin_asigna_roles_normales_pero_no_admin_ni_superadmin(self):
        self.login(self.admin)
        self.assertEqual(self.cambiar(self.usuario, Rol.GESTOR_GLOBAL).status_code, 200)
        self.assertEqual(self.cambiar(self.usuario, Rol.ADMIN).status_code, 403)
        self.assertEqual(self.cambiar(self.usuario, Rol.SUPERADMIN).status_code, 403)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.rol, Rol.GESTOR_GLOBAL)

    def test_3_admin_no_puede_degradar_a_admin_ni_superadmin(self):
        self.login(self.admin)
        self.assertEqual(self.cambiar(self.superadmin, Rol.USUARIO).status_code, 403)
        self.assertEqual(self.cambiar(self.otro_admin, Rol.USUARIO).status_code, 403)
        self.assertEqual(self.client.patch(f'/api/usuarios/{self.superadmin.id}/', {'activo': False}, format='json').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/usuarios/{self.superadmin.id}/').status_code, 403)
        self.superadmin.refresh_from_db()
        self.assertEqual(self.superadmin.rol, Rol.SUPERADMIN)
        self.assertTrue(self.superadmin.activo)

    def test_4_nadie_cambia_su_propio_rol(self):
        self.login(self.admin)
        self.assertEqual(self.cambiar(self.admin, Rol.SUPERADMIN).status_code, 403)
        self.login(self.superadmin)
        self.assertEqual(self.cambiar(self.superadmin, Rol.USUARIO).status_code, 403)
        self.assertEqual(self.client.delete(f'/api/usuarios/{self.superadmin.id}/').status_code, 403)

    def test_superadmin_si_puede_crear_admins_y_degradar_otros(self):
        self.login(self.superadmin)
        self.assertEqual(self.cambiar(self.usuario, Rol.ADMIN).status_code, 200)
        self.assertEqual(self.cambiar(self.otro_admin, Rol.USUARIO).status_code, 200)

    def test_no_se_puede_dejar_el_sistema_sin_superadmin_activo(self):
        # Un superadmin con la cuenta ya desactivada (token aún vigente) no puede degradar al único superadmin activo.
        inactivo = crear('super_off', Rol.SUPERADMIN)
        Usuario.objects.filter(pk=inactivo.pk).update(activo=False)
        self.login(inactivo)
        self.assertEqual(self.cambiar(self.superadmin, Rol.USUARIO).status_code, 400)
        self.superadmin.refresh_from_db()
        self.assertEqual(self.superadmin.rol, Rol.SUPERADMIN)

    def test_5_crear_usuario_por_api_responde_405_y_no_500(self):
        self.login(self.admin)
        r = self.client.post('/api/usuarios/', {'username': 'nuevo', 'rol': 'admin'}, format='json')
        self.assertEqual(r.status_code, 405)
        self.assertIn('AGA_AUTH', r.data['detail'])
        self.assertFalse(Usuario.objects.filter(username='nuevo').exists())

    def test_usuarios_sin_privilegio_no_acceden_a_la_gestion(self):
        self.login(self.usuario)
        self.assertEqual(self.cambiar(self.admin, Rol.USUARIO).status_code, 403)
        self.assertEqual(self.client.get('/api/usuarios/').status_code, 403)
