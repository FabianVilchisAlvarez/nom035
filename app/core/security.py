from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# 🔐 Contexto de encriptación
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# 🔒 HASH PASSWORD
def hash_password(password: str) -> str:
    # 🔥 bcrypt solo soporta 72 bytes
    password = password.encode("utf-8")[:72].decode("utf-8", "ignore")
    return pwd_context.hash(password)


# 🔑 VERIFY PASSWORD
def verify_password(plain: str, hashed: str) -> bool:
    plain = plain.encode("utf-8")[:72].decode("utf-8", "ignore")
    return pwd_context.verify(plain, hashed)


# 🎟️ JWT TOKEN
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )