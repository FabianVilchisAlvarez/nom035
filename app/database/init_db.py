from app.database.connection import engine
from app.database.base import Base

# 🔥 IMPORTAR TODOS LOS MODELOS (OBLIGATORIO)
from app.models.usuario import Usuario
from app.models.empresa import Empresa
from app.models.asignacion import Asignacion
from app.models.respuesta import Respuesta
from app.models.pregunta import Pregunta
from app.models.evaluacion import Evaluacion


def init_db():
    Base.metadata.create_all(bind=engine)