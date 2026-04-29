import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Orden(Base):
    __tablename__ = "ordenes"

    # =========================
    # 🆔 ID
    # =========================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # =========================
    # 🔗 RELACIONES
    # =========================
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    evaluacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evaluaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # =========================
    # 💳 INFO DEL PLAN
    # =========================
    plan = Column(
        String,
        nullable=False  # micro | mediana | grande | corporativo
    )

    monto = Column(
        Float,
        nullable=False
    )

    moneda = Column(
        String,
        default="MXN",
        nullable=False
    )

    # =========================
    # 🧩 TIPO DE ORDEN
    # =========================
    tipo = Column(
        String,
        default="principal",  # principal | adicional
        nullable=False,
        index=True
    )

    # 👉 cuántos centros adicionales se compraron en esta orden
    cantidad = Column(
        Integer,
        default=1,
        nullable=False
    )

    # =========================
    # 🔥 ESTADO DEL PAGO
    # =========================
    estado = Column(
        String,
        default="pendiente",  # pendiente | pagado | fallido
        nullable=False,
        index=True
    )

    provider = Column(
        String,
        default="stripe",
        nullable=False
    )

    # =========================
    # 🔑 STRIPE
    # =========================
    stripe_session_id = Column(
        String,
        nullable=True,
        index=True
    )

    stripe_payment_intent = Column(
        String,
        nullable=True,
        index=True
    )

    # =========================
    # 📅 TIMESTAMPS
    # =========================
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================
    # 🔗 RELACIONES ORM
    # =========================
    usuario = relationship("Usuario", backref="ordenes")
    evaluacion = relationship("Evaluacion", backref="ordenes")