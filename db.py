import os
import sqlite3

from flask import g

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT DEFAULT '',
    email TEXT DEFAULT '',
    carrera TEXT DEFAULT '',
    avatar TEXT DEFAULT '',
    theme TEXT DEFAULT 'light',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    codigo TEXT DEFAULT '',
    nombre TEXT NOT NULL,
    profesor TEXT DEFAULT '',
    modalidad TEXT DEFAULT 'presencial',
    horas_semana INTEGER DEFAULT 0,
    aula TEXT DEFAULT '',
    comision TEXT DEFAULT '',
    color TEXT DEFAULT 'indigo',
    regimen TEXT DEFAULT 'promocionable',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS clases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    dia INTEGER NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fin TEXT NOT NULL,
    tipo TEXT DEFAULT 'teorica',
    aula TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    titulo TEXT NOT NULL,
    descripcion TEXT DEFAULT '',
    fecha_limite TEXT DEFAULT '',
    prioridad TEXT DEFAULT 'media',
    tipo_entrega TEXT DEFAULT 'individual',
    estado TEXT DEFAULT 'pendiente',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS examenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    nombre TEXT DEFAULT 'Parcial',
    categoria TEXT DEFAULT 'primeros',
    fecha TEXT NOT NULL,
    hora TEXT DEFAULT '08:00',
    aula TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_materias_user ON materias(user_id);
CREATE INDEX IF NOT EXISTS idx_clases_user ON clases(user_id);
CREATE INDEX IF NOT EXISTS idx_tareas_user ON tareas(user_id);
CREATE INDEX IF NOT EXISTS idx_examenes_user ON examenes(user_id);
"""


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def seed():
    from werkzeug.security import generate_password_hash

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    existing = cur.execute("SELECT id FROM users LIMIT 1").fetchone()
    if existing:
        conn.close()
        return
    now = "2026-09-13"
    cur.execute(
        "INSERT INTO users (username, password_hash, full_name, email, carrera, theme, created_at) VALUES (?,?,?,?,?,?,?)",
        ("sofia", generate_password_hash("demo1234"), "Sofía Martínez", "sofia@correo.com", "Licenciatura en Sistemas (Plan 2023)", "light", now),
    )
    user_id = cur.lastrowid
    materias = [
        ("BDI-301", "Bases de Datos I", "Dra. Marcela Gómez", "hibrida", 6, "Aula 302 • Pabellón 2", "K2012", "indigo", "promocionable"),
        ("SOP-210", "Sistemas Operativos", "Prof. Ing. Marcos Paz", "presencial", 6, "Laboratorio C3", "K3051", "violet", "promocionable"),
        ("AED-204", "Algoritmos y Estructuras de Datos", "Dra. Elena Valenzuela", "presencial", 6, "Aula Magna", "K3021", "emerald", "promocionable"),
        ("FIS-108", "Física II (Electromag.)", "Dra. Marcela Gómez", "presencial", 4, "Aula 105", "K2108", "sky", "promocionable"),
        ("ARS-210", "Arquitectura de Software", "Prof. Roberto Díaz", "presencial", 3, "Aula 204", "K3210", "amber", "promocionable"),
        ("LAB-401", "Laboratorio de Redes", "Prof. Ing. Roberto Rossi", "presencial", 3, "Lab 4", "K3401", "rose", "promocionable"),
    ]
    materia_ids = {}
    for m in materias:
        cur.execute(
            "INSERT INTO materias (user_id, codigo, nombre, profesor, modalidad, horas_semana, aula, comision, color, regimen) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (user_id,) + m,
        )
        materia_ids[m[1]] = cur.lastrowid

    clases = [
        ("Bases de Datos I", 0, "08:00", "11:00", "teorica", "Aula 302 • Pabellón 2"),
        ("Sistemas Operativos", 0, "14:00", "17:00", "practica", "Laboratorio C3"),
        ("Algoritmos y Estructuras de Datos", 1, "10:00", "12:00", "teorica", "Aula Magna"),
        ("Física II (Electromag.)", 2, "09:00", "12:00", "teorica", "Aula 105"),
        ("Bases de Datos I", 2, "14:00", "17:00", "practica", "Laboratorio SQL"),
        ("Arquitectura de Software", 3, "08:30", "11:30", "teorica", "Aula 204"),
        ("Laboratorio de Redes", 3, "16:00", "19:00", "taller", "Lab 4"),
        ("Algoritmos y Estructuras de Datos", 4, "10:00", "13:00", "taller", "Lab. Informática 1"),
    ]
    for c in clases:
        cur.execute(
            "INSERT INTO clases (user_id, materia_id, dia, hora_inicio, hora_fin, tipo, aula) VALUES (?,?,?,?,?,?,?)",
            (user_id, materia_ids[c[0]]) + c[1:],
        )

    tareas = [
        ("Subir Ejercicios Árboles AVL", "Algoritmos y Estructuras de Datos", "2026-09-13T23:59", "alta", "individual", "Práctico 3 • Árboles AVL", "pendiente"),
        ("Lectura: Normalización SQL", "Bases de Datos I", "2026-09-14T18:00", "media", "individual", "Cap. 4 • Normalización SQL", "pendiente"),
        ("TP Shell Scripting en C", "Sistemas Operativos", "2026-09-18T23:59", "alta", "grupal", "TP N° 2 • Shell scripting en C", "pendiente"),
        ("Resumen Electromagnetismo", "Física II (Electromag.)", "2026-09-20T12:00", "baja", "individual", "Cap. 5 y 6", "pendiente"),
        ("Guía Conceptos de Arquitectura", "Arquitectura de Software", "2026-09-08T23:59", "media", "individual", "Guía 1", "completada"),
        ("Configuración de Routers", "Laboratorio de Redes", "2026-09-06T23:59", "media", "grupal", "Lab N° 1: Scripts y Procesos", "completada"),
    ]
    for t in tareas:
        cur.execute(
            "INSERT INTO tareas (user_id, materia_id, titulo, fecha_limite, prioridad, tipo_entrega, descripcion, estado) VALUES (?,?,?,?,?,?,?,?)",
            (user_id, materia_ids[t[1]], t[0], t[2], t[3], t[4], t[5], t[6]),
        )

    examenes = [
        ("Bases de Datos I", "1er Parcial", "primeros", "2026-09-21", "08:30", "Aula Magna 2 (Pabellón Central)"),
        ("Sistemas Operativos", "1er Parcial", "primeros", "2026-09-19", "09:00", "Laboratorio C3"),
        ("Algoritmos y Estructuras de Datos", "1er Parcial", "primeros", "2026-09-28", "14:00", "Laboratorio Turing (Piso 3)"),
        ("Bases de Datos I", "Recuperatorio", "recuperatorios", "2026-10-12", "08:30", "Aula Magna 2 (Pabellón Central)"),
        ("Sistemas Operativos", "Final", "finales", "2026-12-15", "09:00", "Aula 118 • Central"),
    ]
    for e in examenes:
        cur.execute(
            "INSERT INTO examenes (user_id, materia_id, nombre, categoria, fecha, hora, aula) VALUES (?,?,?,?,?,?,?)",
            (user_id, materia_ids[e[0]], e[1], e[2], e[3], e[4], e[5]),
        )

    conn.commit()
    conn.close()