from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session


# Supabase connection
DATABASE_URL = (
    "postgresql://postgres:c1e2m3m4e5@db.hgsxcrndzebldtkhhnca.supabase.co:5432/postgres"
)

# Crear motor y sesión
engine = create_engine(
    DATABASE_URL,
    echo=True  # Muestra consultas SQL en consola (opcional)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Función para obtener la sesión en las rutas de FastAPI
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
