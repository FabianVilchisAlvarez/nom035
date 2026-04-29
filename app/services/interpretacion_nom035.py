# =====================================================
# 📚 BASE NOM-035 (FORMAL)
# =====================================================

INTERPRETACION_NIVELES = {
    "Nulo": {
        "riesgo": "No se identifican factores de riesgo psicosocial.",
        "accion": "Mantener condiciones actuales y monitoreo periódico."
    },
    "Bajo": {
        "riesgo": "Existen factores de riesgo en nivel bajo que no comprometen de forma significativa al personal.",
        "accion": "Fortalecer medidas preventivas existentes."
    },
    "Medio": {
        "riesgo": "Se identifican factores de riesgo que pueden afectar el bienestar si no se controlan.",
        "accion": "Implementar acciones preventivas específicas."
    },
    "Alto": {
        "riesgo": "Los factores de riesgo identificados afectan de manera relevante el entorno organizacional.",
        "accion": "Aplicar medidas correctivas prioritarias."
    },
    "Muy alto": {
        "riesgo": "Los factores de riesgo representan un impacto significativo en la salud del personal.",
        "accion": "Intervención inmediata conforme a NOM-035-STPS-2018."
    }
}


RECOMENDACIONES_DOMINIO = {
    "Condiciones en el ambiente de trabajo": "Evaluar condiciones físicas, seguridad e higiene, e implementar mejoras estructurales.",
    "Carga de trabajo": "Revisar distribución de tareas, cargas y tiempos operativos.",
    "Falta de control sobre el trabajo": "Incrementar autonomía operativa y claridad en funciones.",
    "Jornada de trabajo": "Ajustar horarios y evitar jornadas prolongadas.",
    "Interferencia trabajo-familia": "Establecer políticas de equilibrio vida-trabajo.",
    "Relaciones en el trabajo": "Fortalecer clima laboral, comunicación y prevención de conflictos.",
    "Liderazgo": "Capacitar mandos medios en liderazgo, comunicación y gestión de personal.",
    "Violencia": "Implementar protocolos formales de prevención, denuncia y atención."
}


# =====================================================
# 🔥 INTERPRETADOR NIVEL AUDITORÍA REAL
# =====================================================

def interpretar_resultados(resultados):

    interpretacion = {
        "global": {},
        "dominios": {},
        "prioridades": [],
        "resumen_ejecutivo": ""
    }

    # =====================================================
    # 🌎 GLOBAL
    # =====================================================
    nivel_global = resultados["global"]["nivel"]
    score = resultados["global"].get("score_bruto", 0)

    base = INTERPRETACION_NIVELES.get(nivel_global, {
        "riesgo": "Nivel no identificado",
        "accion": "Revisar resultados"
    })

    interpretacion["global"] = {
        "nivel": nivel_global,
        "score": score,
        "riesgo": base["riesgo"],
        "accion": base["accion"],
        "dictamen": (
            f"Con base en los resultados obtenidos, el centro de trabajo se clasifica "
            f"en un nivel de riesgo psicosocial '{nivel_global}', conforme a la NOM-035-STPS-2018."
        )
    }

    # =====================================================
    # 🧠 DOMINIOS
    # =====================================================
    dominios_ordenados = sorted(
        resultados.get("dominios", {}).items(),
        key=lambda x: x[1].get("puntaje", 0),
        reverse=True
    )

    for i, (dominio, data) in enumerate(dominios_ordenados):

        nivel = data.get("nivel", "Sin clasificar")
        puntaje = data.get("puntaje", 0)
        score_bruto = data.get("score_bruto", 0)

        base_nivel = INTERPRETACION_NIVELES.get(nivel, {
            "riesgo": "Nivel no identificado",
            "accion": "Revisar"
        })

        recomendacion = RECOMENDACIONES_DOMINIO.get(
            dominio,
            "Realizar análisis específico conforme a NOM-035."
        )

        criticidad = (
            "Crítico" if i == 0 else
            "Alto" if nivel in ["Alto", "Muy alto"] else
            "Medio" if nivel == "Medio" else
            "Bajo"
        )

        interpretacion["dominios"][dominio] = {
            "nivel": nivel,

            # 🔥 CLAVES IMPORTANTES (COMPATIBLES CON FRONT)
            "puntaje": puntaje,
            "score_bruto": score_bruto,
            "porcentaje": puntaje,

            "riesgo": base_nivel["riesgo"],

            "impacto": (
                f"El dominio '{dominio}' presenta un nivel {nivel} con un puntaje de {puntaje}, "
                f"lo que evidencia condiciones que requieren intervención organizacional."
            ),

            # 🔥 ESTA ES LA CLAVE DEL FIX
            "accion": recomendacion,
            "recomendacion": recomendacion,

            "criticidad": criticidad
        }

        # 🎯 PRIORIDADES
        if nivel in ["Muy alto", "Alto"]:
            interpretacion["prioridades"].append({
                "dominio": dominio,
                "nivel": nivel,
                "accion": recomendacion,
                "tipo": "Inmediata"
            })

        elif nivel == "Medio":
            interpretacion["prioridades"].append({
                "dominio": dominio,
                "nivel": nivel,
                "accion": recomendacion,
                "tipo": "Programada"
            })

    # =====================================================
    # 📊 RESUMEN EJECUTIVO
    # =====================================================
    resumen = []

    resumen.append(
        f"El diagnóstico evidencia un nivel de riesgo psicosocial {nivel_global} en el centro de trabajo."
    )

    if dominios_ordenados:
        principal = dominios_ordenados[0][0]
        resumen.append(
            f"El dominio con mayor nivel de exposición es '{principal}', constituyendo el principal foco de intervención."
        )

    if interpretacion["prioridades"]:
        resumen.append(
            "Se identifican áreas críticas que requieren intervención inmediata, así como acciones programadas."
        )

    resumen.append(
        "Se recomienda implementar un plan de acción estructurado conforme a la NOM-035-STPS-2018."
    )

    interpretacion["resumen_ejecutivo"] = " ".join(resumen)

    return interpretacion