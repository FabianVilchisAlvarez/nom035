from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.asignacion import Asignacion
from app.models.evaluacion import Evaluacion
from app.models.cuestionario import Cuestionario
from app.models.pregunta import Pregunta
from app.models.opcion_respuesta import OpcionRespuesta
from app.models.respuesta import Respuesta

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/cuestionario/{token}")
def obtener_cuestionario(token: str, db: Session = Depends(get_db)):

    # 🔹 1. Buscar asignación
    asignacion = db.query(Asignacion).filter_by(token=token).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="Token inválido")

    # 🔹 2. Validar si ya respondió
    respuesta_existente = db.query(Respuesta).filter_by(
        asignacion_id=asignacion.id
    ).first()

    if respuesta_existente:
        return {
            "completado": True,
            "mensaje": "Este cuestionario ya fue respondido"
        }

    # 🔹 3. Obtener evaluación
    evaluacion = db.query(Evaluacion).filter_by(
        id=asignacion.evaluacion_id
    ).first()

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    # 🔹 4. Obtener cuestionario
    cuestionario = db.query(Cuestionario).filter_by(
        id=evaluacion.cuestionario_id
    ).first()

    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")

    # 🔹 5. Obtener preguntas
    preguntas_db = db.query(Pregunta).filter_by(
        cuestionario_id=cuestionario.id
    ).all()

    preguntas = []

    for p in preguntas_db:

        # 🔹 opciones (seguro)
        opciones_db = db.query(OpcionRespuesta).filter_by(
            pregunta_id=p.id
        ).all()

        preguntas.append({
            "id": str(p.id),
            "texto": p.texto,
            "dominio": getattr(p, "dominio", ""),
            "categoria": getattr(p, "categoria", ""),
            "opciones": [
                {
                    "id": str(o.id),
                    "texto": o.texto,
                    "valor": o.valor
                }
                for o in opciones_db
            ]
        })

    # 🔹 6. Respuesta final
    return {
        "completado": False,
        "cuestionario": {
            "id": str(cuestionario.id),
            "nombre": cuestionario.nombre,
            "descripcion": cuestionario.descripcion
        },
        "preguntas": preguntas
    }