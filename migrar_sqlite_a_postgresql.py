"""Migra los datos de la base SQLite (database.db) a PostgreSQL (Supabase).

Conserva los IDs originales, respeta las relaciones (FK) e inserta primero las
tablas padre. No borra database.db y aborta si PostgreSQL ya tiene datos.
"""

import os
import sqlite3

from dotenv import load_dotenv

load_dotenv()

import db

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
TABLAS = [
    ("users", "id"),
    ("materias", "id"),
    ("clases", "id"),
    ("tareas", "id"),
    ("examenes", "id"),
]


def contar_sqlite():
    con = sqlite3.connect(SRC)
    try:
        return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t, _ in TABLAS}
    finally:
        con.close()


def leer_sqlite():
    con = sqlite3.connect(SRC)
    con.row_factory = sqlite3.Row
    try:
        datos = {}
        for t, _ in TABLAS:
            filas = con.execute(f"SELECT * FROM {t} ORDER BY id").fetchall()
            datos[t] = [dict(f) for f in filas]
        return datos
    finally:
        con.close()


def main():
    if not os.path.exists(SRC):
        print(f"ERROR: no existe {SRC}. Nada que migrar.")
        return 1

    sqlite_counts = contar_sqlite()
    print("Registros en SQLite (database.db):")
    for t, c in sqlite_counts.items():
        print(f"  {t}: {c}")

    print("\nCreando tablas en PostgreSQL si no existen...")
    db.init_db()

    conn = db.connect()
    try:
        cur = conn.cursor()

        ocupadas = []
        for t, _ in TABLAS:
            n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()["count"]
            if n > 0:
                ocupadas.append((t, n))
        if ocupadas:
            print("\nABORTO: PostgreSQL ya tiene datos. No se toca nada:")
            for t, n in ocupadas:
                print(f"  {t}: {n} registros")
            print("Si querés empezar de cero, vaciá las tablas en Supabase y volvé a correr este script.")
            return 2

        datos = leer_sqlite()

        for t, col_id in TABLAS:
            filas = datos[t]
            if not filas:
                print(f"\n{t}: tabla vacía en SQLite, se omite.")
                continue
            columnas = list(filas[0].keys())
            marcadores = ", ".join(["%s"] * len(columnas))
            nombre_cols = ", ".join(columnas)
            sql_insert = f"INSERT INTO {t} ({nombre_cols}) VALUES ({marcadores})"
            for f in filas:
                cur.execute(sql_insert, tuple(f.values()))
            print(f"\n{t}: insertadas {len(filas)} filas (IDs {filas[0][col_id]}..{filas[-1][col_id]})")

        for t, col_id in TABLAS:
            cur.execute(f"SELECT MAX({col_id}) AS max_id FROM {t}")
            max_id = cur.fetchone()["max_id"]
            if max_id is not None:
                cur.execute(
                    f"SELECT setval(pg_get_serial_sequence('{t}', '{col_id}'), %s)",
                    (int(max_id),),
                )
                print(f"Secuencia de {t} sincronizada a {max_id}")

        conn.commit()
        print("\nMigración completada. Base SQLite intacta como respaldo.")
    finally:
        db.put_conn(conn)

    print("\nRegistros en PostgreSQL: (verificar con la app o consulta directa)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())