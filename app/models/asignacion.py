import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Asignacion(Base):
    __tablename__ = "asignaciones"

    # =========================
    # 🆔 ID
    # =========================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # =========================
    # 🔗 RELACIONES
    # =========================
    evaluacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evaluaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    cuestionario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cuestionarios.id", ondelete="CASCADE"),
        nullable=False
    )

    # =========================
    # 🔑 TOKEN ÚNICO
    # =========================
    token = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    # =========================
    # ✅ ESTADO
    # =========================
    completado = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # =========================
    # 📅 TIMESTAMPS (CLAVE NOM-035)
    # =========================
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        nullable=True
    )

    # =========================
    # 📊 OPCIONAL (TRACKING PRO)
    # =========================
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # =========================
    # 🔗 RELACIONES ORM
    # =========================
    evaluacion = relationship(
        "Evaluacion",
        back_populates="asignaciones"
    )

    cuestionario = relationship(
        "Cuestionario"
    )

    respuestas = relationship(
        "Respuesta",
        back_populates="asignacion",
        cascade="all, delete-orphan"
    )

    # =========================
    # ⚡ ÍNDICES (PERFORMANCE)
    # =========================
    __table_args__ = (
        Index("idx_asignacion_eval_token", "evaluacion_id", "token"),
    )