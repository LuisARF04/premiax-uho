# PREMIAX-UHO — Sistema de Gestión de los Premios del Rector

Implementación funcional del sistema descrito en el Documento de Requerimientos (ERS) de la
Universidad de Holguín: backend Django REST + frontend React, con base de datos, autenticación
(simulando AGA_AUTH) y flujo completo de propuestas, comisiones y aprobación de premios.

> **Alcance de esta versión:** app full-stack funcional para ejecutarse en local. La integración
> real con AGA_AUTH/SIGENU/ASSET, Docker/CI-CD y despliegue en el entorno UHO quedan fuera de
> este alcance y se simulan (ver sección "Simulaciones" más abajo).

## Estructura

```
Premiax UHO/
├── backend/     Django + Django REST Framework (API + base de datos)
└── frontend/    React (Vite) — landing pública + panel de administración
```

## Requisitos

- Python 3.11+ (probado con 3.14)
- Node.js 18+ (probado con 24)

## Puesta en marcha — Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data       # carga datos de ejemplo (áreas, premios, usuarios, propuestas...)
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/api/` y el admin de Django en `/admin/`.

### Usuarios de prueba

Todos con contraseña **`Premiax2025!`**:

| Usuario       | Rol                                   |
|---------------|----------------------------------------|
| `cperez`      | Superadmin                              |
| `mrodriguez`  | Admin                                   |
| `jpmartinez`  | Gestor Global                           |
| `rfuentes`    | Jefe de Comisión (Formación de Pregrado)|
| `vperez`      | Jefe de Comisión (Integrales y Gestión) |
| `agarcia`     | Jefe de Área (Agronomía)                |
| `ltorres`     | Jefe de Departamento (Biología)         |
| `pgomez`      | Miembro de Comisión                     |
| `rmedina`     | Usuario (trabajador)                    |
| `msoto`       | Usuario (trabajador)                    |

El superusuario de Django es `root` / `Premiax2025!` (acceso a `/admin/`).

## Puesta en marcha — Frontend

```bash
cd frontend
npm install
npm run dev
```

La app queda disponible en `http://localhost:5173/`. La variable `VITE_API_URL` en `frontend/.env`
apunta al backend (`http://127.0.0.1:8000/api` por defecto).

## Simulaciones respecto al ERS

Para poder ejecutarse fuera de la red de la UHO, esta versión simula lo siguiente (con código
señalado en comentarios donde aplica):

- **AGA_AUTH**: el login valida usuario/contraseña contra la base de datos local en vez de
  redirigir a `auth.uho.edu.cu`. La respuesta y el flujo (rechazo de estudiantes, registro
  automático, selección de área/departamento en el primer acceso) siguen el mismo contrato.
- **SIGENU / ASSET**: no se consumen; los datos de usuario se gestionan directamente en
  PREMIAX-UHO como si ya hubieran sido sincronizados.
- **Envío de correos**: se usa el backend de consola de Django (`EmailBackend` que imprime el
  correo en la terminal del backend) en vez de un servidor SMTP real.
- **Docker / CI-CD**: no incluidos; el proyecto corre directamente con `runserver` / `vite dev`.

## Módulos implementados (según el ERS)

- Landing page pública: reglamento, categorías y premios, galería de premiados por año,
  calendario del proceso, botón de convocatoria condicionado a la etapa activa.
- Autenticación simulando AGA_AUTH + selección de área/departamento en primer acceso.
- RBAC con los 8 roles del ERS (superadmin → usuario) y jerarquía de privilegios.
- CRUD de: categorías de premio, premios, etapas del proceso, áreas y departamentos
  (con importación CSV), nomencladores (categorías docentes/científicas, cargos, carreras).
- Flujo completo de propuestas: creación → revisión de departamento → revisión de área →
  asignación/reasignación de comisión → propuesta de ganadores → aprobación final, con
  historial completo por propuesta.
- Premios "asignados por comisión" (sin propuesta de área previa).
- Gestión de comisiones (jefe, miembros, premios asignados) y panel de comisión.
- Registro retroactivo de ganadores para años anteriores.
- Notificaciones internas (+ envío de correo simulado) en cada evento relevante del flujo.
- Panel de usuarios inactivos.
- Dashboard principal y dashboard estadístico (propuestas por área/categoría, participación).
- Logs de auditoría de toda acción que modifica datos, más acciones de negocio detalladas.
- Perfil de usuario con preferencias de notificación y visibilidad de foto en el landing.

## Notas de seguridad para este demo

- `SECRET_KEY` y `DEBUG=True` están configurados para desarrollo local; deben cambiarse antes
  de cualquier despliegue real.
- Los tokens JWT (access) expiran en 8 horas, según RNF-006.
- CORS está abierto (`CORS_ALLOW_ALL_ORIGINS=True`) para simplificar el desarrollo local; debe
  restringirse a los orígenes reales antes de producción.
