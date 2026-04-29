import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nombre = Column(String, nullable=False)

    # 🔥 NUEVO CAMPO (CLAVE)
    plan = Column(
        String,
        nullable=True  # se define cuando paga la primera vez
    )