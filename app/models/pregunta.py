import uuid

from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base

class Pregunta(Base):
    __tablename__ = "preguntas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    cuestionario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cuestionarios.id"),
        nullable=False
    )

    texto = Column(Text, nullable=False)

    # ✅ NOM-035 CONTROLADO
    dominio = Column(String, nullable=True)
    categoria = Column(String, nullable=True)

    es_invertida = Column(Boolean, default=False)

    orden = Column(Integer, default=0)

    # RELACIONES
    cuestionario = relationship(
        "Cuestionario",
        back_populates="preguntas"
    )

    opciones = relationship(
        "OpcionRespuesta",
        back_populates="pregunta",
        cascade="all, delete-orphan"
    )

    # 🔥 ESTE ES EL FIX
    respuestas = relationship(
        "Respuesta",
        back_populates="pregunta",
        cascade="all, delete-orphan"
    )