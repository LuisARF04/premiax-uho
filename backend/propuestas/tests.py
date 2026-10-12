import io
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from openpyxl import Workbook
from rest_framework.test import APIClient

from comisiones.models import AsignacionRevision, Comision, MiembroComision
from notificaciones.models import Notificacion
from notificaciones.utils import procesar_etapas
from organizacion.models import Area, Departamento
from premios.models import CategoriaPremio, EtapaProceso, Premio, ReglamentoSeccion
from propuestas.models import EstadoPropuesta, Propuesta
from usuarios.models import Rol, Usuario

PDF = b'%PDF-1.4 contenido de prueba'


def crear_usuario(username, rol=Rol.USUARIO, **extra):
    return Usuario.objects.create_user(username=username, password='x', rol=rol, email=f'{username}@uho.edu.cu', **extra)


class BaseTest(TestCase):
    def setUp(self):
        hoy = timezone.now().date()
        self.area = Area.objects.create(nombre='Facultad A')
        self.depto = Departamento.objects.create(nombre='Dpto 1', area=self.area)
        self.cat = CategoriaPremio.objects.create(nombre='Integrales', tipo='ind_docente')
        self.premio = Premio.objects.create(nombre='Mejor profesor', categoria=self.cat)
        self.premio_comision = Premio.objects.create(nombre='Por comisión', categoria=self.cat, es_por_comision=True)
        self.convocatoria = EtapaProceso.objects.create(
            nombre='Convocatoria', fecha_inicio=hoy - timedelta(days=1), fecha_cierre=hoy + timedelta(days=20),
            es_convocatoria=True,
        )
        self.usuario = crear_usuario('user', area=self.area, departamento=self.depto)
        self.jefe_depto = crear_usuario('jdep', Rol.JEFE_DEPARTAMENTO, area=self.area, departamento=self.depto)
        self.depto.responsable = self.jefe_depto
        self.depto.save()
        self.admin = crear_usuario('admin', Rol.ADMIN)
        self.gestor = crear_usuario('gestor', Rol.GESTOR_GLOBAL)
        self.client = APIClient()

    def login(self, usuario):
        self.client.force_authenticate(usuario)

    def proponer(self, premio=None, **extra):
        datos = {'premio': (premio or self.premio).id, 'candidato_nombre': 'Ana Pérez', 'resumen': 'Méritos', **extra}
        return self.client.post('/api/propuestas/', datos, format='multipart')


class ConvocatoriaYValidacionTests(BaseTest):
    def test_usuario_puede_proponer_en_convocatoria(self):
        self.login(self.usuario)
        r = self.proponer()
        self.assertEqual(r.status_code, 201, r.data)
        propuesta = Propuesta.objects.get()
        self.assertEqual(propuesta.version, 1)
        self.assertEqual(propuesta.versiones.count(), 1)
        self.assertTrue(Notificacion.objects.filter(usuario=self.jefe_depto).exists())

    def test_sin_convocatoria_el_usuario_no_puede_proponer(self):
        EtapaProceso.objects.update(es_convocatoria=False)
        self.login(self.usuario)
        r = self.proponer()
        self.assertEqual(r.status_code, 400)
        self.assertIn('convocatoria', r.data['detail'])

    def test_jefe_puede_anadir_propuesta_fuera_de_convocatoria(self):
        EtapaProceso.objects.update(es_convocatoria=False)
        self.login(self.jefe_depto)
        self.assertEqual(self.proponer().status_code, 201)

    def test_premio_inactivo_o_por_comision_es_rechazado(self):
        self.login(self.usuario)
        self.premio.activo = False
        self.premio.save()
        self.assertEqual(self.proponer().status_code, 400)
        self.assertEqual(self.proponer(self.premio_comision).status_code, 400)

    def test_documento_valida_tipo_y_tamano(self):
        self.login(self.usuario)
        malo = SimpleUploadedFile('virus.exe', b'MZ binario')
        self.assertEqual(self.proponer(documento=malo).status_code, 400)
        falso = SimpleUploadedFile('falso.pdf', b'esto no es un pdf')
        self.assertEqual(self.proponer(documento=falso).status_code, 400)
        grande = SimpleUploadedFile('grande.pdf', PDF + b'0' * (10 * 1024 * 1024))
        self.assertEqual(self.proponer(documento=grande).status_code, 400)
        bueno = SimpleUploadedFile('ok.pdf', PDF)
        self.assertEqual(self.proponer(documento=bueno).status_code, 201)


