from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import SessionLocal
from app.models.usuario import Usuario


security = HTTPBearer()


# =========================
# 🔹 DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 🔐 AUTH
# =========================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("user_id")
        empresa_id = payload.get("empresa_id")

        if not user_id or not empresa_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    user = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    return user


# =========================
# 🏢 EMPRESA (CLAVE PARA SaaS)
# =========================
def get_current_empresa(
    current_user: Usuario = Depends(get_current_user)
):
    return current_user.empresa_id


# =========================
# 👑 SOLO ADMIN (opcional)
# =========================
def require_admin(
    current_user: Usuario = Depends(get_current_user)
):
    if hasattr(current_user, "rol") and current_user.rol != "admin":
        raise HTTPException(
            status_code=403,
            detail="No autorizado"
        )
    return current_user