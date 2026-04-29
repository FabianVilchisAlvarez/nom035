from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.database.connection import SessionLocal
from app.models.empresa import Empresa
from app.models.evaluacion import Evaluacion
from app.models.asignacion import Asignacion
from app.models.cuestionario import Cuestionario

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/empresas/crear-evaluacion")
def crear_empresa_evaluacion(nombre_empresa: str, empleados: int, db: Session = Depends(get_db)):

    # 🔹 1. Crear empresa
    empresa = Empresa(nombre=nombre_empresa)
    db.add(empresa)
    db.commit()
    db.refresh(empresa)

    # 🔹 2. Obtener cuestionario III
    cuestionario = db.query(Cuestionario).filter_by(tipo="III").first()

    # 🔹 3. Crear evaluación
    evaluacion = Evaluacion(
        empresa_id=empresa.id,
        cuestionario_id=cuestionario.id
    )
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)

    # 🔹 4. Crear tokens (empleados)
    tokens = []

    for _ in range(empleados):
        token = str(uuid.uuid4())[:8]

        asignacion = Asignacion(
        evaluacion_id=evaluacion.id,
        cuestionario_id=cuestionario.id,  # 🔥 FALTABA ESTO
        token=token
        )

        db.add(asignacion)
        tokens.append(token)

    db.commit()

    return {
        "empresa": empresa.nombre,
        "evaluacion_id": str(evaluacion.id),
        "tokens": tokens
    }