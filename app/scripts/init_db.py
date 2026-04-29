from app.database.connection import SessionLocal, engine
from app.database.base import Base

# 🔥 IMPORTAR TODOS LOS MODELOS (IMPORTANTE)
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.cuestionario import Cuestionario
from app.models.pregunta import Pregunta

# 🔥 SEED NOM-035
from app.services.seed_nom035 import seed_nom035


def init_db():
    print("🚀 Iniciando base de datos...")

    # 🔹 Crear todas las tablas
    print("📦 Creando tablas...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 🔹 Cargar cuestionarios NOM-035
        print("📊 Cargando datos NOM-035...")
        seed_nom035(db)

        print("✅ Base de datos lista")

    except Exception as e:
        print("❌ Error al inicializar la BD:", e)

    finally:
        db.close()


if __name__ == "__main__":
    init_db()