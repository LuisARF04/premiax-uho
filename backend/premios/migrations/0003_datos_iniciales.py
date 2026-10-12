from django.db import migrations

SECCIONES = [
    ('Principios Fundamentales', '🎯',
     'Reconocimiento del mérito, la excelencia y la dedicación de los trabajadores universitarios en todas sus dimensiones.'),
    ('Niveles de Incentivos', '🏅',
     'Premios individuales y colectivos, docentes y no docentes, con reconocimientos en diferentes categorías.'),
    ('Procedimiento de Selección', '📑',
     'Proceso transparente desde propuestas de departamento, hasta aprobación por la Rectoría y el Consejo de Dirección.'),
]


def cargar(apps, schema_editor):
    Etapa = apps.get_model('premios', 'EtapaProceso')
    Etapa.objects.filter(nombre__icontains='convocatoria').update(es_convocatoria=True)
    Seccion = apps.get_model('premios', 'ReglamentoSeccion')
    if not Seccion.objects.exists():
        for i, (titulo, icono, contenido) in enumerate(SECCIONES, start=1):
            Seccion.objects.create(titulo=titulo, icono=icono, contenido=contenido, orden=i)


class Migration(migrations.Migration):
    dependencies = [('premios', '0002_reglamentoseccion_etapaproceso_es_convocatoria')]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]
