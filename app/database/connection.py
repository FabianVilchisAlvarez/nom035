from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 🔥 Tomar la variable de entorno (Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# 🔒 Validación básica (opcional pero útil)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada")

# 🔥 FIX RENDER (PostgreSQL requiere SSL)
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)