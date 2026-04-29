from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database.connection import SessionLocal
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.core.security import verify_password, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["Auth"])


# =========================
# 🔌 DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 📦 SCHEMAS
# =========================
class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class RegistroSchema(BaseModel):
    empresa: str
    email: EmailStr
    password: str


# =========================
# 🔐 LOGIN
# =========================
@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):

    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not usuario or not verify_password(data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token = create_access_token({
        "user_id": str(usuario.id),
        "empresa_id": str(usuario.empresa_id)
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================
# 🧾 REGISTRO + AUTO LOGIN (PRO)
# =========================
@router.post("/registro")
def registro(data: RegistroSchema, db: Session = Depends(get_db)):

    email = data.email.strip().lower()
    password = data.password
    empresa_nombre = data.empresa.strip()

    # =========================
    # 🔍 VALIDACIONES
    # =========================
    if not email or not password or not empresa_nombre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todos los campos son obligatorios"
        )

    # 🔒 validar usuario existente
    existe = db.query(Usuario).filter(Usuario.email == email).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )

    try:
        # =========================
        # 🏢 CREAR EMPRESA
        # =========================
        empresa = Empresa(nombre=empresa_nombre)

        db.add(empresa)
        db.flush()  # 🔥 importante: obtiene ID sin commit

        # =========================
        # 👤 CREAR USUARIO
        # =========================
        usuario = Usuario(
            email=email,
            password=hash_password(password),
            empresa_id=empresa.id
            # rol="admin"  # si lo usas
        )

        db.add(usuario)

        # =========================
        # 💾 COMMIT FINAL (todo junto)
        # =========================
        db.commit()

        db.refresh(usuario)
        db.refresh(empresa)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar usuario: {str(e)}"
        )

    # =========================
    # 🔐 AUTO LOGIN
    # =========================
    token = create_access_token({
        "user_id": str(usuario.id),
        "empresa_id": str(empresa.id)
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }