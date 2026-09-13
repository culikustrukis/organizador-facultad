# Organizador Facultad · Student Planner

Aplicación web para gestionar tu cursada universitaria: materias, horarios con
detección de conflictos, tareas y exámenes. Interfaz basada en un diseño exportado
desde Google Stitch (tema **Academic Clarity**, Material 3).

## Requisitos

- Python 3.10+
- Node.js 18+ (solo para recompilar los estilos Tailwind, opcional)
- Una base de datos PostgreSQL alojada en **Supabase**

## Base de datos

La aplicación usa **PostgreSQL** alojado en **Supabase** como base de datos.
Todos los datos se guardan allí (usuarios, materias, clases, tareas y exámenes).

### Configurar `DATABASE_URL`

1. Creá un archivo `.env` copiando `.env.example`:
   ```
   copy .env.example .env
   ```
2. Completá `DATABASE_URL` con la cadena de conexión de tu proyecto Supabase:
   - Andá a **Supabase Dashboard** → tu proyecto → **Project Settings** → **Database**.
   - Copiá la cadena de conexión (formato SQLAlchemy / libpq), por ejemplo:
     ```
     DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres
     ```
   - Si tu proyecto exige SSL, agregá `?sslmode=require` al final, por ejemplo:
     ```
     DATABASE_URL=postgresql://postgres.xxxx:password@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require
     ```

   NUNCA subas el `.env` real a Git (ya está ignorado en `.gitignore`).

### Qué pasa si `DATABASE_URL` no está configurada

La aplicación no puede arrancar sin base de datos. Si `DATABASE_URL` falta o es
inválida, el servidor mostrará un error claro al iniciarse indicando que falta
configurarla. Revisá que el archivo `.env` exista y tenga la cadena correcta.

Si necesitás replicar los datos del proyecto original de SQLite (`database.db`)
en PostgreSQL, seguí las instrucciones de la sección **Migración de datos**.

## Instalación y arranque

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrí [http://127.0.0.1:5000](http://127.0.0.1:5000).

Las tablas se crean automáticamente al iniciar la primera vez (no se borran ni se
duplican datos en cada arranque). Si la base está vacía, se inserta un usuario
demo con datos de ejemplo:

- **Usuario demo:** `sofia`
- **Contraseña:** `demo1234`

## Migración de datos

Si ya tenías la app con SQLite (`database.db`) y querés llevar esos datos a
PostgreSQL conservando los IDs, ejecutá:

```
python migrar_sqlite_a_postgresql.py
```

El script:

- Crea las tablas si no existen.
- Copia todos los registros de `database.db` a PostgreSQL (usuarios, materias,
  clases, tareas y exámenes) **respetando los IDs originales** y las relaciones.
- No borra `database.db` (queda como respaldo) y no crea duplicados: si la base
  PostgreSQL ya tiene datos, aborta sin tocar nada.
- Deja las secuencias sincronizadas para que los próximos IDs no colisionen.

## Prueba de conexión

Podés verificar que la app llega a PostgreSQL con:

```
python -c "import db; db.init_db(); print('Conexión OK')"
```

Si la conexión falla, revisá `DATABASE_URL` y que la IP de tu entorno esté
permitida en Supabase (**Database** → **Connection pooling / Direct** → firewalls)
y que el password sea correcto.

## Configuración por variables de entorno

La app lee opcionalmente un archivo `.env` (ver `.env.example`).

| Variable               | Uso                                                                                          | Valor de ejemplo |
|------------------------|----------------------------------------------------------------------------------------------|------------------|
| `DATABASE_URL`         | Cadena de conexión PostgreSQL (Supabase). Obligatoria para arrancar.                          | `postgresql://...` |
| `SECRET_KEY`           | Firma las sesiones. Generarla con `python -c "import secrets; print(secrets.token_hex(32))"`  | clave aleatoria |
| `FLASK_DEBUG`          | `1` activa el debug server con recarga automática (solo desarrollo)                           | `0` |
| `SESSION_COOKIE_SECURE`| `1` envía la cookie de sesión solo por HTTPS (producción con SSL)                             | `1` |

## Despliegue en producción

La app es una aplicación WSGI estándar. El objeto se importa como `app:app`.

```
pip install -r requirements.txt
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

Recomendaciones:

- Definir `DATABASE_URL`, `SECRET_KEY` (aleatoria y larga), `SESSION_COOKIE_SECURE=1`
  si hay HTTPS y `FLASK_DEBUG=0`.
- La carpeta de uploads (`static/uploads`) debe ser escribible.
- Gunicorn no se instala en Windows; el `requirements.txt` lo excluye con un
  marcador de plataforma. Solo es necesario en el servidor.

## Recompilar estilos

Los estilos ya compilados están en `static/css/tailwind.css`. Si querés regenerarlos
después de editar los templates:

```
npm install
npm run build:css
```

Para desarrollo con recarga automática de estilos: `npm run watch:css`.

## Funcionalidades

- **Inicio** — resumen del día: próxima clase, carga semanal, próximo examen, entregas activas y mini horario semanal.
- **Mi horario** — calendario semanal (Lun a Vie) con vista por materia, detección de superposiciones y aviso de conflictos.
- **Materias** — alta/edición/baja con código, cátedra, modalidad, régimen, carga horaria, aula, comisión y color de identificación.
- **Tareas** — lista con filtros (pendientes, urgentes, completadas) y vista kanban; prioridades y modalidad de entrega.
- **Parciales** — exámenes agrupados por categoría (primeros, recuperatorios, finales) con cuenta regresiva.
- **Configuración** — foto de perfil, nombre y carrera, tema claro/oscuro y cierre de sesión.

## Estructura

```
app.py                      Rutas de páginas y API JSON
db.py                       Conexión PostgreSQL (psycopg), esquema y seed demo
migrar_sqlite_a_postgresql.py  Migración de database.db → PostgreSQL
utils.py                    Paleta de colores, conflictos, helpers de fechas
templates/                  Vistas Jinja2 (base + 7 páginas)
static/js/                  Interacción por página
static/css/                 tailwind.css (compilado) + style.css (tokens de tema)
src/input.css               Entrada de Tailwind
tailwind.config.js          Tema Academic Clarity + safelist de colores
```

La app es 100% local y offline salvo las fuentes de Google Fonts y la conexión a
Supabase (que sí requiere internet).