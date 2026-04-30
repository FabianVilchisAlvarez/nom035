from dotenv import load_dotenv
load_dotenv()

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# 🔥 DB
from app.database.connection import engine
from app.database.base import Base

# 🔥 MODELOS
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.evaluacion import Evaluacion
from app.models.asignacion import Asignacion
from app.models.respuesta import Respuesta
from app.models.cuestionario import Cuestionario
from app.models.pregunta import Pregunta
from app.models.opcion_respuesta import OpcionRespuesta

# 🔥 ROUTES
from app.api.routes import auth
from app.api.routes import evaluaciones
from app.api.routes import cuestionarios
from app.api.routes import respuestas
from app.api.routes import resultados
from app.api.routes import ia
from app.api.routes import reportes
from app.api.routes import pagos


# =========================
# 🚀 APP
# =========================
app = FastAPI(
    title="NOM-035 SaaS PRO",
    version="1.0.0"
)

# =========================
# 🧨 DB (solo dev)
# =========================
if settings.ENV == "development":
    Base.metadata.create_all(bind=engine)

# =========================
# 🌐 CORS (PRODUCCIÓN FIX)
# =========================
origins = [
    "https://nom035-frontend.onrender.com",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# =========================
# 🔥 ROUTES
# =========================
app.include_router(auth.router)
app.include_router(evaluaciones.router)
app.include_router(cuestionarios.router)
app.include_router(respuestas.router)
app.include_router(resultados.router)
app.include_router(ia.router)
app.include_router(reportes.router)
app.include_router(pagos.router, prefix="/pagos", tags=["Pagos"])

# =========================
# ❤️ HEALTH CHECK
# =========================
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# 🏠 ROOT
# =========================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API NOM-035 funcionando 🚀"
    }