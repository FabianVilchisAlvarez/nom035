import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class OpcionRespuesta(Base):
    __tablename__ = "opciones_respuesta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    pregunta_id = Column(UUID(as_uuid=True), ForeignKey("preguntas.id"))

    texto = Column(String, nullable=False)
    valor = Column(Integer, nullable=False)

    pregunta = relationship("Pregunta", back_populates="opciones")