# =====================================================
#  RESPONSABLES
# =====================================================

def obtener_responsable(dominio):
    d = dominio.lower()

    if "liderazgo" in d:
        return "Dirección / Gerencia"

    elif "relaciones" in d:
        return "Recursos Humanos"

    elif "ambiente" in d or "condiciones" in d:
        return "Seguridad e Higiene"

    elif "jornada" in d:
        return "Operaciones"

    elif "control" in d:
        return "Operaciones"

    elif "interferencia" in d or "familia" in d:
        return "Recursos Humanos"

    return "Recursos Humanos"

# =====================================================
# 📊 REPORTE EJECUTIVO NOM-035 (FORMATO CONSULTORÍA PRO)
# =====================================================

def generar_reporte_ejecutivo(empresa, empleados, resultados, interpretacion):

    # =========================
    # 🔥 BASE REAL (NO INTERPRETACIÓN)
    # =========================
    nivel = resultados["global"]["nivel"]
    puntaje = round(resultados["global"].get("puntaje", 0), 2)
    score_bruto = resultados["global"].get("score_bruto", 0)

    dominios_resultados = resultados.get("dominios", {})
    dominios_interpretacion = interpretacion.get("dominios", {})

    # =========================
    # 🔥 DOMINIO CRÍTICO REAL
    # =========================
    if dominios_resultados:
        dominio_critico = max(
            dominios_resultados.items(),
            key=lambda x: x[1].get("puntaje", 0)
        )[0]
    else:
        dominio_critico = "No identificado"

    participacion = "100%"

    # =========================
    # 🧾 RESUMEN EJECUTIVO
    # =========================
    resumen = f"""
Se llevó a cabo la evaluación de factores de riesgo psicosocial conforme a la NOM-035-STPS-2018,
mediante la aplicación del cuestionario tipo {empresa}, cubriendo al {participacion} de la población objetivo ({empleados} colaboradores).

El centro de trabajo presenta un nivel de riesgo {nivel.upper()}, con un puntaje global de {puntaje}% y un score normativo de {round(score_bruto,2)}.

Este resultado indica que la organización
{"se encuentra en una condición que requiere intervención inmediata para mitigar riesgos psicosociales" if nivel in ["Alto","Muy alto"]
else "mantiene condiciones aceptables, pero requiere fortalecimiento preventivo"}.

El análisis identifica como principal área de atención el dominio "{dominio_critico}", el cual impacta directamente en el desempeño organizacional, clima laboral y estabilidad operativa.

De no atenderse oportunamente, estos factores pueden derivar en:
• Disminución de productividad
• Incremento en rotación de personal
• Riesgos de incumplimiento normativo

Se recomienda implementar un plan estructurado de intervención, priorizando acciones organizacionales, liderazgo y condiciones de trabajo.
"""

    # =========================
    # 📊 RESULTADOS GENERALES
    # =========================
    resultados_generales = {
        "nivel": nivel,
        "puntaje": puntaje,
        "score_bruto": score_bruto,
        "dominio_critico": dominio_critico,
        "empleados": empleados
    }

    # =========================
    # 🔎 DOMINIOS (MEZCLA CORRECTA)
    # =========================
    analisis_dominios = []

    for nombre, data in dominios_resultados.items():

        interpretacion_dom = dominios_interpretacion.get(nombre, {})

        analisis_dominios.append({
            "nombre": nombre,
            "nivel": data.get("nivel"),
            "puntaje": data.get("puntaje"),
            "score_bruto": data.get("score_bruto"),
            "accion": interpretacion_dom.get("recomendacion"),  # 🔥 correcto
            "criticidad": interpretacion_dom.get("criticidad")
        })

    # 🔥 ordenar por impacto real
    analisis_dominios = sorted(
        analisis_dominios,
        key=lambda x: x.get("puntaje") or 0,
        reverse=True
    )

    # =========================
    # 🛠️ PLAN DE ACCIÓN
    # =========================
    plan = []

    for d in analisis_dominios:

        prioridad = "Alta" if d["nivel"] in ["Alto", "Muy alto"] else "Media"

        plan.append({
        "dominio": d["nombre"],
        "nivel": d["nivel"],
        "accion": d["accion"],
        "prioridad": prioridad,
        "responsable": obtener_responsable(d["nombre"]),  # ✅ FIX REAL
        "kpi": "Reducción del puntaje en próxima evaluación",
        "evidencia": "Registro documental de acciones implementadas",
        "plazo": (
            "0-30 días" if prioridad == "Alta"
            else "30-90 días"
        )
    })

    # =========================
    # ⚠️ OBLIGACIONES
    # =========================
    obligaciones = [
        "Identificar y evaluar factores de riesgo",
        "Implementar acciones correctivas",
        "Documentar evidencia de cumplimiento",
        "Dar seguimiento continuo"
    ]

    # =========================
    # 🎯 CONCLUSIÓN
    # =========================
    conclusion = f"""
El centro de trabajo se clasifica en un nivel de riesgo {nivel.upper()}.

Se requiere implementar acciones
{"inmediatas y correctivas" if nivel in ["Alto","Muy alto"] else "preventivas"},
priorizando los dominios críticos identificados.

El cumplimiento efectivo de estas acciones permitirá mitigar riesgos organizacionales
y asegurar alineación con la NOM-035-STPS-2018.
"""

    return {
        "resumen": resumen.strip(),
        "resultados_generales": resultados_generales,
        "analisis_dominios": analisis_dominios,
        "plan": plan,
        "obligaciones": obligaciones,
        "conclusion": conclusion.strip()
    }