class VersionesTests(BaseTest):
    def test_editar_incrementa_version_y_guarda_historial(self):
        self.login(self.usuario)
        pid = self.proponer().data['id']
        self.login(self.jefe_depto)
        r = self.client.patch(f'/api/propuestas/{pid}/', {'resumen': 'Resumen enriquecido'}, format='multipart')
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data['version'], 2)
        self.assertEqual(len(r.data['versiones']), 2)
        # Sin cambios reales no se crea otra versión.
        r = self.client.patch(f'/api/propuestas/{pid}/', {'resumen': 'Resumen enriquecido'}, format='multipart')
        self.assertEqual(r.data['version'], 2)

    def test_usuario_sin_permiso_no_edita_y_no_puede_cambiar_estado(self):
        self.login(self.usuario)
        pid = self.proponer().data['id']
        otro = crear_usuario('otro', area=self.area, departamento=self.depto)
        self.login(otro)
        self.assertEqual(self.client.patch(f'/api/propuestas/{pid}/', {'resumen': 'x'}).status_code, 404)
        self.login(self.usuario)
        self.client.patch(f'/api/propuestas/{pid}/', {'estado': 'aprobada', 'resumen': 'Nuevo'}, format='multipart')
        self.assertEqual(Propuesta.objects.get(pk=pid).estado, EstadoPropuesta.PENDIENTE_DEPARTAMENTO)


class RevisionesComisionTests(BaseTest):
    def setUp(self):
        super().setUp()
        self.jefe_com = crear_usuario('jcom', Rol.JEFE_COMISION)
        self.miembro = crear_usuario('miembro', Rol.MIEMBRO_COMISION)
        self.otro_miembro = crear_usuario('otro_m', Rol.MIEMBRO_COMISION)
        self.comision = Comision.objects.create(nombre='Comisión 1', jefe=self.jefe_com)
        self.comision.premios.add(self.premio)
        for m in (self.miembro, self.otro_miembro):
            MiembroComision.objects.create(comision=self.comision, usuario=m)
        self.p1 = Propuesta.objects.create(
            premio=self.premio, creado_por=self.usuario, area=self.area, candidato_nombre='A', resumen='r',
            estado=EstadoPropuesta.EN_COMISION, nivel_actual='comision', comision=self.comision,
        )
        self.p2 = Propuesta.objects.create(
            premio=self.premio, creado_por=self.usuario, area=self.area, candidato_nombre='B', resumen='r',
            estado=EstadoPropuesta.EN_COMISION, nivel_actual='comision', comision=self.comision,
        )

    def test_miembro_solo_ve_lo_asignado(self):
        self.login(self.miembro)
        self.assertEqual(self.client.get('/api/propuestas/').data['count'], 0)
        self.login(self.jefe_com)
        r = self.client.post(f'/api/propuestas/{self.p1.id}/asignar_revision/', {'miembro': self.miembro.id})
        self.assertEqual(r.status_code, 201, r.data)
        self.login(self.miembro)
        ids = [p['id'] for p in self.client.get('/api/propuestas/').data['results']]
        self.assertEqual(ids, [self.p1.id])
        self.assertEqual(self.client.get(f'/api/propuestas/{self.p2.id}/').status_code, 404)
        self.assertTrue(Notificacion.objects.filter(usuario=self.miembro, titulo__contains='asignó').exists())

    def test_solo_el_jefe_asigna_y_solo_a_miembros(self):
        self.login(self.miembro)
        # Un miembro sin asignaciones ni siquiera ve la propuesta (404) y por tanto no puede asignar.
        self.assertEqual(self.client.post(f'/api/propuestas/{self.p1.id}/asignar_revision/', {'miembro': self.miembro.id}).status_code, 404)
        AsignacionRevision.objects.create(propuesta=self.p1, miembro=self.miembro, asignado_por=self.jefe_com)
        self.assertEqual(self.client.post(f'/api/propuestas/{self.p1.id}/asignar_revision/', {'miembro': self.otro_miembro.id}).status_code, 403)
        self.login(self.jefe_com)
        ajeno = crear_usuario('ajeno')
        self.assertEqual(self.client.post(f'/api/propuestas/{self.p1.id}/asignar_revision/', {'miembro': ajeno.id}).status_code, 400)

    def test_miembro_registra_revision_y_ve_solo_la_suya(self):
        AsignacionRevision.objects.create(propuesta=self.p1, miembro=self.miembro, asignado_por=self.jefe_com)
        AsignacionRevision.objects.create(propuesta=self.p1, miembro=self.otro_miembro, asignado_por=self.jefe_com)
        self.login(self.miembro)
        self.assertEqual(self.client.post(f'/api/propuestas/{self.p1.id}/registrar_revision/', {'criterio': ''}).status_code, 400)
        self.assertEqual(self.client.post(f'/api/propuestas/{self.p1.id}/registrar_revision/', {'criterio': 'x', 'puntuacion': 11}).status_code, 400)
        r = self.client.post(f'/api/propuestas/{self.p1.id}/registrar_revision/', {'criterio': 'Excelente', 'puntuacion': 9})
        self.assertEqual(r.status_code, 200, r.data)
        detalle = self.client.get(f'/api/propuestas/{self.p1.id}/').data
        self.assertEqual(len(detalle['revisiones']), 1)
        self.login(self.jefe_com)
        self.assertEqual(len(self.client.get(f'/api/propuestas/{self.p1.id}/').data['revisiones']), 2)


