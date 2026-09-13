import datetime
import json
import os
import uuid

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import db as database
from utils import (
    CATEGORIAS_EXAMEN,
    COLORS,
    DIAS,
    MODALIDADES,
    PRIORIDADES,
    REGIMENES,
    TIPOS_CLASE,
    detect_conflicts,
    dias_restantes,
    fecha_humana,
    primeros_nombres,
    semana_actual,
    to_minutes,
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "organizador-facultad-dev-key")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def load_user():
    g.user = None
    user_id = session.get("user_id")
    if user_id:
        g.user = database.get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    def wrapped(*args, **kwargs):
        if not g.user:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


@app.teardown_appcontext
def teardown(_):
    database.close_db()


def get_clases_with_materia():
    db = database.get_db()
    rows = db.execute(
        """
        SELECT c.*, m.nombre AS materia_nombre, m.codigo AS materia_codigo, m.color AS materia_color,
               m.profesor AS materia_profesor
        FROM clases c JOIN materias m ON m.id = c.materia_id
        WHERE c.user_id = ? ORDER BY c.dia, c.hora_inicio
        """,
        (g.user["id"],),
    ).fetchall()
    return [dict(r) for r in rows]


def enrich_clase(clase):
    clase["color"] = COLORS.get(clase.get("materia_color") or "indigo", COLORS["indigo"])
    clase["tipo_label"] = TIPOS_CLASE.get(clase.get("tipo") or "teorica", "Clase")
    clase["hora_txt"] = f"{clase['hora_inicio']} - {clase['hora_fin']}"
    return clase


def materias_del_usuario():
    db = database.get_db()
    rows = db.execute(
        "SELECT * FROM materias WHERE user_id = ? ORDER BY nombre",
        (g.user["id"],),
    ).fetchall()
    materias = []
    for r in rows:
        m = dict(r)
        m["color"] = COLORS.get(m.get("color") or "indigo", COLORS["indigo"])
        m["modalidad_label"] = MODALIDADES.get(m.get("modalidad"), m.get("modalidad", ""))
        m["regimen_label"] = REGIMENES.get(m.get("regimen"), m.get("regimen", ""))
        materias.append(m)
    return materias


def clases_del_usuario():
    rows = get_clases_with_materia()
    return [enrich_clase(c) for c in rows]


def tareas_del_usuario():
    db = database.get_db()
    rows = db.execute(
        """
        SELECT t.*, m.nombre AS materia_nombre, m.color AS materia_color
        FROM tareas t LEFT JOIN materias m ON m.id = t.materia_id
        WHERE t.user_id = ? ORDER BY
            CASE WHEN t.estado = 'pendiente' THEN 0 ELSE 1 END,
            t.fecha_limite ASC
        """,
        (g.user["id"],),
    ).fetchall()
    tareas = []
    for r in rows:
        t = dict(r)
        t["color"] = COLORS.get(t.get("materia_color") or "indigo", COLORS["indigo"])
        t["prioridad_label"] = PRIORIDADES.get(t.get("prioridad"), t.get("prioridad", "media"))
        t["vencida"] = False
        t["para_hoy"] = False
        if t.get("fecha_limite") and t["estado"] == "pendiente":
            try:
                dt = datetime.datetime.strptime(t["fecha_limite"], "%Y-%m-%dT%H:%M")
                hoy = datetime.datetime.now()
                t["fecha_display"] = dt.strftime("%d/%m %H:%M")
                t["fecha_corta"] = dt.strftime("%a %d/%m")
                t["vencida"] = dt < hoy
                t["para_hoy"] = dt.date() == hoy.date()
            except ValueError:
                t["fecha_display"] = t["fecha_limite"]
                t["fecha_corta"] = t["fecha_limite"]
        else:
            t["fecha_display"] = ""
            t["fecha_corta"] = ""
        tareas.append(t)
    return tareas


