from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.usuario import Usuario
from app.models.evaluacion import Evaluacion
from app.models.asignacion import Asignacion
from app.models.respuesta import Respuesta

from app.services.ia_service import generar_con_ia

router = APIRouter()


@router.post("/ia/nom035")
def generar_plan(
    data: dict,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):

    empresa = data.get("empresa", "")
    giro = data.get("giro", "")
    centros = data.get("centros", 1)
    empleados = data.get("empleados", 0)
    evaluacion_id = data.get("evaluacion_id")
    politicas = data.get("politicas", "")

    # 🔒 Validación
    if not evaluacion_id:
        raise HTTPException(400, "Debes seleccionar una evaluación")

    evaluacion = db.query(Evaluacion).filter_by(
        id=evaluacion_id,
        empresa_id=user.empresa_id
    ).first()

    if not evaluacion:
        raise HTTPException(404, "Evaluación no encontrada")

    if not evaluacion.pagado:
        raise HTTPException(
    status_code=402,
    detail="Pago requerido para usar IA"
    )

    # 📊 Obtener respuestas
    respuestas = db.query(Respuesta).join(Asignacion).filter(
        Asignacion.evaluacion_id == evaluacion_id
    ).all()

    if not respuestas:
        raise HTTPException(400, "No hay respuestas suficientes")

    valores = [float(r.valor) for r in respuestas if r.valor is not None]

    if not valores:
        raise HTTPException(400, "No hay datos válidos")

    promedio = round(sum(valores) / len(valores), 2)

    nivel = (
        "Nulo" if promedio <= 1 else
        "Bajo" if promedio <= 2 else
        "Medio" if promedio <= 3 else
        "Alto" if promedio <= 4 else
        "Muy alto"
    )

    # 🧹 Políticas
    lista_politicas = [
        p.strip() for p in politicas.split("\n") if p.strip()
    ]

    # 🧠 Prompt PRO
    prompt = f"""
    Actúa como consultor NOM-035.

    Empresa: {empresa}
    Giro: {giro}
    Empleados: {empleados}

    Resultado:
    Nivel: {nivel}
    Promedio: {promedio}

    TAREA:

    1. Interpretación general del nivel de riesgo
    2. Explicación técnica breve

    REGLAS:
    - Máximo 150 palabras
    - No inventar datos
    - No generar planes
    - No generar riesgos específicos
    - No usar ejemplos

    Formato profesional.
    """

    try:
        respuesta = generar_con_ia(prompt)
    except Exception:
        raise HTTPException(500, "Error generando IA")

    return {
        "plan": respuesta,
        "meta": {
            "promedio": promedio,
            "nivel": nivel,
            "respuestas": len(valores)
        }
    }