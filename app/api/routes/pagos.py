from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe

from app.api.deps import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.evaluacion import Evaluacion
from app.models.orden import Orden
from app.models.empresa import Empresa
from app.core.config import settings

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

# =========================
# 💰 PRECIOS BASE
# =========================
PRECIOS = {
    "micro": 6900,
    "mediana": 29900,
    "grande": 49900,
    "corporativo": 79900
}

# =========================
# ➕ PRECIOS ADICIONALES
# =========================
PRECIOS_ADICIONALES = {
    "micro": 3990,
    "mediana": 19900,
    "grande": 29900,
    "corporativo": 49900
}

MAX_ADICIONALES = 3


# =========================
# 🧠 PLAN AUTOMÁTICO
# =========================
def obtener_plan_por_empleados(empleados: int) -> str:
    if empleados <= 15:
        return "micro"
    elif empleados <= 50:
        return "mediana"
    elif empleados <= 250:
        return "grande"
    return "corporativo"


# =========================
# 🔥 STRIPE WEBHOOK (FIX PRO)
# =========================
@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):

    print("🔥 WEBHOOK RECIBIDO")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print("❌ Error validando webhook:", repr(e))
        return {"ok": False}

    try:
        # =========================
        # SOLO EVENTO IMPORTANTE
        # =========================
        if event["type"] != "checkout.session.completed":
            return {"ok": True}

        session_data = event["data"]["object"]

        print("🔎 TIPO SESSION:", type(session_data))

        # 🔥 CONVERTIR A DICT REAL (FIX CLAVE)
        session_dict = session_data.to_dict()

        print("💳 SESSION ID:", session_dict.get("id"))

        metadata = session_dict.get("metadata", {})

        orden_id = metadata.get("orden_id")
        tipo = metadata.get("tipo", "principal")

        payment_intent = session_dict.get("payment_intent")

        print("📦 METADATA:", metadata)

        if not orden_id:
            print("❌ Sin orden_id")
            return {"ok": True}

        # =========================
        # BUSCAR ORDEN
        # =========================
        orden = db.query(Orden)\
            .filter_by(id=orden_id)\
            .with_for_update()\
            .first()

        if not orden:
            print("❌ Orden no encontrada")
            return {"ok": True}

        # =========================
        # EVITAR DUPLICADOS
        # =========================
        if orden.estado == "pagado":
            print("⚠️ Duplicado ignorado")
            return {"ok": True}

        # =========================
        # MARCAR PAGADO
        # =========================
        orden.estado = "pagado"
        orden.stripe_payment_intent = payment_intent

        # =========================
        # DESBLOQUEAR EVALUACIÓN
        # =========================
        evaluacion = db.query(Evaluacion)\
            .filter_by(id=orden.evaluacion_id)\
            .first()

        if evaluacion:
            evaluacion.pagado = True
            print("✅ Evaluación desbloqueada")

            if tipo == "principal":
                evaluacion.plan = orden.plan

                empresa = db.query(Empresa)\
                    .filter_by(id=evaluacion.empresa_id)\
                    .first()

                if empresa and not empresa.plan:
                    empresa.plan = orden.plan
                    print(f"🏢 Plan asignado: {orden.plan}")

        db.commit()

        print("💰 WEBHOOK PROCESADO OK")

    except Exception as e:
        db.rollback()
        print("💥 ERROR WEBHOOK COMPLETO:", repr(e))
        return {"ok": False}

    return {"ok": True}


# =========================
# 💳 CHECKOUT
# =========================
@router.post("/crear-checkout")
def crear_checkout(
    data: dict,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):

    evaluacion_id = data.get("evaluacion_id")

    if not evaluacion_id:
        raise HTTPException(400, "Falta evaluacion_id")

    evaluacion = db.query(Evaluacion).filter_by(
        id=evaluacion_id,
        empresa_id=user.empresa_id
    ).first()

    if not evaluacion:
        raise HTTPException(404, "Evaluación no encontrada")

    if evaluacion.pagado:
        raise HTTPException(400, "Esta evaluación ya está pagada")

    # =========================
    # 🧠 PLAN (🔥 FIX SaaS)
    # =========================
    empresa = db.query(Empresa).filter_by(
        id=user.empresa_id
    ).first()

    if not empresa:
        raise HTTPException(404, "Empresa no encontrada")

    # 🔥 PRIMERA COMPRA → viene del frontend
    if not empresa.plan:

        plan_seleccionado = data.get("plan")

        if not plan_seleccionado:
            raise HTTPException(400, "Debes seleccionar un plan")

        if plan_seleccionado not in PRECIOS:
            raise HTTPException(400, "Plan inválido")

        plan_real = plan_seleccionado

    # 🔒 YA TIENE PLAN → se respeta SIEMPRE
    else:
        plan_real = empresa.plan

    # =========================
    # 🔥 TIPO
    # =========================
    principal_pagada = db.query(Orden).filter(
        Orden.user_id == user.id,
        Orden.tipo == "principal",
        Orden.estado == "pagado"
    ).first()

    tipo = "principal" if not principal_pagada else "adicional"

    # =========================
    # 🔒 LÍMITE ADICIONALES
    # =========================
    if tipo == "adicional":
        adicionales_pagados = db.query(Orden).filter(
            Orden.user_id == user.id,
            Orden.tipo == "adicional",
            Orden.estado == "pagado"
        ).count()

        if adicionales_pagados >= MAX_ADICIONALES:
            raise HTTPException(
                status_code=403,
                detail="Ya alcanzaste el máximo de evaluaciones adicionales"
            )

    # =========================
    # 💰 PRECIO
    # =========================
    if tipo == "principal":
        precio = PRECIOS[plan_real]
        nombre = f"NOM-035 - Plan {plan_real.capitalize()}"
    else:
        precio = PRECIOS_ADICIONALES[plan_real]
        nombre = f"Centro adicional NOM-035 - {plan_real.capitalize()}"

    print(f"💳 Tipo: {tipo} | Plan: {plan_real} | Precio: {precio}")

    # =========================
    # 🧾 ORDEN
    # =========================
    orden = Orden(
        user_id=user.id,
        evaluacion_id=evaluacion_id,
        plan=plan_real,
        monto=precio,
        estado="pendiente",
        tipo=tipo
    )

    db.add(orden)
    db.commit()
    db.refresh(orden)

    # =========================
    # 💳 STRIPE
    # =========================
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "mxn",
                "product_data": {
                    "name": nombre
                },
                "unit_amount": int(precio * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        customer_email=user.email,
        metadata={
            "orden_id": str(orden.id),
            "tipo": tipo
        },
        success_url=f"{settings.FRONTEND_URL}/pago-exitoso",
        cancel_url=f"{settings.FRONTEND_URL}/pago-cancelado",
    )

    orden.stripe_session_id = session.id
    db.commit()

    return {"url": session.url}


# =========================
# 📊 HISTORIAL
# =========================
@router.get("/mis-pagos")
def mis_pagos(
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user)
):

    ordenes = db.query(Orden).filter_by(
        user_id=user.id
    ).order_by(Orden.created_at.desc()).all()

    return [
        {
            "id": str(o.id),
            "plan": o.plan,
            "monto": o.monto,
            "estado": o.estado,
            "tipo": o.tipo
        }
        for o in ordenes
    ]