def examenes_del_usuario():
    db = database.get_db()
    rows = db.execute(
        """
        SELECT e.*, m.nombre AS materia_nombre, m.codigo AS materia_codigo, m.color AS materia_color
        FROM examenes e LEFT JOIN materias m ON m.id = e.materia_id
        WHERE e.user_id = ? ORDER BY e.fecha, e.hora
        """,
        (g.user["id"],),
    ).fetchall()
    examenes = []
    for r in rows:
        e = dict(r)
        e["color"] = COLORS.get(e.get("materia_color") or "indigo", COLORS["indigo"])
        e["categoria_label"] = CATEGORIAS_EXAMEN.get(e.get("categoria"), e.get("categoria", "Parcial"))
        e["mes"], e["dia"] = fecha_humana(e.get("fecha"))
        e["dias_restantes"] = dias_restantes(e.get("fecha"))
        examenes.append(e)
    return examenes


@app.context_processor
def inject_globals():
    def pending_count():
        if not g.user:
            return 0
        return database.get_db().execute(
            "SELECT COUNT(*) AS c FROM tareas WHERE user_id = ? AND estado = 'pendiente'",
            (g.user["id"],),
        ).fetchone()["c"]

    def exam_count():
        if not g.user:
            return 0
        hoy = datetime.date.today().isoformat()
        return database.get_db().execute(
            "SELECT COUNT(*) AS c FROM examenes WHERE user_id = ? AND fecha >= ?",
            (g.user["id"], hoy),
        ).fetchone()["c"]

    return {
        "current_user": g.user,
        "COLORS": COLORS,
        "DIAS": DIAS,
        "pending_count": pending_count() if g.user else 0,
        "exam_count": exam_count() if g.user else 0,
    }


@app.route("/")
def index():
    if g.user:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    row = database.get_db().execute(
        "SELECT * FROM users WHERE username = ? OR email = ?", (username, username)
    ).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"ok": False, "message": "Usuario o contraseña incorrectos."}), 401
    session.clear()
    session["user_id"] = row["id"]
    return jsonify({"ok": True, "redirect": url_for("dashboard")})


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"ok": False, "message": "Completá usuario, nombre y contraseña."}), 400
    if len(password) < 6:
        return jsonify({"ok": False, "message": "La contraseña debe tener al menos 6 caracteres."}), 400
    db = database.get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email)).fetchone()
    if existing:
        return jsonify({"ok": False, "message": "Ese usuario o correo ya está registrado."}), 409
    cur = db.execute(
        "INSERT INTO users (username, password_hash, full_name, email, carrera) VALUES (?,?,?,?,?)",
        (username, generate_password_hash(password), full_name or username, email, "Licenciatura en Sistemas"),
    )
    db.commit()
    session.clear()
    session["user_id"] = cur.lastrowid
    return jsonify({"ok": True, "redirect": url_for("dashboard")})


