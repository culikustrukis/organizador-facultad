# Organizador Facultad · Student Planner

Aplicación web local para gestionar tu cursada universitaria: materias, horarios con
detección de conflictos, tareas y exámenes. Interfaz basada en un diseño exportado
desde Google Stitch (tema **Academic Clarity**, Material 3).

## Requisitos

- Python 3.10+
- Node.js 18+ (solo para recompilar los estilos Tailwind, opcional)

## Instalación y arranque

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrí [http://127.0.0.1:5000](http://127.0.0.1:5000).

La base SQLite se crea automáticamente en `database.db` con datos de demostración la
primera vez:

- **Usuario demo:** `sofia`
- **Contraseña:** `demo1234`

## Configuración por variables de entorno

La app lee opcionalmente un archivo `.env` (ver `.env.example`). En desarrollo no es
necesario configurar nada; los valores por defecto son seguros para localhost.

| Variable               | Uso                                                                                          | Default local |
|------------------------|----------------------------------------------------------------------------------------------|---------------|
| `SECRET_KEY`           | Firma las sesiones. En producción generarla con `python -c "import secrets; print(secrets.token_hex(32))"` | clave fija solo de desarrollo |
| `FLASK_DEBUG`          | `1` activa el debug server con recarga automática (solo desarrollo)                          | `0`           |
| `SESSION_COOKIE_SECURE`| `1` envía la cookie de sesión solo por HTTPS (producción con SSL)                            | `0`           |
| `DATABASE_PATH`        | Ruta del archivo SQLite; útil en el servidor para usar almacenamiento persistente            | `database.db` junto al código |

## Despliegue en producción

La app es una aplicación WSGI estándar. El objeto se importa como `app:app`.

```
pip install -r requirements.txt
gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

Recomendaciones:

- Definir `SECRET_KEY` (aleatoria y larga), `SESSION_COOKIE_SECURE=1` si hay HTTPS y
  `FLASK_DEBUG=0`.
- Apuntar `DATABASE_PATH` a un volumen persistente: la base debe vivir fuera del código
  porque muchos hosts reemplazan el filesystem en cada despliegue. La carpeta de uploads
  (`static/uploads`) también debe ser escribible.
- El modo debug de desarrollo (`debug=True`) ya no es obligatorio: la app arranca
  correctamente con debug apagado. En producción ejecutar con gunicorn (u otro servidor
  WSGI como waitress) y no usar `python app.py` para servir tráfico real.
- Gunicorn no se instala en Windows; el `requirements.txt` lo excluye con un marcador de
  plataforma. Solo es necesario en el servidor.

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
app.py              Rutas de páginas y API JSON
db.py               Esquema SQLite y datos de demostración
utils.py            Paleta de colores, conflictos, helpers de fechas
templates/          Vistas Jinja2 (base + 7 páginas)
static/js/          Interacción por página
static/css/         tollwind.css (compilado) + style.css (tokens de tema)
src/input.css       Entrada de Tailwind
tailwind.config.js  Tema Academic Clarity + safelist de colores
```

La app es 100% local y offline salvo las fuentes de Google Fonts.