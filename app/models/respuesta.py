import uuid
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base


class Respuesta(Base):
    __tablename__ = "respuestas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    asignacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("asignaciones.id"),
        nullable=False
    )

    pregunta_id = Column(
        UUID(as_uuid=True),
        ForeignKey("preguntas.id"),
        nullable=False
    )

    # 🔢 Valor de la respuesta (0–4 normalmente)
    valor = Column(Integer, nullable=False)

    # 🕒 Timestamp (útil para auditoría)
    created_at = Column(DateTime, default=datetime.utcnow)

    # =========================
    # 🔗 RELACIONES
    # =========================
    asignacion = relationship(
        "Asignacion",
        back_populates="respuestas"
    )

    pregunta = relationship(
        "Pregunta",
        back_populates="respuestas"
    )