@app.route("/dashboard")
@login_required
def dashboard():
    db = database.get_db()
    hoy = datetime.date.today()
    hoy_idx = hoy.weekday()

    materias = materias_del_usuario()
    clases = clases_del_usuario()
    tareas = tareas_del_usuario()
    examenes = examenes_del_usuario()

    materias_count = len(materias)
    horas = sum(m.get("horas_semana") or 0 for m in materias)
    creditos = materias_count * 4

    clases_hoy = [c for c in clases if c["dia"] == hoy_idx]
    ahora = datetime.datetime.now().time()
    proxima_clase = None
    for c in classes_today_sorted(clases_hoy, ahora):
        if to_minutes(c["hora_inicio"]) > to_minutes(ahora.strftime("%H:%M")):
            proxima_clase = c
            break
    if not proxima_clase and clases_hoy:
        proxima_clase = clases_hoy[0]

    pendientes = [t for t in tareas if t["estado"] == "pendiente"]
    para_hoy = [t for t in pendientes if t.get("para_hoy") or t.get("vencida")]
    prox_examen = min(examenes, key=lambda e: (e["fecha"], e["hora"])) if examenes else None
    proximos_examenes = [e for e in sorted(examenes, key=lambda e: (e["fecha"], e["hora"])) if (e.get("dias_restantes") or 0) >= 0][:3]

    horas_teoricas = 0
    horas_practicas = 0
    for c in clases:
        dur = to_minutes(c["hora_fin"]) - to_minutes(c["hora_inicio"])
        if (c.get("tipo") or "teorica").startswith("teor"):
            horas_teoricas += dur / 60
        else:
            horas_practicas += dur / 60
    horas_teoricas = int(horas_teoricas) if horas_teoricas == int(horas_teoricas) else round(horas_teoricas, 1)
    horas_practicas = int(horas_practicas) if horas_practicas == int(horas_practicas) else round(horas_practicas, 1)

    if proxima_clase:
        inicio_min = to_minutes(proxima_clase["hora_inicio"])
        diff = inicio_min - (ahora.hour * 60 + ahora.minute)
        if diff <= 0:
            proxima_clase["chip"] = "Comenzó"
            proxima_clase["chip_clase"] = "bg-surface-container text-primary"
        elif diff < 60:
            proxima_clase["chip"] = f"En {diff} min"
            proxima_clase["chip_clase"] = "bg-surface-container text-primary font-semibold animate-pulse"
        else:
            proxima_clase["chip"] = f"En {diff // 60} h"
            proxima_clase["chip_clase"] = "bg-surface-container text-primary font-semibold animate-pulse"

    por_dia = {}
    for c in clases:
        por_dia.setdefault(c["dia"], []).append(c)

    semana = semana_actual()
    semana_labels = [
        {"idx": i, "nombre": DIAS[i][0], "corto": DIAS[i][1], "numero": semana[i].day, "hoy": i == hoy_idx}
        for i in range(5)
    ]

    return render_template(
        "dashboard.html",
        active="inicio",
        add_link=url_for("tareas"),
        hoy_iso=hoy.isoformat(),
        hoy_idx=hoy_idx,
        hoy_idioma_nombre=DIAS[hoy_idx][0],
        hoy_corto=DIAS[hoy_idx][1],
        materias_count=materias_count,
        materias=materias,
        horas=horas,
        horas_teoricas=horas_teoricas,
        horas_practicas=horas_practicas,
        creditos=creditos,
        clases_hoy=clases_hoy,
        proxima_clase=proxima_clase,
        prox_examen=prox_examen,
        proximos_examenes=proximos_examenes,
        total_pendientes=len(pendientes),
        para_hoy=para_hoy,
        por_dia=por_dia,
        semana_labels=semana_labels,
        tareas_inmediatas=pendientes[:3],
        tareas_count=len(pendientes),
    )


def classes_today_sorted(clases, ahora):
    now_min = ahora.hour * 60 + ahora.minute
    return sorted(clases, key=lambda c: abs(to_minutes(c["hora_inicio"]) - now_min))


@app.route("/horario")
@login_required
def horario():
    clases = clases_del_usuario()
    por_dia = {}
    for c in clases:
        por_dia.setdefault(c["dia"], []).append(c)

    total_horas = 0
    for c in clases:
        total_horas += to_minutes(c["hora_fin"]) - to_minutes(c["hora_inicio"])
    total_horas = round(total_horas / 60, 1)
    if total_horas == int(total_horas):
        total_horas = int(total_horas)

    conflicts, conflicted_ids = detect_conflicts(clases)
    hoy_idx = datetime.date.today().weekday()

    lista_materias_aux = materias_del_usuario()
    materias_grid = []
    for m in lista_materias_aux:
        mate_clases = [c for c in clases if c["materia_id"] == m["id"]]
        hrs = sum((to_minutes(c["hora_fin"]) - to_minutes(c["hora_inicio"])) for c in mate_clases) / 60
        hrs = int(hrs) if hrs == int(hrs) else hrs
        materias_grid.append(
            {
                "materia": m,
                "clases": mate_clases,
                "horas": hrs,
                "cant": len(mate_clases),
            }
        )

    dias = []
    for i in range(5):
        dias.append(
            {
                "idx": i,
                "nombre": DIAS[i][0],
                "corto": DIAS[i][1],
                "es_hoy": i == hoy_idx,
                "clases": por_dia.get(i, []),
                "total_min": sum(to_minutes(c["hora_fin"]) - to_minutes(c["hora_inicio"]) for c in por_dia.get(i, [])),
            }
        )

    return render_template(
        "horario.html",
        active="mi-horario",
        add_link="#modal-clase",
        dias=dias,
        total_horas=total_horas,
        aviso="Cursada regular del primer cuatrimestre",
        conflicts=conflicts,
        conflicted_ids=conflicted_ids,
        materias_grid=materias_grid,
        materias_select=lista_materias_aux,
        tipos_clase=[{"value": k, "label": v} for k, v in TIPOS_CLASE.items()],
        clases_json=json.dumps(
            [
                {
                    "id": c["id"],
                    "materia_id": c["materia_id"],
                    "dia": c["dia"],
                    "hora_inicio": c["hora_inicio"],
                    "hora_fin": c["hora_fin"],
                    "tipo": c["tipo"],
                    "aula": c["aula"],
                }
                for c in clases
            ],
            ensure_ascii=False,
        ),
    )