class OrganizacionTests(BaseTest):
    def xlsx(self, filas, nombre='areas.xlsx'):
        wb = Workbook()
        ws = wb.active
        for fila in filas:
            ws.append(fila)
        buf = io.BytesIO()
        wb.save(buf)
        return SimpleUploadedFile(nombre, buf.getvalue())

    def test_importar_xlsx_valido(self):
        self.login(self.admin)
        r = self.client.post('/api/areas/importar_excel/', {'archivo': self.xlsx([['Area', 'Departamento'], ['Nueva', 'D1'], ['Nueva', 'D2']])}, format='multipart')
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data['areas_creadas'], 1)
        self.assertEqual(r.data['departamentos_creados'], 2)

    def test_importar_estructura_invalida_o_con_errores_no_importa_nada(self):
        self.login(self.admin)
        r = self.client.post('/api/areas/importar_excel/', {'archivo': self.xlsx([['Nombre', 'Otra'], ['x', 'y']])}, format='multipart')
        self.assertEqual(r.status_code, 400)
        r = self.client.post('/api/areas/importar_excel/', {'archivo': self.xlsx([['area', 'departamento'], ['Buena', 'D'], ['', 'Huérfano']])}, format='multipart')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Area.objects.filter(nombre='Buena').exists())

    def test_importar_csv_sigue_funcionando(self):
        self.login(self.admin)
        csv_ = SimpleUploadedFile('a.csv', 'area,departamento\nCSV,D1\n'.encode())
        self.assertEqual(self.client.post('/api/areas/importar_excel/', {'archivo': csv_}, format='multipart').status_code, 200)

    def test_eliminar_area_con_usuarios_pide_confirmacion(self):
        self.login(self.admin)
        r = self.client.delete(f'/api/areas/{self.area.id}/')
        self.assertEqual(r.status_code, 409)
        self.assertTrue(r.data['requiere_confirmacion'])
        self.assertTrue(Area.objects.filter(pk=self.area.id).exists())
        self.assertEqual(self.client.delete(f'/api/areas/{self.area.id}/?confirmar=true').status_code, 204)

    def test_eliminar_departamento_con_usuarios_pide_confirmacion(self):
        self.login(self.admin)
        self.assertEqual(self.client.delete(f'/api/departamentos/{self.depto.id}/').status_code, 409)
        self.assertEqual(self.client.delete(f'/api/departamentos/{self.depto.id}/?confirmar=true').status_code, 204)


