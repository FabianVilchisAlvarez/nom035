import random

from app.database.connection import SessionLocal
from app.models.asignacion import Asignacion
from app.models.respuesta import Respuesta
from app.models.pregunta import Pregunta

# =========================
# 🎯 CONFIG
# =========================
EVALUACION_ID = "f73f2cf6-149d-4314-b97f-ddd3b7f658eb"

# =========================
# 🧠 LÓGICA ALTO ESTRÉS
# =========================
def generar_valor(dominio):
    dominio = (dominio or "").lower()

    # 🔴 DOMINIOS CRÍTICOS (pero no exagerados)
    if "carga de trabajo" in dominio:
        return random.choices([2, 3, 4], weights=[30, 50, 20])[0]

    elif "control sobre el trabajo" in dominio:
        return random.choices([2, 3, 4], weights=[40, 40, 20])[0]

    elif "liderazgo" in dominio:
        return random.choices([1, 2, 3, 4], weights=[20, 40, 30, 10])[0]

    elif "violencia" in dominio:
        return random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0]

    # ⚖️ DOMINIOS MEDIOS
    elif "jornada" in dominio:
        return random.choices([1, 2, 3], weights=[30, 50, 20])[0]

    elif "interferencia" in dominio:
        return random.choices([1, 2, 3], weights=[30, 50, 20])[0]

    elif "relaciones" in dominio:
        return random.choices([1, 2, 3], weights=[40, 40, 20])[0]

    # 🟢 DOMINIOS BAJOS
    else:
        return random.choices([0, 1, 2], weights=[50, 35, 15])[0]

# =========================
# 🔌 DB
# =========================
db = SessionLocal()

# 🔥 SOLO asignaciones de esa evaluación
asignaciones = db.query(Asignacion)\
    .filter_by(evaluacion_id=EVALUACION_ID)\
    .all()

preguntas = db.query(Pregunta).all()

print(f"👥 Asignaciones encontradas: {len(asignaciones)}")
print(f"📋 Preguntas cargadas: {len(preguntas)}")

# =========================
# ⚡ GENERAR RESPUESTAS
# =========================
for asignacion in asignaciones:

    for p in preguntas:
        valor = generar_valor(p.dominio)

        respuesta = Respuesta(
            asignacion_id=asignacion.id,
            pregunta_id=p.id,
            valor=valor
        )

        db.add(respuesta)

print("💾 Guardando...")
db.commit()
db.close()

print("✅ Simulación completada")