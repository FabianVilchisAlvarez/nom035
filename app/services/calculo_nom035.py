from collections import defaultdict


# =========================
# 🔹 TOTAL DE REACTIVOS OFICIALES
# =========================
TOTAL_REACTIVOS = {
    "III": 72,
    "II": 46
}


# =========================
# 🔹 TABLA GLOBAL STPS
# =========================
RANGO_GLOBAL = {
    "III": [50, 75, 99, 140],
    "II": [45, 65, 85, 120]
}


def clasificar_global(score, tipo):
    rangos = RANGO_GLOBAL.get(tipo)

    if not rangos:
        return "Sin clasificar"

    if score < rangos[0]:
        return "Nulo"
    elif score < rangos[1]:
        return "Bajo"
    elif score < rangos[2]:
        return "Medio"
    elif score < rangos[3]:
        return "Alto"
    else:
        return "Muy alto"


# =========================
# 🔹 CLASIFICACIÓN DOMINIOS (FIX REAL)
# 🔥 PORCENTAJE (NO BRUTO)
# =========================
def clasificar_dominio_porcentaje(porcentaje):
    if porcentaje < 25:
        return "Nulo"
    elif porcentaje < 50:
        return "Bajo"
    elif porcentaje < 75:
        return "Medio"
    elif porcentaje < 90:
        return "Alto"
    else:
        return "Muy alto"


# =========================
# 🔹 NORMALIZACIÓN
# =========================
def normalizar_valor(valor):
    if valor is None:
        return 0
    return max(0, min(valor, 4))


def invertir_valor(valor, tipo_escala):
    valor = normalizar_valor(valor)

    if tipo_escala == "LIKERT":
        return 4 - valor
    elif tipo_escala == "BINARIA":
        return 1 - valor

    return valor


# =========================
# 🔹 MAPEOS
# =========================
MAPEO_II_III = {
    "Ambiente": "Condiciones en el ambiente de trabajo",
    "Ambiente de trabajo": "Condiciones en el ambiente de trabajo",
    "Entorno": "Condiciones en el ambiente de trabajo",

    "Carga": "Carga de trabajo",
    "Carga de trabajo": "Carga de trabajo",

    "Control": "Falta de control sobre el trabajo",
    "Control del trabajo": "Falta de control sobre el trabajo",

    "Jornada": "Jornada de trabajo",
    "Jornada de trabajo": "Jornada de trabajo",

    "Interferencia": "Interferencia trabajo-familia",
    "Interferencia trabajo-familia": "Interferencia trabajo-familia",

    "Relaciones": "Relaciones en el trabajo",

    "Liderazgo": "Liderazgo",

    "Violencia": "Violencia"
}


MAPEO_I = {
    "Recuerdos persistentes": "Acontecimiento traumático",
    "Evitación": "Acontecimiento traumático",
    "Afectación": "Acontecimiento traumático"
}


DOMINIOS_VALIDOS_II_III = set(MAPEO_II_III.values())
DOMINIOS_VALIDOS_I = {"Acontecimiento traumático"}


def obtener_dominio(pregunta, tipo):
    dom = pregunta.dominio

    if tipo == "I":
        return MAPEO_I.get(dom, "Acontecimiento traumático")

    return MAPEO_II_III.get(dom, dom)


# =========================
# 🔥 MOTOR FINAL AUDITORÍA REAL
# =========================
def calcular_resultados(respuestas, preguntas, tipo_cuestionario="III", tipo_escala="LIKERT"):

    total = 0
    dominios = defaultdict(int)
    conteo_dominios = defaultdict(int)

    for r in respuestas:
        pregunta = preguntas.get(r.pregunta_id)

        if not pregunta:
            continue

        valor = normalizar_valor(r.valor)

        if pregunta.es_invertida:
            valor = invertir_valor(valor, tipo_escala)

        total += valor

        dominio = obtener_dominio(pregunta, tipo_cuestionario)

        # FILTRO NOM
        if tipo_cuestionario == "I" and dominio not in DOMINIOS_VALIDOS_I:
            continue

        if tipo_cuestionario in ["II", "III"] and dominio not in DOMINIOS_VALIDOS_II_III:
            continue

        dominios[dominio] += valor
        conteo_dominios[dominio] += 1

    # =========================
    # 🟢 CUESTIONARIO I
    # =========================
    if tipo_cuestionario == "I":
        positivos = sum(1 for r in respuestas if normalizar_valor(r.valor) > 0)

        return {
            "global": {
                "puntaje": positivos,
                "score_bruto": positivos,
                "nivel": "Requiere atención" if positivos > 0 else "Sin riesgo"
            },
            "dominios": {
                "Acontecimiento traumático": {
                    "puntaje": positivos,
                    "score_bruto": positivos,
                    "nivel": "Crítico" if positivos > 0 else "Nulo"
                }
            },
            "categorias": {}
        }

    # =========================
    # 🔥 ESCALADO GLOBAL STPS
    # =========================
    total_esperado = TOTAL_REACTIVOS.get(tipo_cuestionario, len(respuestas) or 1)
    factor_escala = total_esperado / (len(respuestas) or 1)
    score_escalado = total * factor_escala

    porcentaje_global = (score_escalado / (TOTAL_REACTIVOS[tipo_cuestionario] * 4)) * 100
    nivel_global = clasificar_global(score_escalado, tipo_cuestionario)

    # =========================
    # 📊 DOMINIOS (FIX REAL)
    # =========================
    dominios_resultado = {}

    for dom, suma in dominios.items():

        preguntas_dom = conteo_dominios[dom] or 1

        porcentaje_dom = (suma / (preguntas_dom * 4)) * 100

        nivel = clasificar_dominio_porcentaje(porcentaje_dom)

        dominios_resultado[dom] = {
            "puntaje": round(porcentaje_dom, 2),  # UI
            "score_bruto": suma,                  # referencia
            "nivel": nivel
        }

    # ORDEN POR RIESGO REAL
    dominios_resultado = dict(
        sorted(
            dominios_resultado.items(),
            key=lambda x: x[1]["puntaje"],
            reverse=True
        )[:6]
    )

    return {
        "global": {
            "puntaje": round(porcentaje_global, 2),
            "score_bruto": round(score_escalado, 2),
            "nivel": nivel_global
        },
        "categorias": {},
        "dominios": dominios_resultado
    }