class ReglamentoYEtapasTests(BaseTest):
    def test_reglamento_publico_y_edicion_solo_admin(self):
        publico = self.client.get('/api/publico/reglamento/')
        self.assertEqual(publico.status_code, 200)
        self.assertGreaterEqual(len(publico.data), 3)  # secciones por defecto de la migración
        self.login(self.usuario)
        self.assertEqual(self.client.post('/api/reglamento/', {'titulo': 'x', 'contenido': 'y'}).status_code, 403)
        self.login(self.admin)
        r = self.client.post('/api/reglamento/', {'titulo': 'Nueva', 'contenido': 'Texto', 'orden': 9}, format='json')
        self.assertEqual(r.status_code, 201, r.data)
        self.client.patch(f"/api/reglamento/{r.data['id']}/", {'contenido': 'Cambiado'}, format='json')
        self.client.logout()
        self.client.force_authenticate(None)
        textos = [s['contenido'] for s in self.client.get('/api/publico/reglamento/').data]
        self.assertIn('Cambiado', textos)
        ReglamentoSeccion.objects.filter(pk=r.data['id']).update(activo=False)
        textos = [s['contenido'] for s in self.client.get('/api/publico/reglamento/').data]
        self.assertNotIn('Cambiado', textos)

    def test_convocatoria_activa_depende_del_flag(self):
        self.assertTrue(self.client.get('/api/publico/convocatoria-activa/').data['convocatoria_activa'])
        EtapaProceso.objects.update(es_convocatoria=False)
        self.assertFalse(self.client.get('/api/publico/convocatoria-activa/').data['convocatoria_activa'])

    def test_avisos_de_etapa_se_envian_una_sola_vez(self):
        hoy = timezone.now().date()
        EtapaProceso.objects.create(nombre='Cierre próximo', fecha_inicio=hoy - timedelta(days=10), fecha_cierre=hoy + timedelta(days=2))
        enviados = procesar_etapas(forzar=True)
        self.assertGreaterEqual(enviados, 2)  # inicio de la convocatoria + alerta de "Cierre próximo"
        self.assertTrue(Notificacion.objects.filter(titulo__startswith='Inició la etapa: Convocatoria', usuario=self.usuario).exists())
        self.assertTrue(Notificacion.objects.filter(titulo__startswith='Se acerca la fecha límite', usuario=self.gestor).exists())
        # Etapa no-convocatoria: el usuario común no recibe nada.
        self.assertFalse(Notificacion.objects.filter(titulo__contains='Cierre próximo', usuario=self.usuario).exists())
        self.assertEqual(procesar_etapas(forzar=True), 0)
        self.assertTrue(mail.outbox)


class EstadisticasEInactivosTests(BaseTest):
    def test_estadisticas_accesibles_para_jefe_de_comision_pero_no_para_usuarios(self):
        jefe = crear_usuario('jc', Rol.JEFE_COMISION)
        self.login(jefe)
        r = self.client.get('/api/dashboard/estadisticas/')
        self.assertEqual(r.status_code, 200)
        for clave in ('propuestas_por_premio', 'propuestas_por_departamento', 'estado_por_area', 'participacion_roles', 'ganadores_por_anio'):
            self.assertIn(clave, r.data)
        self.login(self.jefe_depto)
        self.assertEqual(self.client.get('/api/dashboard/estadisticas/').status_code, 403)

    def test_inactivos_incluye_sin_ingreso_y_propuestas_sin_revisar(self):
        self.login(self.usuario)
        self.proponer()
        self.jefe_depto.last_login = timezone.now()
        self.jefe_depto.save()
        self.login(self.gestor)
        data = self.client.get('/api/usuarios-inactivos/').data
        jefe = next(u for u in data['usuarios'] if u['id'] == self.jefe_depto.id)
        self.assertEqual(jefe['pendientes'], 1)
        self.assertEqual(jefe['motivos'], ['propuestas_sin_revisar'])
        self.assertTrue(any(r['rol'] == Rol.USUARIO for r in data['por_rol']))
