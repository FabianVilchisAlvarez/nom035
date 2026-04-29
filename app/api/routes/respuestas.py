from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.connection import SessionLocal
from app.models.asignacion import Asignacion
from app.models.respuesta import Respuesta

router = APIRouter()


# =========================
# 🔌 DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 📩 RESPONDER CUESTIONARIO
# =========================
@router.post("/responder/{token}")
def responder(
    token: str,
    data: dict,
    request: Request,
    db: Session = Depends(get_db)
):

    try:
        # =========================
        # 🔍 BUSCAR ASIGNACIÓN
        # =========================
        asignacion = db.query(Asignacion).filter_by(token=token).first()

        if not asignacion:
            raise HTTPException(status_code=404, detail="Token inválido")

        # =========================
        # 🚫 YA RESPONDIDO
        # =========================
        if asignacion.completado:
            raise HTTPException(status_code=400, detail="Este cuestionario ya fue respondido")

        # =========================
        # 📥 VALIDAR INPUT
        # =========================
        respuestas = data.get("respuestas")

        if not isinstance(respuestas, list) or not respuestas:
            raise HTTPException(
                status_code=400,
                detail="Formato de respuestas inválido"
            )

        # =========================
        # 🧹 LIMPIAR Y VALIDAR RESPUESTAS
        # =========================
        respuestas_limpias = []

        for r in respuestas:
            pregunta_id = r.get("pregunta_id")
            valor = r.get("valor")

            if not pregunta_id:
                continue

            try:
                valor = int(valor)
            except:
                continue

            # Validación NOM-035 típica (1 a 5)
            if valor < 0 or valor > 4:
                continue

            respuestas_limpias.append({
                "pregunta_id": pregunta_id,
                "valor": valor
            })

        if not respuestas_limpias:
            raise HTTPException(
                status_code=400,
                detail="No hay respuestas válidas"
            )

        # =========================
        # 🚫 PREVENIR DUPLICADOS
        # =========================
        existentes = db.query(Respuesta).filter_by(
            asignacion_id=asignacion.id
        ).first()

        if existentes:
            raise HTTPException(
                status_code=400,
                detail="Las respuestas ya fueron registradas"
            )

        # =========================
        # 💾 GUARDAR RESPUESTAS
        # =========================
        for r in respuestas_limpias:
            nueva = Respuesta(
                asignacion_id=asignacion.id,
                pregunta_id=r["pregunta_id"],
                valor=r["valor"]
            )
            db.add(nueva)

        # =========================
        # 📅 MARCAR COMPLETADO
        # =========================
        asignacion.completado = True
        asignacion.updated_at = datetime.utcnow()

        # =========================
        # 🌐 METADATA (AUDITORÍA)
        # =========================
        asignacion.ip_address = request.client.host
        asignacion.user_agent = request.headers.get("user-agent")

        # =========================
        # 💾 COMMIT
        # =========================
        db.commit()

        return {
            "mensaje": "Respuestas guardadas correctamente",
            "respuestas_guardadas": len(respuestas_limpias)
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error interno al guardar respuestas"
        )