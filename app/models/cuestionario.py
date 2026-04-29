import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base import Base


class Cuestionario(Base):
    __tablename__ = "cuestionarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    tipo = Column(String, nullable=False)  
    # Ej: "I", "II", "III"

    preguntas = relationship("Pregunta", back_populates="cuestionario")