@app.route("/materias")
@login_required
def materias():
    db = database.get_db()
    materias_list = materias_del_usuario()
    examenes = examenes_del_usuario()
    prox_examen = min(examenes, key=lambda e: (e["fecha"], e["hora"])) if examenes else None
    promocionales = sum(1 for m in materias_list if m["regimen"] in ("promocionable", "promocional"))
    total_horas = sum(m.get("horas_semana") or 0 for m in materias_list)

    return render_template(
        "materias.html",
        active="materias",
        add_link="#modal-materia",
        materias=materias_list,
        total_horas=total_horas,
        promocionales=promocionales,
        prox_examen=prox_examen,
        materias_json=json.dumps(
            [
                {
                    "id": m["id"],
                    "codigo": m["codigo"],
                    "nombre": m["nombre"],
                    "profesor": m["profesor"],
                    "modalidad": m["modalidad"],
                    "horas_semana": m["horas_semana"],
                    "regimen": m["regimen"],
                    "aula": m["aula"],
                    "comision": m["comision"],
                    "color": m["color"],
                }
                for m in materias_list
            ],
            ensure_ascii=False,
        ),
    )


@app.route("/tareas")
@login_required
def tareas():
    tareas_list = tareas_del_usuario()
    pendientes = [t for t in tareas_list if t["estado"] == "pendiente"]
    urgente_count = sum(1 for t in pendientes if t["prioridad"] == "alta" or t.get("para_hoy") or t.get("vencida"))
    vencieron_count = sum(1 for t in pendientes if t.get("vencida"))

    return render_template(
        "tareas.html",
        active="tareas",
        add_link="#modal-tarea",
        tareas=tareas_list,
        pendientes_count=len(pendientes),
        urgente_count=urgente_count,
        vencieron_count=vencieron_count,
        materias_select=materias_del_usuario(),
        tareas_json=json.dumps(
            [
                {
                    "id": t["id"],
                    "titulo": t["titulo"],
                    "materia_id": t["materia_id"],
                    "fecha_limite": t["fecha_limite"],
                    "prioridad": t["prioridad"],
                    "tipo_entrega": t["tipo_entrega"],
                    "descripcion": t["descripcion"],
                    "estado": t["estado"],
                }
                for t in tareas_list
            ],
            ensure_ascii=False,
        ),
    )


@app.route("/parciales")
@login_required
def parciales():
    examenes = examenes_del_usuario()
    counts = {"todos": len(examenes), "primeros": 0, "recuperatorios": 0, "finales": 0}
    for e in examenes:
        if e["categoria"] in counts:
            counts[e["categoria"]] += 1

    return render_template(
        "parciales.html",
        active="parciales",
        add_link="#modal-examen",
        examenes=examenes,
        counts=counts,
        materias_select=materias_del_usuario(),
        examenes_json=json.dumps(
            [
                {
                    "id": e["id"],
                    "materia_id": e["materia_id"],
                    "nombre": e["nombre"],
                    "categoria": e["categoria"],
                    "fecha": e["fecha"],
                    "hora": e["hora"],
                    "aula": e["aula"],
                }
                for e in examenes
            ],
            ensure_ascii=False,
        ),
    )


@app.route("/configuracion")
@login_required
def configuracion():
    return render_template("configuracion.html", active="configuracion")


def body_json():
    return request.get_json(silent=True) or {}


def color_auto():
    db = database.get_db()
    rows = db.execute(
        "SELECT color, COUNT(*) AS n FROM materias WHERE user_id = ? AND color != '' GROUP BY color",
        (g.user["id"],),
    ).fetchall()
    usados = {r["color"]: r["n"] for r in rows}
    orden = list(COLORS.keys())
    if not orden:
        return "indigo"
    return min(orden, key=lambda k: (usados.get(k, 0), orden.index(k)))


