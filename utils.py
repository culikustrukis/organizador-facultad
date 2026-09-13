import datetime

DIAS = [
    ("Lunes", "Lun"),
    ("Martes", "Mar"),
    ("Miércoles", "Mié"),
    ("Jueves", "Jue"),
    ("Viernes", "Vie"),
    ("Sábado", "Sáb"),
    ("Domingo", "Dom"),
]

TIPOS_CLASE = {
    "teorica": "Teórica",
    "practica": "Práctica",
    "taller": "Taller",
    "laboratorio": "Laboratorio",
    "prob_teorica": "Teórica / Prob.",
}

COLORS = {
    "indigo": {
        "name": "Índigo",
        "bg": "bg-[#EEF2FF]",
        "border": "border-[#C7D2FE]",
        "text": "text-primary",
        "soft": "bg-[#E0E7FF]",
        "dot": "bg-primary",
        "left": "border-l-primary",
        "hex": "#4F46E5",
        "light": "#EEF2FF",
        "border_hex": "#C7D2FE",
    },
    "violet": {
        "name": "Violeta",
        "bg": "bg-[#FAF5FF]",
        "border": "border-[#E9D5FF]",
        "text": "text-[#7E22CE]",
        "soft": "bg-[#F3E8FF]",
        "dot": "bg-[#7E22CE]",
        "left": "border-l-[#7E22CE]",
        "hex": "#7E22CE",
        "light": "#FAF5FF",
        "border_hex": "#E9D5FF",
    },
    "emerald": {
        "name": "Esmeralda",
        "bg": "bg-[#ECFDF5]",
        "border": "border-[#A7F3D0]",
        "text": "text-[#047857]",
        "soft": "bg-[#D1FAE5]",
        "dot": "bg-[#047857]",
        "left": "border-l-[#047857]",
        "hex": "#047857",
        "light": "#ECFDF5",
        "border_hex": "#A7F3D0",
    },
    "sky": {
        "name": "Cielo",
        "bg": "bg-[#F0F9FF]",
        "border": "border-[#BAE6FD]",
        "text": "text-[#0369A1]",
        "soft": "bg-[#E0F2FE]",
        "dot": "bg-[#0369A1]",
        "left": "border-l-[#0369A1]",
        "hex": "#0369A1",
        "light": "#F0F9FF",
        "border_hex": "#BAE6FD",
    },
    "amber": {
        "name": "Ámbar",
        "bg": "bg-[#FFFBEB]",
        "border": "border-[#FDE68A]",
        "text": "text-[#B45309]",
        "soft": "bg-[#FEF3C7]",
        "dot": "bg-[#B45309]",
        "left": "border-l-[#B45309]",
        "hex": "#B45309",
        "light": "#FFFBEB",
        "border_hex": "#FDE68A",
    },
    "rose": {
        "name": "Rosa",
        "bg": "bg-[#FFF1F2]",
        "border": "border-[#FECDD3]",
        "text": "text-[#BE123C]",
        "soft": "bg-[#FFE4E6]",
        "dot": "bg-[#BE123C]",
        "left": "border-l-[#BE123C]",
        "hex": "#BE123C",
        "light": "#FFF1F2",
        "border_hex": "#FECDD3",
    },
}

MODALIDADES = {
    "presencial": "Presencial",
    "hibrida": "Híbrida",
    "virtual": "Virtual",
}

REGIMENES = {
    "promocionable": "Promocionable",
    "promocional": "Promocional",
    "con.final": "Con final",
}

PRIORIDADES = {
    "baja": "Baja",
    "media": "Media",
    "alta": "Alta",
}

CATEGORIAS_EXAMEN = {
    "primeros": "Parcial",
    "recuperatorios": "Recuperatorio",
    "finales": "Final",
}


def to_minutes(hhmm):
    try:
        h, m = (int(x) for x in str(hhmm).split(":"))
        return h * 60 + m
    except (ValueError, AttributeError):
        return 0


def format_hour(hhmm):
    return f"{hhmm} hs"


def to_time(hhmm):
    try:
        return datetime.datetime.strptime(str(hhmm), "%H:%M").time()
    except ValueError:
        return None


def detect_conflicts(clases):
    conflicts = []
    conflicted_ids = set()
    by_day = {}
    for c in clases:
        by_day.setdefault(c["dia"], []).append(c)
    for day, items in by_day.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                a0, a1 = to_minutes(a["hora_inicio"]), to_minutes(a["hora_fin"])
                b0, b1 = to_minutes(b["hora_inicio"]), to_minutes(b["hora_fin"])
                if a0 < b1 and b0 < a1:
                    conflicted_ids.add(a["id"])
                    conflicted_ids.add(b["id"])
                    dia_nombre = DIAS[a["dia"]][0]
                    conflicts.append({
                        "dia": a["dia"],
                        "dia_nombre": dia_nombre,
                        "a_id": a["id"],
                        "b_id": b["id"],
                        "a_nombre": a["materia_nombre"],
                        "b_nombre": b["materia_nombre"],
                        "a_horario": f"{a['hora_inicio']} - {a['hora_fin']}",
                        "b_horario": f"{b['hora_inicio']} - {b['hora_fin']}",
                    })
    return conflicts, conflicted_ids


def semana_actual():
    hoy = datetime.date.today()
    lunes = hoy - datetime.timedelta(days=hoy.weekday())
    return [lunes + datetime.timedelta(days=i) for i in range(7)]


def fecha_humana(fecha):
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    try:
        d = datetime.datetime.strptime(str(fecha)[:10], "%Y-%m-%d")
        return meses[d.month - 1].upper(), d.day
    except ValueError:
        return "---", "--"


def dias_restantes(fecha, hora=""):
    try:
        f = datetime.datetime.strptime(str(fecha)[:10], "%Y-%m-%d")
        hoy = datetime.date.today()
        dias = (f.date() - hoy).days
        return dias
    except ValueError:
        return None


def primeros_nombres(full_name):
    if not full_name:
        return "Estudiante"
    return full_name.split()[0]