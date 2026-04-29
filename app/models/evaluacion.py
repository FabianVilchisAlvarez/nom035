import uuid
from sqlalchemy import Column, ForeignKey, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Integer

centros_adicionales = Column(Integer, default=0)

from app.database.base import Base


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False
    )

    cuestionario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cuestionarios.id", ondelete="CASCADE"),
        nullable=False
    )

    # 🔥 CONTROL DE PLAN / PAGO
    pagado = Column(Boolean, default=False)
    plan = Column(String, nullable=True)

    centros_adicionales = Column(Integer, default=0)

    # 🔥 CLAVE NOM-035
    tipo_escala = Column(String, nullable=False)

    # 🔗 RELACIONES
    asignaciones = relationship(
        "Asignacion",
        back_populates="evaluacion",
        cascade="all, delete-orphan"
    )

    cuestionario = relationship("Cuestionario")
    empresa = relationship("Empresa")