@app.route("/api/materias", methods=["POST"])
@login_required
def api_materia_create():
    data = body_json()
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return jsonify({"ok": False, "message": "El nombre de la materia es obligatorio."}), 400
    db = database.get_db()
    cur = db.execute(
        """INSERT INTO materias (user_id, codigo, nombre, profesor, modalidad, horas_semana, aula, comision, color, regimen)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (
            g.user["id"],
            (data.get("codigo") or "").strip().upper(),
            nombre,
            (data.get("profesor") or "").strip(),
            data.get("modalidad") or "presencial",
            int(data.get("horas_semana") or 0),
            (data.get("aula") or "").strip(),
            (data.get("comision") or "").strip(),
            color_auto(),
            data.get("regimen") or "promocionable",
        ),
    )
    db.commit()
    return jsonify({"ok": True, "id": cur.lastrowid, "redirect": url_for("materias")})


@app.route("/api/materias/<int:materia_id>", methods=["PUT", "DELETE"])
@login_required
def api_materia(materia_id):
    db = database.get_db()
    existing = db.execute(
        "SELECT id FROM materias WHERE id = ? AND user_id = ?", (materia_id, g.user["id"])
    ).fetchone()
    if not existing:
        return jsonify({"ok": False, "message": "Materia no encontrada."}), 404
    if request.method == "DELETE":
        db.execute("DELETE FROM materias WHERE id = ?", (materia_id,))
        db.commit()
        return jsonify({"ok": True})
    data = body_json()
    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        return jsonify({"ok": False, "message": "El nombre de la materia es obligatorio."}), 400
    db.execute(
        """UPDATE materias SET codigo = ?, nombre = ?, profesor = ?, modalidad = ?, horas_semana = ?,
           aula = ?, comision = ?, regimen = ? WHERE id = ?""",
        (
            (data.get("codigo") or "").strip().upper(),
            nombre,
            (data.get("profesor") or "").strip(),
            data.get("modalidad") or "presencial",
            int(data.get("horas_semana") or 0),
            (data.get("aula") or "").strip(),
            (data.get("comision") or "").strip(),
            data.get("regimen") or "promocionable",
            materia_id,
        ),
    )
    db.commit()
    return jsonify({"ok": True})


def check_clase_conflict(materia_id, dia, hora_inicio, hora_fin, ignore_id=None):
    db = database.get_db()
    rows = db.execute(
        "SELECT id FROM clases WHERE user_id = ? AND dia = ?",
        (g.user["id"], dia),
    ).fetchall()
    conflicts = []
    for row in rows:
        if ignore_id is not None and row["id"] == ignore_id:
            continue
        c = db.execute(
            """SELECT c.*, m.nombre AS materia_nombre FROM clases c JOIN materias m ON m.id = c.materia_id WHERE c.id = ?""",
            (row["id"],),
        ).fetchone()
        if c and to_minutes(hora_inicio) < to_minutes(c["hora_fin"]) and to_minutes(hora_fin) > to_minutes(c["hora_inicio"]):
            conflicts.append(
                {
                    "id_otra": c["id"],
                    "materia": c["materia_nombre"],
                    "horario": f"{c['hora_inicio']} - {c['hora_fin']}",
                    "dia": DIAS[dia][0] if 0 <= dia < 7 else "?",
                }
            )
    return conflicts


@app.route("/api/clases", methods=["POST"])
@login_required
def api_clase_create():
    data = body_json()
    dia = int(data.get("dia") or 0)
    hora_inicio = (data.get("hora_inicio") or "08:00").strip()
    hora_fin = (data.get("hora_fin") or "09:00").strip()
    materia_id = int(data.get("materia_id") or 0)
    if not materia_id or not hora_inicio or not hora_fin:
        return jsonify({"ok": False, "message": "Completá materia y horario."}), 400
    if to_minutes(hora_fin) <= to_minutes(hora_inicio):
        return jsonify({"ok": False, "message": "La hora de fin debe ser posterior al inicio."}), 400
    if not (0 <= dia <= 6):
        return jsonify({"ok": False, "message": "Día inválido."}), 400
    conflicts = check_clase_conflict(materia_id, dia, hora_inicio, hora_fin)
    db = database.get_db()
    cur = db.execute(
        "INSERT INTO clases (user_id, materia_id, dia, hora_inicio, hora_fin, tipo, aula) VALUES (?,?,?,?,?,?,?)",
        (g.user["id"], materia_id, dia, hora_inicio, hora_fin, data.get("tipo") or "teorica", (data.get("aula") or "").strip()),
    )
    db.commit()
    return jsonify({"ok": True, "id": cur.lastrowid, "conflicts": conflicts})


@app.route("/api/clases/<int:clase_id>", methods=["PUT", "DELETE"])
@login_required
def api_clase(clase_id):
    db = database.get_db()
    existing = db.execute(
        "SELECT id FROM clases WHERE id = ? AND user_id = ?", (clase_id, g.user["id"])
    ).fetchone()
    if not existing:
        return jsonify({"ok": False, "message": "Clase no encontrada."}), 404
    if request.method == "DELETE":
        db.execute("DELETE FROM clases WHERE id = ?", (clase_id,))
        db.commit()
        return jsonify({"ok": True})
    data = body_json()
    dia = int(data.get("dia") or 0)
    hora_inicio = (data.get("hora_inicio") or "08:00").strip()
    hora_fin = (data.get("hora_fin") or "09:00").strip()
    materia_id = int(data.get("materia_id") or 0)
    if not materia_id or to_minutes(hora_fin) <= to_minutes(hora_inicio):
        return jsonify({"ok": False, "message": "Datos de horario inválidos."}), 400
    conflicts = check_clase_conflict(materia_id, dia, hora_inicio, hora_fin, ignore_id=clase_id)
    db.execute(
        "UPDATE clases SET materia_id = ?, dia = ?, hora_inicio = ?, hora_fin = ?, tipo = ?, aula = ? WHERE id = ?",
        (materia_id, dia, hora_inicio, hora_fin, data.get("tipo") or "teorica", (data.get("aula") or "").strip(), clase_id),
    )
    db.commit()
    return jsonify({"ok": True, "conflicts": conflicts})


@app.route("/api/tareas", methods=["POST"])
@login_required
def api_tarea_create():
    data = body_json()
    titulo = (data.get("titulo") or "").strip()
    if not titulo:
        return jsonify({"ok": False, "message": "El título de la tarea es obligatorio."}), 400
    db = database.get_db()
    cur = db.execute(
        """INSERT INTO tareas (user_id, materia_id, titulo, descripcion, fecha_limite, prioridad, tipo_entrega, estado)
           VALUES (?,?,?,?,?,?,?, 'pendiente')""",
        (
            g.user["id"],
            int(data.get("materia_id") or 0) or None,
            titulo,
            (data.get("descripcion") or "").strip(),
            (data.get("fecha_limite") or "").strip(),
            data.get("prioridad") or "media",
            data.get("tipo_entrega") or "individual",
        ),
    )
    db.commit()
    return jsonify({"ok": True, "id": cur.lastrowid, "redirect": url_for("tareas")})


@app.route("/api/tareas/<int:tarea_id>", methods=["PUT", "DELETE"])
@login_required
def api_tarea(tarea_id):
    db = database.get_db()
    row = db.execute(
        "SELECT * FROM tareas WHERE id = ? AND user_id = ?", (tarea_id, g.user["id"])
    ).fetchone()
    if not row:
        return jsonify({"ok": False, "message": "Tarea no encontrada."}), 404
    if request.method == "DELETE":
        db.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
        db.commit()
        return jsonify({"ok": True})
    data = body_json()

    def val(key):
        return data[key] if key in data else row[key]

    db.execute(
        """UPDATE tareas SET titulo = ?, descripcion = ?, fecha_limite = ?, prioridad = ?,
           tipo_entrega = ?, estado = ?, materia_id = ? WHERE id = ?""",
        (
            (val("titulo") or "").strip(),
            (val("descripcion") or "").strip(),
            (val("fecha_limite") or "").strip(),
            val("prioridad") or "media",
            val("tipo_entrega") or "individual",
            val("estado") or "pendiente",
            int(val("materia_id") or 0) or None,
            tarea_id,
        ),
    )
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/examenes", methods=["POST"])
@login_required
def api_examen_create():
    data = body_json()
    fecha = (data.get("fecha") or "").strip()
    if not fecha:
        return jsonify({"ok": False, "message": "La fecha del examen es obligatoria."}), 400
    db = database.get_db()
    cur = db.execute(
        "INSERT INTO examenes (user_id, materia_id, nombre, categoria, fecha, hora, aula) VALUES (?,?,?,?,?,?,?)",
        (
            g.user["id"],
            int(data.get("materia_id") or 0) or None,
            (data.get("nombre") or "Parcial").strip(),
            data.get("categoria") or "primeros",
            fecha,
            (data.get("hora") or "08:00").strip(),
            (data.get("aula") or "").strip(),
        ),
    )
    db.commit()
    return jsonify({"ok": True, "id": cur.lastrowid, "redirect": url_for("parciales")})


@app.route("/api/examenes/<int:examen_id>", methods=["DELETE", "PUT"])
@login_required
def api_examen(examen_id):
    db = database.get_db()
    existing = db.execute(
        "SELECT id FROM examenes WHERE id = ? AND user_id = ?", (examen_id, g.user["id"])
    ).fetchone()
    if not existing:
        return jsonify({"ok": False, "message": "Examen no encontrado."}), 404
    if request.method == "DELETE":
        db.execute("DELETE FROM examenes WHERE id = ?", (examen_id,))
        db.commit()
        return jsonify({"ok": True})
    data = body_json()
    db.execute(
        "UPDATE examenes SET materia_id = ?, nombre = ?, categoria = ?, fecha = ?, hora = ?, aula = ? WHERE id = ?",
        (
            int(data.get("materia_id") or 0) or None,
            (data.get("nombre") or "Parcial").strip(),
            data.get("categoria") or "primeros",
            (data.get("fecha") or "").strip(),
            (data.get("hora") or "08:00").strip(),
            (data.get("aula") or "").strip(),
            examen_id,
        ),
    )
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/perfil", methods=["POST"])
@login_required
def api_perfil():
    data = body_json()
    db = database.get_db()
    full_name = (data.get("full_name") or g.user["full_name"] or "").strip()
    carrera = (data.get("carrera") or g.user["carrera"] or "").strip()
    db.execute("UPDATE users SET full_name = ?, carrera = ? WHERE id = ?", (full_name, carrera, g.user["id"]))
    db.commit()
    return jsonify({"ok": True, "message": "Cambios guardados."})


@app.route("/api/tema", methods=["POST"])
@login_required
def api_tema():
    data = body_json()
    tema = "dark" if data.get("tema") == "dark" else "light"
    db = database.get_db()
    db.execute("UPDATE users SET theme = ? WHERE id = ?", (tema, g.user["id"]))
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/avatar", methods=["POST"])
@login_required
def api_avatar():
    archivo = request.files.get("avatar")
    if not archivo or archivo.filename == "":
        return jsonify({"ok": False, "message": "No se recibió ningún archivo."}), 400
    if not allowed_file(archivo.filename):
        return jsonify({"ok": False, "message": "Formato no permitido. Usá PNG o JPG."}), 400
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = archivo.filename.rsplit(".", 1)[1].lower()
    nombre = f"user_{g.user['id']}_{uuid.uuid4().hex[:8]}.{ext}"
    archivo.save(os.path.join(UPLOAD_DIR, nombre))
    db = database.get_db()
    db.execute("UPDATE users SET avatar = ? WHERE id = ?", (nombre, g.user["id"]))
    db.commit()
    return jsonify({"ok": True, "avatar": url_for("static", filename=f"uploads/{nombre}")})


@app.route("/api/avatar/remove", methods=["POST"])
@login_required
def api_avatar_remove():
    db = database.get_db()
    db.execute("UPDATE users SET avatar = '' WHERE id = ?", (g.user["id"],))
    db.commit()
    return jsonify({"ok": True})


def iniciar():
    database.init_db()
    database.seed()


iniciar()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)