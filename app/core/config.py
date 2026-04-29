from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # =========================
    # 🌍 ENTORNO
    # =========================
    ENV: str = "development"  # development | production

    # =========================
    # 🔐 SEGURIDAD
    # =========================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día

    # =========================
    # 🗄️ BASE DE DATOS
    # =========================
    DATABASE_URL: str

    # =========================
    # 🌐 FRONTEND / CORS
    # =========================
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = ""

    # =========================
    # 💳 STRIPE
    # =========================
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""  # 👈 IMPORTANTE (tu error venía de aquí)

    # =========================
    # 🤖 IA (opcional)
    # =========================
    OPENAI_API_KEY: str = ""

    # =========================
    # 🔧 HELPERS
    # =========================
    @property
    def cors_list(self) -> List[str]:
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return [self.FRONTEND_URL]

    # =========================
    # ⚙️ CONFIG Pydantic
    # =========================
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 👈 🔥 CLAVE: evita que truene por variables extra


settings = Settings()