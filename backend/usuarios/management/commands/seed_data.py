from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from comisiones.models import Comision, MiembroComision
from ganadores.models import Ganador
from nomencladores.models import Cargo, Carrera, CategoriaCientifica, CategoriaDocente
from organizacion.models import Area, Departamento
from premios.models import CategoriaPremio, EtapaProceso, Premio, TipoCategoria
from propuestas.models import EstadoPropuesta, HistorialPropuesta, NivelPropuesta, Propuesta
from usuarios.models import Rol, TipoUsuarioAGA, Usuario

PASSWORD = 'Premiax2025!'


class Command(BaseCommand):
    help = 'Carga datos de ejemplo para PREMIAX-UHO (nomencladores, áreas, premios, usuarios, propuestas, comisiones y ganadores).'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Borra los datos existentes antes de sembrar.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Borrando datos existentes...')
            Ganador.objects.all().delete()
            HistorialPropuesta.objects.all().delete()
            Propuesta.objects.all().delete()
            MiembroComision.objects.all().delete()
            Comision.objects.all().delete()
            Premio.objects.all().delete()
            CategoriaPremio.objects.all().delete()
            EtapaProceso.objects.all().delete()
            Usuario.objects.exclude(is_superuser=True).delete()
            Departamento.objects.all().delete()
            Area.objects.all().delete()
            CategoriaDocente.objects.all().delete()
            CategoriaCientifica.objects.all().delete()
            Cargo.objects.all().delete()
            Carrera.objects.all().delete()

        self.stdout.write('Sembrando nomencladores...')
        cat_docentes = self._crear_nomencladores(CategoriaDocente, ['Instructor', 'Profesor Asistente', 'Profesor Auxiliar', 'Profesor Titular'])
        cat_cientificas = self._crear_nomencladores(CategoriaCientifica, ['Lic.', 'MSc.', 'Dr.C.'])
        self._crear_nomencladores(Cargo, ['Decano', 'Jefe de Departamento', 'Jefe de Carrera', 'Profesor Principal de Año', 'Rector', 'Vicerrector'])
        self._crear_nomencladores(Carrera, ['Ingeniería Informática', 'Agronomía', 'Contabilidad y Finanzas', 'Derecho', 'Medicina'])

        self.stdout.write('Sembrando áreas y departamentos...')
        areas = self._crear_areas()

        self.stdout.write('Sembrando categorías y premios...')
        premios = self._crear_categorias_y_premios()

        self.stdout.write('Sembrando etapas del proceso...')
        self._crear_etapas()

        self.stdout.write('Sembrando usuarios...')
        usuarios = self._crear_usuarios(areas, cat_docentes, cat_cientificas)

        self.stdout.write('Sembrando comisiones...')
        comisiones = self._crear_comisiones(usuarios, premios)

        self.stdout.write('Sembrando propuestas de ejemplo...')
        self._crear_propuestas(usuarios, areas, premios, comisiones)

        self.stdout.write('Sembrando ganadores históricos...')
        self._crear_ganadores_historicos(premios)

        self.stdout.write(self.style.SUCCESS('¡Datos de ejemplo cargados con éxito!'))
        self.stdout.write(self.style.WARNING(f'Contraseña de todos los usuarios de prueba: {PASSWORD}'))

    def _crear_nomencladores(self, modelo, nombres):
        objs = {}
        for i, nombre in enumerate(nombres):
            obj, _ = modelo.objects.get_or_create(nombre=nombre, defaults={'orden': i})
            objs[nombre] = obj
        return objs

    def _crear_areas(self):
        estructura = {
            'Dirección de Recursos Humanos': ['Gestión de Capital Humano', 'Capacitación y Desarrollo', 'Nóminas'],
            'Facultad de Informática': ['Ciencias de la Computación', 'Ingeniería de Software', 'Matemática'],
            'Facultad de Agronomía': ['Biología', 'Zootecnia', 'Agronomía General'],
            'Vicerrectoría Docente (VRRPA)': ['Formación de Pregrado', 'Postgrado'],
            'Dirección de Ciencia y Técnica': ['Proyectos de Investigación', 'Innovación'],
        }
        areas = {}
        for nombre_area, deptos in estructura.items():
            area, _ = Area.objects.get_or_create(nombre=nombre_area)
            areas[nombre_area] = {'obj': area, 'deptos': {}}
            for nombre_depto in deptos:
                depto, _ = Departamento.objects.get_or_create(nombre=nombre_depto, area=area)
                areas[nombre_area]['deptos'][nombre_depto] = depto
        return areas

    def _crear_categorias_y_premios(self):
        categorias = {}
        for nombre, tipo in [
            ('Individuales Docentes', TipoCategoria.IND_DOCENTE),
            ('Individuales No Docentes', TipoCategoria.IND_NO_DOCENTE),
            ('Colectivos Docentes', TipoCategoria.COL_DOCENTE),
            ('Colectivos No Docentes', TipoCategoria.COL_NO_DOCENTE),
        ]:
            categorias[tipo], _ = CategoriaPremio.objects.get_or_create(nombre=nombre, tipo=tipo)

        datos_premios = [
            ('Mejor profesor integralmente', TipoCategoria.IND_DOCENTE, 10, 1, False, 'Resultados docentes, científicos e integrales sostenidos.'),
            ('Mejor profesor joven (hasta 35 años)', TipoCategoria.IND_DOCENTE, 3, 1, False, 'Destacado desempeño docente en los primeros años de carrera.'),
            ('Mejor profesor en apoyo a la gestión de la calidad', TipoCategoria.IND_DOCENTE, 1, 0, True, 'Aporte sobresaliente a los procesos de calidad institucional.'),
            ('Mejor profesor a tiempo parcial', TipoCategoria.IND_DOCENTE, 2, 0, False, 'Desempeño destacado como profesor a tiempo parcial.'),
            ('Mejor profesor en trabajo docente educativo y metodológico', TipoCategoria.IND_DOCENTE, 2, 0, False, 'Excelencia en la labor educativa y metodológica.'),
            ('Mejor profesor guía', TipoCategoria.IND_DOCENTE, 3, 1, False,
             'Resultados del trabajo como profesor guía de grupo. Participación en actividades formativas extracurriculares. Contribución al desarrollo cultural y social del grupo.'),
            ('Mejor profesor principal de año académico', TipoCategoria.IND_DOCENTE, 3, 1, False, 'Liderazgo y resultados como profesor principal de año.'),
            ('Mejor profesor a tiempo completo en CUM-FUM', TipoCategoria.IND_DOCENTE, 1, 1, False, 'Desempeño destacado en un Centro/Filial Universitaria Municipal.'),
            ('Mejor coordinador del colectivo de carrera (Jefe de carrera)', TipoCategoria.IND_DOCENTE, 2, 1, False, 'Gestión sobresaliente al frente de un colectivo de carrera.'),

            ('Mejor trabajador no docente', TipoCategoria.IND_NO_DOCENTE, 5, 1, False, 'Desempeño ejemplar en funciones no docentes.'),
            ('Mejor recién graduado', TipoCategoria.IND_NO_DOCENTE, 3, 0, False, 'Incorporación destacada de un recién graduado a la institución.'),
            ('Distinción Roberto Rodríguez Córdoba', TipoCategoria.IND_NO_DOCENTE, 1, 0, False, 'Reconocimiento a la labor medioambiental y científico-técnica.'),

            ('Mejor Facultad integralmente', TipoCategoria.COL_DOCENTE, 1, 1, True, 'Resultados integrales sobresalientes de una Facultad.'),
            ('Mejor Departamento docente', TipoCategoria.COL_DOCENTE, 1, 1, False, 'Resultados docentes, científicos y metodológicos del colectivo.'),
            ('Mejor Departamento docente de CUM-FUM', TipoCategoria.COL_DOCENTE, 1, 0, False, 'Mejor colectivo docente de un CUM-FUM.'),

            ('Mejor Colectivo no docente', TipoCategoria.COL_NO_DOCENTE, 1, 1, False, 'Desempeño colectivo sobresaliente en funciones no docentes.'),
            ('Mejor área de apoyo', TipoCategoria.COL_NO_DOCENTE, 1, 1, True, 'Área de apoyo con resultados destacados en el período.'),
        ]

        premios = {}
        for nombre, tipo, cant_premios, cant_reconoc, por_comision, criterios in datos_premios:
            premio, _ = Premio.objects.get_or_create(
                nombre=nombre, categoria=categorias[tipo],
                defaults=dict(
                    cant_premios=cant_premios, cant_reconocimientos=cant_reconoc,
                    es_por_comision=por_comision, criterios=criterios,
                ),
            )
            premios[nombre] = premio
        return premios

    def _crear_etapas(self):
        hoy = timezone.now().date()
        anio = hoy.year
        etapas = [
            ('Convocatoria y propuestas', hoy - timedelta(days=5), hoy + timedelta(days=25), 'Usuarios', 1),
            ('Revisión a nivel de departamento', hoy - timedelta(days=5), hoy + timedelta(days=25), 'Jefes de Departamento', 2),
            ('Trabajo de comisiones', hoy - timedelta(days=3), hoy + timedelta(days=8), 'Jefes de Comisión', 3),
            ('Análisis Comisión Central', hoy + timedelta(days=15), hoy + timedelta(days=15), 'Gestor Global', 4),
            ('Aprobación Consejo de Dirección', hoy + timedelta(days=20), hoy + timedelta(days=30), 'Rectorado', 5),
            ('Publicación y entrega de certificados', hoy + timedelta(days=35), hoy + timedelta(days=55), 'Rectorado', 6),
        ]
        for nombre, inicio, cierre, resp, orden in etapas:
            EtapaProceso.objects.get_or_create(
                nombre=nombre, anio=anio,
                defaults=dict(fecha_inicio=inicio, fecha_cierre=cierre, responsable_desc=resp, orden=orden),
            )

    def _crear_usuario(self, username, first_name, last_name, rol, area=None, departamento=None,
                        categoria_docente=None, categoria_cientifica=None, tipo_aga=TipoUsuarioAGA.TRABAJADOR):
        usuario, creado = Usuario.objects.get_or_create(
            username=username,
            defaults=dict(
                first_name=first_name, last_name=last_name, email=f'{username}@uho.edu.cu',
                correo_institucional=f'{username}@uho.edu.cu', rol=rol, area=area, departamento=departamento,
                categoria_docente=categoria_docente, categoria_cientifica=categoria_cientifica,
                tipo_aga=tipo_aga, perfil_completo=True,
            ),
        )
        if creado:
            usuario.set_password(PASSWORD)
            usuario.save()
        return usuario

    def _crear_usuarios(self, areas, cat_docentes, cat_cientificas):
        drh = areas['Dirección de Recursos Humanos']['obj']
        drh_gch = areas['Dirección de Recursos Humanos']['deptos']['Gestión de Capital Humano']
        fi = areas['Facultad de Informática']['obj']
        fi_cc = areas['Facultad de Informática']['deptos']['Ciencias de la Computación']
        fi_is = areas['Facultad de Informática']['deptos']['Ingeniería de Software']
        fa = areas['Facultad de Agronomía']['obj']
        fa_bio = areas['Facultad de Agronomía']['deptos']['Biología']
        vrrpa = areas['Vicerrectoría Docente (VRRPA)']['obj']
        vrrpa_pregrado = areas['Vicerrectoría Docente (VRRPA)']['deptos']['Formación de Pregrado']

        u = {}
        u['superadmin'] = self._crear_usuario('cperez', 'Carlos', 'Pérez González', Rol.SUPERADMIN, drh, drh_gch)
        u['admin'] = self._crear_usuario('mrodriguez', 'María', 'Rodríguez López', Rol.ADMIN, fi, fi_cc,
                                          cat_docentes['Profesor Titular'], cat_cientificas['Dr.C.'])
        u['gestor_global'] = self._crear_usuario('jpmartinez', 'Juan Pablo', 'Martínez', Rol.GESTOR_GLOBAL, vrrpa, vrrpa_pregrado,
                                                  cat_docentes['Profesor Auxiliar'], cat_cientificas['MSc.'])
        u['jefe_area_agronomia'] = self._crear_usuario('agarcia', 'Ana', 'García Ruiz', Rol.JEFE_AREA, fa, fa_bio,
                                                        cat_docentes['Profesor Auxiliar'], cat_cientificas['MSc.'])
        u['jefe_depto_biologia'] = self._crear_usuario('ltorres', 'Luis', 'Torres Mora', Rol.JEFE_DEPARTAMENTO, fa, fa_bio,
                                                        cat_docentes['Profesor Asistente'], cat_cientificas['Lic.'])
        u['jefe_comision_pregrado'] = self._crear_usuario('rfuentes', 'Raúl', 'Fuentes', Rol.JEFE_COMISION, vrrpa, vrrpa_pregrado,
                                                           cat_docentes['Profesor Titular'], cat_cientificas['Dr.C.'])
        u['jefe_comision_integral'] = self._crear_usuario('vperez', 'Víctor', 'Pérez Díaz', Rol.JEFE_COMISION, tipo_aga=TipoUsuarioAGA.INSTITUCIONAL)
        u['miembro_pgomez'] = self._crear_usuario('pgomez', 'Pedro', 'Gómez Castro', Rol.MIEMBRO_COMISION, fi, fi_is,
                                                   cat_docentes['Profesor Asistente'], cat_cientificas['Lic.'])
        u['miembro_clpena'] = self._crear_usuario('clpena', 'Carlos', 'López Peña', Rol.MIEMBRO_COMISION, drh, drh_gch)
        u['usuario_rmedina'] = self._crear_usuario('rmedina', 'Rosa', 'Medina Pérez', Rol.USUARIO, fi, fi_is,
                                                    cat_docentes['Profesor Auxiliar'], cat_cientificas['MSc.'])
        u['usuario_msoto'] = self._crear_usuario('msoto', 'María', 'Soto López', Rol.USUARIO, vrrpa, vrrpa_pregrado,
                                                  cat_docentes['Profesor Asistente'], cat_cientificas['Lic.'])
        return u

    def _crear_comisiones(self, u, premios):
        comisiones = {}

        c1 = Comision.objects.get_or_create(nombre='Integrales y Gestión', defaults={'jefe': u['jefe_comision_integral']})[0]
        c1.premios.set([
            premios['Mejor profesor integralmente'], premios['Mejor profesor joven (hasta 35 años)'],
            premios['Mejor Departamento docente'], premios['Mejor Colectivo no docente'],
            premios['Mejor profesor en apoyo a la gestión de la calidad'],
        ])
        MiembroComision.objects.get_or_create(comision=c1, usuario=u['miembro_pgomez'])
        MiembroComision.objects.get_or_create(comision=c1, usuario=u['miembro_clpena'])
        comisiones['integral'] = c1

        c2 = Comision.objects.get_or_create(nombre='Formación de Pregrado', defaults={'jefe': u['jefe_comision_pregrado']})[0]
        c2.premios.set([
            premios['Mejor profesor a tiempo parcial'], premios['Mejor profesor en trabajo docente educativo y metodológico'],
            premios['Mejor profesor guía'], premios['Mejor profesor principal de año académico'],
            premios['Mejor profesor a tiempo completo en CUM-FUM'], premios['Mejor coordinador del colectivo de carrera (Jefe de carrera)'],
        ])
        MiembroComision.objects.get_or_create(comision=c2, usuario=u['jefe_area_agronomia'])
        MiembroComision.objects.get_or_create(comision=c2, usuario=u['jefe_depto_biologia'])
        MiembroComision.objects.get_or_create(comision=c2, usuario=u['miembro_pgomez'])
        comisiones['pregrado'] = c2

        return comisiones

    def _crear_propuestas(self, u, areas, premios, comisiones):
        fi = areas['Facultad de Informática']['obj']
        fi_is = areas['Facultad de Informática']['deptos']['Ingeniería de Software']
        fa = areas['Facultad de Agronomía']['obj']
        fa_bio = areas['Facultad de Agronomía']['deptos']['Biología']
        vrrpa = areas['Vicerrectoría Docente (VRRPA)']['obj']
        vrrpa_pregrado = areas['Vicerrectoría Docente (VRRPA)']['deptos']['Formación de Pregrado']

        def historial(p, usuario, accion, desc='', desde='', hasta=''):
            HistorialPropuesta.objects.create(propuesta=p, usuario=usuario, accion=accion, descripcion=desc, nivel_desde=desde, nivel_hasta=hasta)

        # 1. Pendiente de departamento
        p1 = Propuesta.objects.create(
            premio=premios['Mejor profesor a tiempo parcial'], creado_por=u['usuario_rmedina'],
            area=fi, departamento=fi_is, candidato_nombre='Rosa Medina Pérez', candidato_usuario=u['usuario_rmedina'],
            resumen='Propongo mi candidatura por los resultados obtenidos en la impartición de asignaturas como profesora a tiempo parcial durante el curso.',
            estado=EstadoPropuesta.PENDIENTE_DEPARTAMENTO, nivel_actual=NivelPropuesta.DEPARTAMENTO,
        )
        historial(p1, u['usuario_rmedina'], 'Creación de propuesta', 'Propuesta creada.', '', NivelPropuesta.DEPARTAMENTO)

        # 2. Pendiente de elevación a área
        p2 = Propuesta.objects.create(
            premio=premios['Mejor profesor joven (hasta 35 años)'], creado_por=u['jefe_depto_biologia'],
            area=fa, departamento=fa_bio, candidato_nombre='Luis Torres Mora', candidato_usuario=u['jefe_depto_biologia'],
            resumen='Excelente desempeño docente y científico en sus primeros años de carrera, con publicaciones y participación en proyectos de investigación.',
            estado=EstadoPropuesta.PENDIENTE_AREA, nivel_actual=NivelPropuesta.AREA,
        )
        historial(p2, u['jefe_depto_biologia'], 'Creación de propuesta', '', '', NivelPropuesta.DEPARTAMENTO)
        historial(p2, u['jefe_depto_biologia'], 'Elevar a Área', '', NivelPropuesta.DEPARTAMENTO, NivelPropuesta.AREA)

        # 3-6. En comisión: 4 candidatos para "Mejor profesor guía"
        candidatos_guia = [
            ('Ana García Ruiz', u['jefe_area_agronomia'], fa, fa_bio, 'Jefe de Área de Agronomía'),
            ('Pedro Gómez Castro', u['miembro_pgomez'], fi, fi_is, 'Jefe de Área de Informática'),
            ('Rosa Medina Pérez', u['usuario_rmedina'], fi, fi_is, 'Jefe de Área de Informática'),
            ('Carlos Vega Ramos', None, fa, fa_bio, 'Jefe de Área de FUM Moa'),
        ]
        for nombre, candidato_usuario, area, depto, proponente_desc in candidatos_guia:
            p = Propuesta.objects.create(
                premio=premios['Mejor profesor guía'], creado_por=u['jefe_area_agronomia'],
                area=area, departamento=depto, candidato_nombre=nombre, candidato_usuario=candidato_usuario,
                resumen=f'La comisión evaluó la propuesta de {nombre} para el premio Mejor Profesor Guía, considerando resultados '
                        'académicos, participación extracurricular y calidad del trabajo con los estudiantes.',
                estado=EstadoPropuesta.EN_COMISION, nivel_actual=NivelPropuesta.COMISION, comision=comisiones['pregrado'],
            )
            historial(p, u['jefe_area_agronomia'], 'Creación de propuesta', f'Propuesta creada por {proponente_desc}.', '', NivelPropuesta.DEPARTAMENTO)
            historial(p, u['jefe_area_agronomia'], 'Elevar a Área', '', NivelPropuesta.DEPARTAMENTO, NivelPropuesta.AREA)
            historial(p, u['jefe_area_agronomia'], 'Elevar a nivel Universidad / Comisión', '', NivelPropuesta.AREA, NivelPropuesta.COMISION)

        # 7. Aprobada + Ganador ya publicado (Mejor Departamento docente - Matemática, colectivo)
        p_mate = Propuesta.objects.create(
            premio=premios['Mejor Departamento docente'], creado_por=u['admin'],
            area=fi, departamento=None, candidato_nombre='Departamento de Matemática',
            resumen='El Departamento de Matemática de la Facultad de Informática mostró resultados sobresalientes en la formación de pregrado y el trabajo metodológico durante el curso.',
            estado=EstadoPropuesta.APROBADA, nivel_actual=NivelPropuesta.COMISION, comision=comisiones['integral'],
            seleccion_comision='premio', fundamentacion_comision='Resultados destacados en el trabajo metodológico e indicadores de calidad del colectivo.',
        )
        historial(p_mate, u['admin'], 'Creación de propuesta', '', '', NivelPropuesta.DEPARTAMENTO)
        historial(p_mate, u['admin'], 'Elevar a Área', '', NivelPropuesta.DEPARTAMENTO, NivelPropuesta.AREA)
        historial(p_mate, u['admin'], 'Elevar a nivel Universidad / Comisión', '', NivelPropuesta.AREA, NivelPropuesta.COMISION)
        historial(p_mate, u['jefe_comision_integral'], 'Propuesta de ganador por comisión', 'Seleccionado como premio.')
        historial(p_mate, u['gestor_global'], 'Aprobación final', 'Ganador aprobado y publicado en el landing page.')
        Ganador.objects.create(
            propuesta=p_mate, premio=p_mate.premio, persona_nombre=p_mate.candidato_nombre, persona_area='Facultad de Informática',
            fundamentacion=p_mate.fundamentacion_comision, tipo='premio', anio=p_mate.anio,
            aprobado_por=u['gestor_global'], fecha_aprobacion=timezone.now(), publicado=True,
        )

        # 8. Pendiente de departamento (María Soto)
        p8 = Propuesta.objects.create(
            premio=premios['Mejor coordinador del colectivo de carrera (Jefe de carrera)'], creado_por=u['usuario_msoto'],
            area=vrrpa, departamento=vrrpa_pregrado, candidato_nombre='María Soto López', candidato_usuario=u['usuario_msoto'],
            resumen='Gestión destacada al frente del colectivo de la carrera, con buenos resultados de retención y promoción.',
            estado=EstadoPropuesta.PENDIENTE_DEPARTAMENTO, nivel_actual=NivelPropuesta.DEPARTAMENTO,
        )
        historial(p8, u['usuario_msoto'], 'Creación de propuesta', '', '', NivelPropuesta.DEPARTAMENTO)

        # 9. Premio "por comisión" creado directamente (sin propuesta de área)
        p9 = Propuesta.objects.create(
            premio=premios['Mejor profesor en apoyo a la gestión de la calidad'], creado_por=u['jefe_comision_integral'],
            candidato_nombre='María Rodríguez López', resumen='Aporte sobresaliente al Sistema de Gestión de la Calidad de la universidad durante el proceso de acreditación.',
            estado=EstadoPropuesta.EN_COMISION, nivel_actual=NivelPropuesta.COMISION, comision=comisiones['integral'],
        )
        historial(p9, u['jefe_comision_integral'], 'Creación directa por comisión', 'Premio asignado por comisión (sin propuesta de área).', '', NivelPropuesta.COMISION)

    def _crear_ganadores_historicos(self, premios):
        anio_anterior = timezone.now().year - 1
        historicos = [
            (premios['Mejor profesor integralmente'], 'María Rodríguez López', 'Facultad de Informática', 'Dr.C.', 'Profesor Titular',
             'premio', 'Destacada trayectoria en docencia e investigación con más de 20 años en la institución.'),
            (premios['Mejor profesor joven (hasta 35 años)'], 'Juan Pablo Martínez', 'VRRPA', 'MSc.', 'Profesor Auxiliar',
             'reconocimiento', 'Resultados sobresalientes en sus primeros años como docente universitario.'),
            (premios['Mejor Facultad integralmente'], 'Facultad de Agronomía', '', '', '', 'premio', 'Resultados integrales sobresalientes durante el curso académico.'),
            (premios['Mejor trabajador no docente'], 'Carlos López Peña', 'Dirección de Recursos Humanos', '', '', 'premio', 'Desempeño ejemplar en la gestión de recursos humanos.'),
            (premios['Mejor profesor guía'], 'Ana García Ruiz', 'FUM Moa', 'MSc.', 'Profesor Auxiliar', 'premio', 'Excelente labor como guía de grupo, con un alto índice de retención y resultados académicos.'),
        ]
        for premio, nombre, area, cat_c, cat_d, tipo, fund in historicos:
            Ganador.objects.get_or_create(
                premio=premio, persona_nombre=nombre, anio=anio_anterior,
                defaults=dict(
                    persona_area=area, categoria_cientifica=cat_c, categoria_docente=cat_d,
                    tipo=tipo, fundamentacion=fund, publicado=True, fecha_aprobacion=timezone.now(),
                ),
            )
