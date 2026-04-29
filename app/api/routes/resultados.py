from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.asignacion import Asignacion
from app.models.respuesta import Respuesta
from app.models.pregunta import Pregunta
from app.models.evaluacion import Evaluacion
from app.models.empresa import Empresa

from app.services.calculo_nom035 import calcular_resultados
from app.services.interpretacion_nom035 import interpretar_resultados
from app.services.pdf_nom035 import generar_pdf_resultados

from fastapi.responses import FileResponse

router = APIRouter()


# =========================================================
# 🔹 DB
# =========================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# 🔒 EMPLEADO (PÚBLICO CON TOKEN)
# =========================================================
@router.get("/resultados/{token}")
def obtener_resultados(token: str):
    return {
        "message": "Gracias por completar la evaluación"
    }


# =========================================================
# 📄 PDF (AUDITORÍA)
# =========================================================
@router.get("/resultados/{token}/pdf")
def descargar_pdf(token: str, db: Session = Depends(get_db)):

    # =========================
    # 🔍 ASIGNACIÓN
    # =========================
    asignacion = db.query(Asignacion).filter_by(token=token).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="Token inválido")

    # =========================
    # 📥 RESPUESTAS
    # =========================
    respuestas = db.query(Respuesta).filter_by(
        asignacion_id=asignacion.id
    ).all()

    if not respuestas:
        raise HTTPException(status_code=400, detail="Sin respuestas")

    # =========================
    # 📊 EVALUACIÓN
    # =========================
    evaluacion = db.query(Evaluacion).filter_by(
        id=asignacion.evaluacion_id
    ).first()

    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    # =========================
    # 📊 EMPRESA
    # =========================
    empresa = db.query(Empresa).filter_by(
        id=evaluacion.empresa_id
    ).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # =========================
    # 📊 PREGUNTAS
    # =========================
    preguntas_db = db.query(Pregunta).filter(
        Pregunta.id.in_([r.pregunta_id for r in respuestas])
    ).all()

    preguntas = {p.id: p for p in preguntas_db}

    # =========================
    # 🧠 CÁLCULO NOM-035
    # =========================
    resultados = calcular_resultados(
        respuestas,
        preguntas,
        tipo_escala=evaluacion.tipo_escala
    )

    # =========================
    # 📊 INTERPRETACIÓN
    # =========================
    interpretacion = interpretar_resultados(resultados)
    resultados["interpretacion"] = interpretacion

    # =========================
    # 📄 PDF
    # =========================
    archivo = generar_pdf_resultados(
        resultados,
        empresa=empresa.nombre,
        folio=str(asignacion.id)
    )

    return FileResponse(
        path=archivo,
        filename="reporte_nom035.pdf",
        media_type="application/pdf"
    )